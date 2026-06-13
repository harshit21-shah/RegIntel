#!/usr/bin/env bash
# RegIntel one-time EC2 setup (Amazon Linux 2023 or Ubuntu 22.04+).
# Run as ec2-user (Amazon Linux) or ubuntu (Ubuntu) after SSH:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_USER/RegIntel/main/scripts/aws_ec2_bootstrap.sh | bash
# Or clone the repo and run: bash scripts/aws_ec2_bootstrap.sh

set -euo pipefail

REPO_URL="${REGINTEL_REPO_URL:-}"
INSTALL_DIR="${REGINTEL_INSTALL_DIR:-$HOME/regintel}"

echo "==> Installing Docker..."
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl git
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf update -y
  sudo dnf install -y docker git
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
else
  echo "Unsupported OS. Use Amazon Linux 2023 or Ubuntu 22.04."
  exit 1
fi

echo "==> Cloning RegIntel..."
if [[ -n "$REPO_URL" ]]; then
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "Set REGINTEL_REPO_URL to your GitHub repo, e.g.:"
  echo "  export REGINTEL_REPO_URL=https://github.com/you/RegIntel.git"
  echo "Or clone manually: git clone <repo> $INSTALL_DIR"
  exit 1
fi

cd "$INSTALL_DIR"

if [[ ! -f .env ]]; then
  cp .env.aws.example .env
  PUBLIC_IP=$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4 || true)
  if [[ -n "$PUBLIC_IP" ]]; then
    sed -i "s|YOUR_EC2_PUBLIC_IP|$PUBLIC_IP|g" .env
    echo "==> Set APP_BASE_URL to http://${PUBLIC_IP}:3000 in .env"
  fi
  echo ""
  echo "IMPORTANT: Edit .env and set GROQ_API_KEY and JWT_SECRET_KEY:"
  echo "  nano .env"
  echo ""
fi

echo "==> Building and starting stack (this takes several minutes)..."
docker compose -f docker-compose.aws.yml up -d --build

echo "==> Running database seed + corpus embed..."
docker compose -f docker-compose.aws.yml --profile bootstrap run --rm bootstrap

echo ""
echo "============================================"
echo " RegIntel is running on this server."
echo " Web UI:  http://$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo " API docs: http://$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
echo " Login:   admin@regintel.dev / RegIntel-Demo-2025!"
echo "============================================"
echo ""
echo "Open ports 3000 and 8000 in your EC2 security group if you cannot connect."
