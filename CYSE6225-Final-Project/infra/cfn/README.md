# CloudFormation Deployment

Four steps in order (Network → Data → build the AMI → App; the App stack
imports Network's and Data's outputs by `EnvironmentName`, so the name
must match across all of them):

```bash
export ENV=dev   # dev / demo -- must match across every step below

# 1. Network: VPC, 2 public + 2 private subnets (2 AZs), IGW, NAT Gateway,
#    route tables, DynamoDB/S3 VPC endpoints, security groups
aws cloudformation deploy \
  --stack-name $ENV-network \
  --template-file network.yaml \
  --parameter-overrides EnvironmentName=$ENV SSHLocationCidr=<your-ip>/32 \
  --region us-east-1

# 2. Data: S3 bucket + CloudFront distribution for avatars
aws cloudformation deploy \
  --stack-name $ENV-data \
  --template-file data.yaml \
  --parameter-overrides EnvironmentName=$ENV \
  --region us-east-1

# 3. Build the golden AMI (app code/venv/systemd/nginx baked in -- see
#    ../ec2/build-ami.sh). Needs a subnet + security group with outbound
#    internet access; the Network stack's public subnet + app SG works.
PUBLIC_SUBNET=$(aws cloudformation describe-stacks --stack-name $ENV-network \
  --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet1Id'].OutputValue" --output text)
APP_SG=$(aws cloudformation describe-stacks --stack-name $ENV-network \
  --query "Stacks[0].Outputs[?OutputKey=='AppSecurityGroupId'].OutputValue" --output text)
../ec2/build-ami.sh https://github.com/<org>/<repo>.git main "$PUBLIC_SUBNET" "$APP_SG"
# ^ prints the new AMI ID at the end -- use it below.

# 4. App: IAM role, Launch Template (from that AMI), ALB, Target Group, ASG
aws cloudformation deploy \
  --stack-name $ENV-app \
  --template-file app.yaml \
  --parameter-overrides \
      EnvironmentName=$ENV \
      AmiId=<ami-id-from-step-3> \
      JWTSecret=<a-real-random-secret> \
      TablePrefix=${ENV}_ \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

Changed the app code? Re-run step 3 to get a new AMI, then re-run step 4
with the new `AmiId` -- that updates the Launch Template's default version
and triggers an Instance Refresh (rolling replacement) on the ASG.

After the App stack finishes, run `infra/dynamodb/create_tables.py` once
(with `--prefix ${ENV}_`) against the real AWS account -- table creation
isn't part of the app stack, and the app will 500 on anything that touches
the database until the tables exist (the ALB health check itself doesn't
touch the database, so instances will still come up healthy without this
step).

Then check `aws cloudformation describe-stacks --stack-name $ENV-app
--query "Stacks[0].Outputs"` for the ALB's DNS name and open it in a
browser.

## Tearing down between test sessions

Unlike the App stack, **the Network stack is no longer free to leave
running** -- it now owns the NAT Gateway, which bills by the hour
regardless of traffic (~$32/month if left up all month). Two options:

- **Cheaper, more to redo**: delete both Network and App stacks between
  sessions (`app` first, then `network` -- reverse deploy order, since App
  imports Network's outputs). Data stack (S3/CloudFront/DynamoDB) stays up,
  it's the one that's actually near-free idle.
- **Faster to redo, costs a bit more**: only delete the App stack, leave
  Network (and its NAT Gateway) running. Pick this if you're testing
  across the same day/week and don't want to wait for a fresh NAT Gateway
  (~1 minute) and VPC endpoints every time.

```bash
aws cloudformation delete-stack --stack-name $ENV-app --region us-east-1
# and, if also tearing down Network:
aws cloudformation delete-stack --stack-name $ENV-network --region us-east-1
```

Re-deploying brings everything back against the same avatar bucket/table
data (Network and App stacks are stateless; only Data holds anything you'd
lose).

## What's deliberately not here

- **Custom AMI, but no Packer.** `infra/ec2/build-ami.sh` is a plain
  AWS-CLI script that launches a temp instance, provisions it via SSM Run
  Command (`build-provision.sh`), snapshots it, and cleans up -- same end
  result as Packer (an image with the app already baked in, so ASG
  instances boot in seconds instead of re-installing everything from
  GitHub/apt/pip at every launch), without needing to learn Packer's HCL
  syntax for a 4-person team.
- **No Docker/ECS.** The AMI is a plain VM image, not a container.
- **No HTTPS/ACM/Route53** in the base setup -- that's the assignment's
  bonus item, layered on top once the HTTP version works (a custom domain
  needs to be registered first, then Route53 + an ACM cert + an HTTPS
  listener on the ALB).
- **Single NAT Gateway, not one per AZ.** Halves the NAT cost but means
  both private subnets share a single point of failure for outbound
  internet access. DynamoDB and S3 traffic bypass the NAT entirely via
  Gateway VPC Endpoints, so this only matters for `apt`/`pip`/`git` access
  during boot.
- **SSH into app instances won't work as-is.** They're in a private
  subnet with no inbound route from the internet. Use SSM Session Manager
  (`aws ssm start-session --target <instance-id>`) instead -- the
  instance role already has `AmazonSSMManagedInstanceCore` attached.
