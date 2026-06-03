#!/bin/bash
# Simple dev installer for Ubuntu (IP-based, PostgreSQL)
# Usage: sudo bash install-dev.sh
# Edit SERVER_IP before running, or pass: sudo SERVER_IP=192.168.1.10 bash install-dev.sh

set -e

APP_DIR="/var/www/clinic"
SERVER_IP="${SERVER_IP:-192.168.1.10}"
DB_PASS="${DB_PASS:-devpassword123}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash install-dev.sh"
  exit 1
fi

if [ ! -f "$APP_DIR/manage.py" ]; then
  echo "Project not found at $APP_DIR"
  echo "Copy project first, e.g.: sudo mv /tmp/clinic $APP_DIR"
  exit 1
fi

echo "==> Installing packages..."
apt update
apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib libpq-dev nginx

echo "==> PostgreSQL user & database..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='clinic_user'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER clinic_user WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='clinic_db'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE clinic_db OWNER clinic_user;"

echo "==> Python venv..."
cd "$APP_DIR"
mkdir -p run staticfiles
chown -R www-data:www-data "$APP_DIR"
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  echo "==> Creating .env ..."
  cp .env.dev.example .env
  sed -i "s/192.168.1.10/$SERVER_IP/g" .env
  sed -i "s/change_me/$DB_PASS/g" .env
  chown www-data:www-data .env
  chmod 600 .env
fi

echo "==> Django migrate & static..."
sudo -u www-data .venv/bin/python manage.py migrate --noinput
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput

echo "==> systemd + nginx..."
cp deploy/gunicorn-dev.service /etc/systemd/system/clinic.service
cp deploy/nginx-clinic-dev.conf /etc/nginx/sites-available/clinic
sed -i "s/192.168.1.10/$SERVER_IP/g" /etc/nginx/sites-available/clinic
ln -sf /etc/nginx/sites-available/clinic /etc/nginx/sites-enabled/clinic
rm -f /etc/nginx/sites-enabled/default
systemctl daemon-reload
systemctl enable clinic
systemctl restart clinic
nginx -t && systemctl reload nginx

echo ""
echo "Done. Open: http://$SERVER_IP/"
echo "Create admin: cd $APP_DIR && sudo -u www-data .venv/bin/python manage.py createsuperuser"
echo "Windows hosts (optional): $SERVER_IP    clinic.local"
