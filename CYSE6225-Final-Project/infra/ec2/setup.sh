#!/usr/bin/env bash
# Bootstrap script for a fresh EC2 instance (Ubuntu 22.04/24.04).
# Run as: sudo bash setup.sh
#   (from /opt/webvideofinder/CYSE6225-Final-Project/infra/ec2)
#
# What it does:
#  1. Installs Python3, pip, venv, Nginx
#  2. Creates a backend venv and installs dependencies from the repo root requirements.txt
#  3. Installs the systemd service
#  4. Installs the Nginx reverse-proxy config
#
# Assumes the repo has already been cloned to /opt/webvideofinder
# (adjust APP_DIR below if you cloned it elsewhere).

set -euo pipefail

APP_DIR="/opt/webvideofinder"
PROJECT_DIR="$APP_DIR/CYSE6225-Final-Project"
REPO_BACKEND="$PROJECT_DIR/backend"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
EC2_INFRA_DIR="$PROJECT_DIR/infra/ec2"

echo "==> Installing system packages"
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx git

echo "==> Creating virtualenv"
python3 -m venv "$REPO_BACKEND/venv"
"$REPO_BACKEND/venv/bin/pip" install --upgrade pip
"$REPO_BACKEND/venv/bin/pip" install -r "$REQUIREMENTS_FILE"

echo "==> Don't forget to create $REPO_BACKEND/.env (copy from $REPO_BACKEND/.env.example and fill in real values)"

echo "==> Installing systemd service"
cp "$EC2_INFRA_DIR/webvideofinder.service" /etc/systemd/system/webvideofinder.service
systemctl daemon-reload
systemctl enable webvideofinder

echo "==> Installing Nginx config"
cp "$EC2_INFRA_DIR/nginx.conf" /etc/nginx/sites-available/webvideofinder
ln -sf /etc/nginx/sites-available/webvideofinder /etc/nginx/sites-enabled/webvideofinder
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo "==> Starting services"
systemctl restart webvideofinder
systemctl restart nginx

echo "==> Done. Check status with: systemctl status webvideofinder"
