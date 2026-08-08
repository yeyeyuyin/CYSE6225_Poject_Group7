#!/usr/bin/env bash
# Builds the custom "golden" AMI that the ASG launches instances from (see
# infra/cfn/app.yaml's AmiId parameter). Plain AWS CLI, no Packer: launches
# a temporary instance, provisions it via SSM Run Command (build-provision.sh
# in this directory), snapshots it into an AMI, then cleans up.
#
# Usage:
#   ./build-ami.sh <git-repo-url> <git-branch> <subnet-id> <security-group-id> [region]
#
# subnet-id/security-group-id: anything that gives the temp instance
# outbound internet access -- e.g. the Network stack's PublicSubnet1Id +
# AppSecurityGroupId (SSH not required; SSM does not need port 22 open).
#
# Re-run this after every code change you want reflected in the ASG; the
# App stack's AmiId parameter then needs updating to the new AMI ID and
# re-deploying (which triggers an Instance Refresh).
set -euo pipefail

GIT_REPO_URL="${1:?Usage: build-ami.sh <git-repo-url> <git-branch> <subnet-id> <security-group-id> [region]}"
GIT_BRANCH="${2:?git branch required}"
SUBNET_ID="${3:?subnet id required}"
SECURITY_GROUP_ID="${4:?security group id required}"
REGION="${5:-us-east-1}"

ROLE_NAME="webvideofinder-ami-builder"
PROFILE_NAME="webvideofinder-ami-builder"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Ensuring the builder IAM role/instance profile exists"
if ! aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
    >/dev/null
  aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
fi
if ! aws iam get-instance-profile --instance-profile-name "$PROFILE_NAME" >/dev/null 2>&1; then
  aws iam create-instance-profile --instance-profile-name "$PROFILE_NAME" >/dev/null
  aws iam add-role-to-instance-profile --instance-profile-name "$PROFILE_NAME" --role-name "$ROLE_NAME"
  echo "    (new instance profile -- waiting ~10s for IAM to propagate)"
  sleep 10
fi

echo "==> Looking up latest Ubuntu 22.04 AMI"
BASE_AMI=$(aws ssm get-parameter \
  --name /aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id \
  --region "$REGION" --query "Parameter.Value" --output text)
echo "    base AMI: $BASE_AMI"

echo "==> Launching temporary builder instance"
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "$BASE_AMI" \
  --instance-type t3.micro \
  --subnet-id "$SUBNET_ID" \
  --security-group-ids "$SECURITY_GROUP_ID" \
  --iam-instance-profile "Name=$PROFILE_NAME" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=webvideofinder-ami-builder}]' \
  --region "$REGION" \
  --query "Instances[0].InstanceId" --output text)
echo "    instance: $INSTANCE_ID"

cleanup() {
  echo "==> Terminating builder instance"
  aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --region "$REGION" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "==> Waiting for instance to be running"
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

echo "==> Waiting for the SSM agent to check in (can take ~30-90s after boot)"
for _ in $(seq 1 24); do
  STATUS=$(aws ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=$INSTANCE_ID" \
    --region "$REGION" --query "InstanceInformationList[0].PingStatus" --output text 2>/dev/null || echo "None")
  [ "$STATUS" == "Online" ] && break
  sleep 5
done
if [ "$STATUS" != "Online" ]; then
  echo "SSM agent never came online -- check the instance/subnet routing." >&2
  exit 1
fi

echo "==> Cloning the repo and running build-provision.sh via SSM"
CLONE_AND_PROVISION="apt-get update -y && apt-get install -y git && rm -rf /opt/webvideofinder && git clone --branch $GIT_BRANCH --depth 1 $GIT_REPO_URL /opt/webvideofinder && bash /opt/webvideofinder/CYSE6225-Final-Project/infra/ec2/build-provision.sh"
COMMAND_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"$CLONE_AND_PROVISION\"]" \
  --region "$REGION" \
  --query "Command.CommandId" --output text)

echo "==> Waiting for provisioning to finish (command: $COMMAND_ID)"
aws ssm wait command-executed --command-id "$COMMAND_ID" --instance-id "$INSTANCE_ID" --region "$REGION" || {
  echo "Provisioning failed. Output:" >&2
  aws ssm get-command-invocation --command-id "$COMMAND_ID" --instance-id "$INSTANCE_ID" --region "$REGION" \
    --query "{Status:Status,StdOut:StandardOutputContent,StdErr:StandardErrorContent}" >&2
  exit 1
}

echo "==> Creating AMI"
AMI_NAME="webvideofinder-$(date -u +%Y%m%d%H%M%S)"
AMI_ID=$(aws ec2 create-image \
  --instance-id "$INSTANCE_ID" \
  --name "$AMI_NAME" \
  --region "$REGION" \
  --query "ImageId" --output text)
echo "    ami: $AMI_ID"

echo "==> Waiting for AMI to become available (a few minutes)"
aws ec2 wait image-available --image-ids "$AMI_ID" --region "$REGION"

echo ""
echo "==> Done. AMI ID: $AMI_ID"
echo "Pass this as the AmiId parameter when deploying infra/cfn/app.yaml."
