# Ubuntu Developer Deploy — Full Step-by-Step Guide

**Patient Management System** on Ubuntu with **PostgreSQL**, accessed by **IP address** or a **local hosts name** (e.g. `clinic.local`).

- No live domain  
- No HTTPS / SSL  
- Developer-friendly (LAN / office / home network)  

Same idea as Windows: edit the **hosts** file → open a friendly name instead of remembering the IP.

---

## Table of contents

1. [What you will build](#1-what-you-will-build)
2. [Before you start](#2-before-you-start)
3. [Step 1 — Connect to Ubuntu server](#step-1--connect-to-ubuntu-server)
4. [Step 2 — Update Ubuntu and install packages](#step-2--update-ubuntu-and-install-packages)
5. [Step 3 — Find your server IP](#step-3--find-your-server-ip)
6. [Step 4 — Create PostgreSQL database](#step-4--create-postgresql-database)
7. [Step 5 — Copy project from Windows to Ubuntu](#step-5--copy-project-from-windows-to-ubuntu)
8. [Step 6 — Set folder permissions](#step-6--set-folder-permissions)
9. [Step 7 — Create Python virtual environment](#step-7--create-python-virtual-environment)
10. [Step 8 — Create `.env` configuration file](#step-8--create-env-configuration-file)
11. [Step 9 — Django database and admin user](#step-9--django-database-and-admin-user)
12. [Step 10 — Start Gunicorn (systemd service)](#step-10--start-gunicorn-systemd-service)
13. [Step 11 — Configure Nginx (web server)](#step-11--configure-nginx-web-server)
14. [Step 12 — Open the app in your browser](#step-12--open-the-app-in-your-browser)
15. [Step 13 — Windows hosts file (optional friendly name)](#step-13--windows-hosts-file-optional-friendly-name)
16. [Step 14 — Optional: auto-install script](#step-14--optional-auto-install-script)
17. [Daily use and updates](#daily-use-and-updates)
18. [Full checklist](#full-checklist)
19. [Troubleshooting](#troubleshooting)
20. [Project files reference](#project-files-reference)

---

## 1. What you will build

```
[ Windows / Phone browser ]
        |
        |  http://192.168.1.10/   or   http://clinic.local/
        v
[ Ubuntu Server ]
   Nginx (port 80)
        |
   Gunicorn (Unix socket)
        |
   Django app  ----->  PostgreSQL (clinic_db)
```

| Part | Software | Role |
|------|----------|------|
| Database | PostgreSQL | Stores patients, users, invoices |
| App | Django + Gunicorn | Your clinic application |
| Web | Nginx | Sends browser requests to Gunicorn |
| Config | `.env` file | Passwords, IP, debug mode |
| Code path | `/var/www/clinic` | Project folder on server |

---

## 2. Before you start

### You need

| Item | Example |
|------|---------|
| Ubuntu server | Ubuntu 22.04 or 24.04 (VM, VPS, or physical PC) |
| SSH access | User `ubuntu` with `sudo` |
| Server on network | Same Wi‑Fi/LAN as your Windows PC (for testing) |
| Windows PC | Project folder + PowerShell for `scp` |
| Server IP | e.g. `192.168.1.10` (you will find this in Step 3) |

### Replace in this guide

Everywhere you see **`192.168.1.10`**, use **your real server IP**.

### Project path on server (fixed in this guide)

```
/var/www/clinic
```

---

## Step 1 — Connect to Ubuntu server

On **Windows**, open PowerShell:

```powershell
ssh ubuntu@192.168.1.10
```

- First time: type `yes` to accept fingerprint.  
- Enter your Ubuntu user password.

You are now on the server terminal. All following commands (unless noted) run **on Ubuntu**.

---

## Step 2 — Update Ubuntu and install packages

Copy and run line by line:

```bash
sudo apt update
```

```bash
sudo apt upgrade -y
```

```bash
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  postgresql \
  postgresql-contrib \
  libpq-dev \
  nginx \
  git \
  curl
```

**Check installs:**

```bash
python3 --version
psql --version
nginx -v
```

Expected: Python 3.10+, PostgreSQL, Nginx — no errors.

---

## Step 3 — Find your server IP

```bash
hostname -I
```

Example output:

```
192.168.1.10
```

**Write down this IP.** Use it in `.env`, Nginx, browser, and Windows hosts file.

Test from **Windows** (optional):

```powershell
ping 192.168.1.10
```

---

## Step 4 — Create PostgreSQL database

### 4.1 Open PostgreSQL shell

```bash
sudo -u postgres psql
```

### 4.2 Run SQL (change password if you want)

```sql
CREATE USER clinic_user WITH PASSWORD 'devpassword123';
CREATE DATABASE clinic_db OWNER clinic_user;
GRANT ALL PRIVILEGES ON DATABASE clinic_db TO clinic_user;
\q
```

### 4.3 Test connection

```bash
psql -h localhost -U clinic_user -d clinic_db -c "SELECT 1;"
```

- Password: `devpassword123` (or what you set)  
- Expected: a table with `1`

If this fails, fix PostgreSQL before continuing.

### 4.4 PostgreSQL settings (where they live)

| Setting | Value | Used in |
|---------|-------|---------|
| Database name | `clinic_db` | `.env` → `DB_NAME` |
| User | `clinic_user` | `.env` → `DB_USER` |
| Password | `devpassword123` | `.env` → `DB_PASSWORD` |
| Host | `localhost` | `.env` → `DB_HOST` |
| Port | `5432` | `.env` → `DB_PORT` |

Django reads these from **`.env`** via **`config/settings.py`**.

---

## Step 5 — Copy project from Windows to Ubuntu

### 5.1 On Windows — copy files to server

Open **new PowerShell window** (stay connected with SSH in the other window):

```powershell
scp -r "C:\shiab\Simple Patient Management System" ubuntu@192.168.1.10:/tmp/clinic
```

Wait until upload finishes (may take a few minutes).

**Do not copy** `.venv` from Windows — Ubuntu will create its own.

### 5.2 On Ubuntu — move to `/var/www/clinic`

Back in **SSH**:

```bash
sudo mkdir -p /var/www
sudo mv /tmp/clinic "/var/www/clinic"
```

### 5.3 Verify project files

```bash
ls /var/www/clinic/manage.py
ls /var/www/clinic/config/settings.py
ls /var/www/clinic/requirements.txt
```

All three should exist.

---

## Step 6 — Set folder permissions

```bash
sudo mkdir -p /var/www/clinic/run
sudo mkdir -p /var/www/clinic/staticfiles
sudo chown -R www-data:www-data /var/www/clinic
sudo chown www-data:www-data /var/www/clinic/run
```

| Folder | Purpose |
|--------|---------|
| `/var/www/clinic` | Full project |
| `/var/www/clinic/run` | Gunicorn socket file |
| `/var/www/clinic/staticfiles` | CSS/JS after `collectstatic` |
| `/var/www/clinic/.venv` | Python packages (created next step) |

---

## Step 7 — Create Python virtual environment

```bash
cd /var/www/clinic
```

```bash
sudo -u www-data python3 -m venv .venv
```

```bash
sudo -u www-data .venv/bin/pip install --upgrade pip
```

```bash
sudo -u www-data .venv/bin/pip install -r requirements.txt
```

**Verify Django:**

```bash
sudo -u www-data .venv/bin/python -c "import django; print(django.get_version())"
```

Expected: version number (e.g. `6.0.5`), no error.

**Important:** On the server, always use:

```bash
/var/www/clinic/.venv/bin/python
```

—not system `python3` alone—for `manage.py` commands.

---

## Step 8 — Create `.env` configuration file

### 8.1 Copy template

```bash
cd /var/www/clinic
sudo cp .env.dev.example .env
sudo nano .env
```

### 8.2 Full `.env` example (edit IP and password)

```env
USE_SQLITE=0

DB_NAME=clinic_db
DB_USER=clinic_user
DB_PASSWORD=devpassword123
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=dev-secret-key-change-if-you-want
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.10,clinic.local
CSRF_TRUSTED_ORIGINS=http://192.168.1.10,http://clinic.local,http://localhost,http://127.0.0.1
```

### 8.3 What each line means

| Variable | Value | Meaning |
|----------|-------|---------|
| `USE_SQLITE` | `0` | Use PostgreSQL (not SQLite file) |
| `DB_NAME` | `clinic_db` | PostgreSQL database name |
| `DB_USER` | `clinic_user` | PostgreSQL username |
| `DB_PASSWORD` | your password | Must match Step 4 |
| `DB_HOST` | `localhost` | DB on same server |
| `DB_PORT` | `5432` | Default PostgreSQL port |
| `SECRET_KEY` | any long string | Django security key |
| `DEBUG` | `True` | Developer mode (shows errors) |
| `ALLOWED_HOSTS` | IP + names | Django accepts these hosts |
| `CSRF_TRUSTED_ORIGINS` | `http://...` | Required for login forms over HTTP |

Replace **`192.168.1.10`** with your IP from Step 3.

Save in nano: **Ctrl+O**, Enter, **Ctrl+X**.

### 8.4 Secure the file

```bash
sudo chown www-data:www-data /var/www/clinic/.env
sudo chmod 600 /var/www/clinic/.env
```

### 8.5 Where settings are in code

| File | Role |
|------|------|
| `/var/www/clinic/.env` | Your secrets and IP (edit this) |
| `/var/www/clinic/config/settings.py` | Reads `.env`, configures Django + database |

---

## Step 9 — Django database and admin user

All commands from `/var/www/clinic`:

```bash
cd /var/www/clinic
```

### 9.1 Check Django config

```bash
sudo -u www-data .venv/bin/python manage.py check
```

Expected: `System check identified no issues`.

### 9.2 Create tables in PostgreSQL

```bash
sudo -u www-data .venv/bin/python manage.py migrate
```

Expected: `Applying migrations...` then OK.

### 9.3 Collect static files (CSS)

```bash
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
```

Expected: files copied to `staticfiles/`.

### 9.4 Create admin login

```bash
sudo -u www-data .venv/bin/python manage.py createsuperuser
```

Enter:

- Username (e.g. `admin`)  
- Email (optional)  
- Password (twice)

Remember this — you use it to log in.

---

## Step 10 — Start Gunicorn (systemd service)

Gunicorn runs Django. systemd keeps it running after reboot.

### 10.1 Edit Nginx template IP (optional)

```bash
sudo nano /var/www/clinic/deploy/nginx-clinic-dev.conf
```

Change `192.168.1.10` to your IP in `server_name` line, or leave `_` to accept any host.

### 10.2 Install systemd service

```bash
sudo cp /var/www/clinic/deploy/gunicorn-dev.service /etc/systemd/system/clinic.service
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable clinic
```

```bash
sudo systemctl start clinic
```

### 10.3 Check status

```bash
sudo systemctl status clinic
```

Expected: **`active (running)`** in green.

If failed:

```bash
sudo journalctl -u clinic -n 50 --no-pager
```

---

## Step 11 — Configure Nginx (web server)

### 11.1 Enable site config

```bash
sudo cp /var/www/clinic/deploy/nginx-clinic-dev.conf /etc/nginx/sites-available/clinic
```

Replace IP in nginx config if needed:

```bash
sudo sed -i 's/192.168.1.10/YOUR_REAL_IP/g' /etc/nginx/sites-available/clinic
```

(Or edit with `nano` manually.)

### 11.2 Enable site and disable default

```bash
sudo ln -sf /etc/nginx/sites-available/clinic /etc/nginx/sites-enabled/clinic
sudo rm -f /etc/nginx/sites-enabled/default
```

### 11.3 Test and reload Nginx

```bash
sudo nginx -t
```

Expected: `syntax is ok` and `test is successful`.

```bash
sudo systemctl reload nginx
```

### 11.4 Optional — firewall (UFW)

Only if firewall is enabled:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
sudo ufw status
```

---

## Step 12 — Open the app in your browser

On **Windows** (or any device on same network), open:

| Page | URL |
|------|-----|
| Home | http://192.168.1.10/ |
| Login | http://192.168.1.10/accounts/login/ |
| Admin | http://192.168.1.10/admin/ |
| Patients | http://192.168.1.10/patients/ |

Use your **createsuperuser** username and password.

If the page does not load → see [Troubleshooting](#troubleshooting).

---

## Step 13 — Windows hosts file (optional friendly name)

Like mapping `localhost` → `127.0.0.1`, map **`clinic.local`** → **server IP**.

### 13.1 Open Notepad as Administrator

1. Start menu → type **Notepad**  
2. Right-click → **Run as administrator**

### 13.2 Open hosts file

File → Open:

```
C:\Windows\System32\drivers\etc\hosts
```

Set file type to **All Files**.

### 13.3 Add one line at the bottom

```
192.168.1.10    clinic.local
```

Use your real server IP. Save the file.

### 13.4 Update `.env` on server (if not already)

`ALLOWED_HOSTS` must include `clinic.local`  
`CSRF_TRUSTED_ORIGINS` must include `http://clinic.local`

Then restart app:

```bash
sudo systemctl restart clinic
```

### 13.5 Open in browser

http://clinic.local/  
http://clinic.local/accounts/login/

### 13.6 Linux / Mac hosts (optional)

Edit `/etc/hosts` as root:

```
192.168.1.10    clinic.local
```

---

## Step 14 — Optional: auto-install script

If project is already in `/var/www/clinic`, you can run the installer (Steps 2–11 partially automated):

```bash
cd /var/www/clinic
sudo SERVER_IP=192.168.1.10 DB_PASS=devpassword123 bash deploy/install-dev.sh
```

Then create admin:

```bash
sudo -u www-data .venv/bin/python manage.py createsuperuser
```

---

## Daily use and updates

### Start / stop / restart app

```bash
sudo systemctl start clinic
sudo systemctl stop clinic
sudo systemctl restart clinic
sudo systemctl status clinic
```

### View error logs

```bash
sudo journalctl -u clinic -f
```

Press **Ctrl+C** to exit logs.

### After you change code on server

```bash
cd /var/www/clinic
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo -u www-data .venv/bin/python manage.py migrate
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart clinic
```

### Copy new code from Windows again

```powershell
scp -r "C:\shiab\Simple Patient Management System\*" ubuntu@192.168.1.10:/tmp/clinic-update/
```

On server:

```bash
sudo rsync -av /tmp/clinic-update/ /var/www/clinic/ --exclude .venv
sudo chown -R www-data:www-data /var/www/clinic
sudo systemctl restart clinic
```

### Reset admin password

```bash
cd /var/www/clinic
sudo -u www-data .venv/bin/python manage.py changepassword admin
```

---

## Full checklist

| Step | Task | Done |
|------|------|------|
| 1 | SSH into Ubuntu | ☐ |
| 2 | `apt install` python3, postgresql, nginx | ☐ |
| 3 | Note server IP (`hostname -I`) | ☐ |
| 4 | Create `clinic_user` + `clinic_db` | ☐ |
| 5 | `scp` project to `/var/www/clinic` | ☐ |
| 6 | Permissions `www-data` | ☐ |
| 7 | `.venv` + `pip install -r requirements.txt` | ☐ |
| 8 | `.env` with correct IP + DB password | ☐ |
| 9 | `manage.py check` | ☐ |
| 10 | `manage.py migrate` | ☐ |
| 11 | `manage.py collectstatic` | ☐ |
| 12 | `manage.py createsuperuser` | ☐ |
| 13 | `systemctl start clinic` — active | ☐ |
| 14 | Nginx configured and reloaded | ☐ |
| 15 | Browser `http://YOUR_IP/` works | ☐ |
| 16 | (Optional) Windows hosts `clinic.local` | ☐ |

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| **SSH connection refused** | Check server IP, VM network, firewall |
| **`DisallowedHost`** | Add IP and `clinic.local` to `ALLOWED_HOSTS` in `.env`, then `sudo systemctl restart clinic` |
| **CSRF verification failed** | Add `http://YOUR_IP` and `http://clinic.local` to `CSRF_TRUSTED_ORIGINS` in `.env`, restart clinic |
| **502 Bad Gateway** | Gunicorn not running: `sudo systemctl status clinic` and `journalctl -u clinic -n 50` |
| **`ModuleNotFoundError: django`** | Use `.venv/bin/python`, not system python |
| **Database connection failed** | Check `.env` password matches PostgreSQL; test with `psql` (Step 4.3) |
| **`no such table`** | Run `manage.py migrate` again |
| **Page loads but no CSS** | Run `collectstatic`, check Nginx `alias` points to `/var/www/clinic/staticfiles/` |
| **Cannot open from Windows** | Same Wi‑Fi? `ping SERVER_IP`. VM bridged network? |
| **Nginx error** | `sudo nginx -t` and `sudo journalctl -u nginx -n 20` |
| **Port 80 in use** | `sudo ss -tlnp | grep :80` |

### Useful debug commands

```bash
cd /var/www/clinic
sudo -u www-data .venv/bin/python manage.py check
sudo systemctl status clinic nginx postgresql
curl -I http://127.0.0.1/
```

---

## Project files reference

| File / folder | Purpose |
|---------------|---------|
| `manage.py` | Django entry point |
| `config/settings.py` | App settings, reads `.env` |
| `.env` | **Your** DB password, IP, DEBUG (create on server) |
| `.env.dev.example` | Template for `.env` |
| `requirements.txt` | Python packages (Django, gunicorn, psycopg2) |
| `deploy/gunicorn-dev.service` | systemd service file |
| `deploy/nginx-clinic-dev.conf` | Nginx config (IP / hosts) |
| `deploy/install-dev.sh` | Optional automated installer |
| `/var/www/clinic/.venv/` | Python virtual environment on server |
| PostgreSQL data | Managed by PostgreSQL (not a file in project folder) |

---

## What is NOT in this guide

| Item | Note |
|------|------|
| Live domain (`example.com`) | Not needed |
| HTTPS / SSL | Not needed for dev |
| Public internet deploy | Use [UBUNTU_SERVER_DEPLOYMENT.md](UBUNTU_SERVER_DEPLOYMENT.md) later |

---

## Quick command summary (copy block)

**On Ubuntu (after project is in `/var/www/clinic`):**

```bash
cd /var/www/clinic
sudo apt update && sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib libpq-dev nginx
sudo -u postgres psql -c "CREATE USER clinic_user WITH PASSWORD 'devpassword123';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE clinic_db OWNER clinic_user;" 2>/dev/null || true
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo cp .env.dev.example .env && sudo nano .env
sudo -u www-data .venv/bin/python manage.py migrate
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
sudo -u www-data .venv/bin/python manage.py createsuperuser
sudo cp deploy/gunicorn-dev.service /etc/systemd/system/clinic.service
sudo cp deploy/nginx-clinic-dev.conf /etc/nginx/sites-available/clinic
sudo ln -sf /etc/nginx/sites-available/clinic /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload && sudo systemctl enable clinic && sudo systemctl start clinic
sudo nginx -t && sudo systemctl reload nginx
```

**Browser:** `http://YOUR_SERVER_IP/accounts/login/`

**Windows hosts (optional):** `YOUR_SERVER_IP    clinic.local` → `http://clinic.local/`
