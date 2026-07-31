#!/usr/bin/env bash
# Runs at real instance boot, from the golden AMI (see build-provision.sh
# for what's already baked in). This is short on purpose: packages, code,
# venv, systemd unit, and nginx config already exist on disk, so all that's
# left is writing the environment-specific config and (re)starting the two
# services that are already installed and enabled.
#
# This is the Launch Template's actual UserData (see infra/cfn/app.yaml) --
# CloudFormation substitutes the placeholders below via Fn::Sub before
# handing this to the instance.
#
# DynamoDB tables are NOT created here -- run
# infra/dynamodb/create_tables.py once before the app is expected to
# actually work. Instances still boot and pass the ALB health check
# without it (the health check doesn't touch the database).
set -euo pipefail

REPO_BACKEND="/opt/webvideofinder/CYSE6225-Final-Project/backend"

echo "==> Writing .env"
cat > "$REPO_BACKEND/.env" <<EOF
AWS_REGION=$AWS_REGION
TABLE_PREFIX=$TABLE_PREFIX
JWT_SECRET=$JWT_SECRET
JWT_EXPIRES_HOURS=24
CORS_ORIGINS=*
PORT=5001
AVATAR_BUCKET=$AVATAR_BUCKET
AVATAR_CDN_BASE_URL=$AVATAR_CDN_BASE_URL
EOF
chmod 600 "$REPO_BACKEND/.env"

echo "==> Starting services"
systemctl restart webvideofinder
systemctl restart nginx

echo "==> Boot complete"
