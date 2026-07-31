#!/usr/bin/env bash
# Golden-image provisioning: runs ONCE, on a temporary builder instance,
# while creating the custom AMI (see infra/ec2/build-ami.sh). Everything
# here gets baked into the image -- OS packages, app code, the venv, the
# systemd unit, the nginx config -- so that when the ASG launches a real
# instance from that AMI, it comes up in seconds instead of re-installing
# everything from GitHub/apt/pip at every boot.
#
# Deliberately does NOT write .env or start the app: those depend on which
# environment (dev/demo) the AMI ends up running in, so baking them in
# would make the image env-specific (and would bake the JWT secret into
# an AMI snapshot). That part happens at real boot time -- see boot.sh,
# which is what actually runs as the Launch Template's UserData.
set -euo pipefail

APP_DIR="/opt/webvideofinder"
PROJECT_DIR="$APP_DIR/CYSE6225-Final-Project"
REPO_BACKEND="$PROJECT_DIR/backend"
EC2_INFRA_DIR="$PROJECT_DIR/infra/ec2"

echo "==> Installing system packages"
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx

echo "==> Creating virtualenv"
python3 -m venv "$REPO_BACKEND/venv"
"$REPO_BACKEND/venv/bin/pip" install --upgrade pip
"$REPO_BACKEND/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "==> Installing systemd service (enabled, not started -- no .env yet)"
cp "$EC2_INFRA_DIR/webvideofinder.service" /etc/systemd/system/webvideofinder.service
systemctl daemon-reload
systemctl enable webvideofinder

echo "==> Installing Nginx config (enabled, not started)"
cp "$EC2_INFRA_DIR/nginx.conf" /etc/nginx/sites-available/webvideofinder
ln -sf /etc/nginx/sites-available/webvideofinder /etc/nginx/sites-enabled/webvideofinder
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx

echo "==> Provisioning complete -- ready to snapshot into an AMI"
