# Deploy on Ubuntu Server (domain + HTTPS) — PostgreSQL + Nginx + Gunicorn

> **Developer / LAN / IP only (no domain):** use **[UBUNTU_DEV_DEPLOY.md](UBUNTU_DEV_DEPLOY.md)** — simpler, like Windows `hosts` file.

Full guide: run **Patient Management System** on a **live Ubuntu server** with a **real domain** and **HTTPS**.

Replace placeholders:

| Placeholder | Your value |
|-------------|------------|
| `YOUR_SERVER_IP` | e.g. `203.0.113.50` |
| `your-domain.com` | Your domain (or use IP only) |
| `CHANGE_STRONG_DB_PASSWORD` | PostgreSQL password for app user |
| `CHANGE_TO_LONG_RANDOM_STRING` | Django `SECRET_KEY` |

**Project path on server:** `/var/www/clinic`

---

## Overview (what you will install)

```
Internet → Nginx (port 80/443) → Gunicorn (Unix socket) → Django app
                                      ↓
                              PostgreSQL (clinic_db)
```

| Component | Role |
|-----------|------|
| **Ubuntu** | Operating system |
| **PostgreSQL** | Database |
| **Python + venv** | Run Django |
| **Gunicorn** | Production app server |
| **Nginx** | Web server / reverse proxy |
| **systemd** | Keep Gunicorn running after reboot |

---

## Part 1 — Prepare the Ubuntu server

### 1.1 Connect with SSH

From your PC:

```bash
ssh root@YOUR_SERVER_IP
```

Or use a user with `sudo`:

```bash
ssh ubuntu@YOUR_SERVER_IP
```

### 1.2 Update system

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Install required packages

```bash
sudo apt install -y \
  python3 python3-venv python3-pip \
  postgresql postgresql-contrib libpq-dev \
  nginx git curl
```

Check versions:

```bash
python3 --version
psql --version
nginx -v
```

---

## Part 2 — PostgreSQL database

### 2.1 Create database and user

```bash
sudo -u postgres psql
```

In the `psql` prompt, run (change the password):

```sql
CREATE USER clinic_user WITH PASSWORD 'CHANGE_STRONG_DB_PASSWORD';
CREATE DATABASE clinic_db OWNER clinic_user;
GRANT ALL PRIVILEGES ON DATABASE clinic_db TO clinic_user;
\q
```

### 2.2 Test connection

```bash
psql -h localhost -U clinic_user -d clinic_db -c "SELECT 1;"
```

Enter the password when asked. You should see `1` in the result.

---

## Part 3 — Upload the project to the server

Choose **one** method.

### Method A — Copy from Windows (SCP)

On your **Windows PC** (PowerShell), zip or copy the folder, then:

```powershell
scp -r "C:\shiab\Simple Patient Management System" ubuntu@YOUR_SERVER_IP:/tmp/clinic
```

On the **server**:

```bash
sudo mkdir -p /var/www
sudo mv /tmp/clinic "/var/www/clinic"
```

### Method B — Git (if project is in a repository)

On the **server**:

```bash
sudo mkdir -p /var/www
sudo git clone YOUR_REPO_URL /var/www/clinic
```

### 3.1 Set folder permissions

```bash
sudo chown -R www-data:www-data /var/www/clinic
sudo mkdir -p /var/www/clinic/run
sudo chown -R www-data:www-data /var/www/clinic/run
```

---

## Part 4 — Python virtual environment

```bash
cd /var/www/clinic
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install --upgrade pip
sudo -u www-data .venv/bin/pip install -r requirements.txt
```

Verify Django and Gunicorn:

```bash
sudo -u www-data .venv/bin/python -c "import django; print(django.VERSION)"
sudo -u www-data .venv/bin/gunicorn --version
```

---

## Part 5 — Environment file (`.env`)

### 5.1 Create `.env` on the server

```bash
cd /var/www/clinic
sudo cp .env.production.example .env
sudo nano .env
```

Example content (edit all values):

```env
USE_SQLITE=0

DB_NAME=clinic_db
DB_USER=clinic_user
DB_PASSWORD=CHANGE_STRONG_DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=CHANGE_TO_LONG_RANDOM_STRING
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**Generate `SECRET_KEY` (on server):**

```bash
.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output into `.env` as `SECRET_KEY`.

**If you use IP only (no domain yet):**

```env
ALLOWED_HOSTS=YOUR_SERVER_IP
DEBUG=False
```

Leave `CSRF_TRUSTED_ORIGINS` empty until you enable HTTPS, or use `http://YOUR_SERVER_IP` only for testing (not recommended long term).

### 5.2 Secure `.env`

```bash
sudo chown www-data:www-data /var/www/clinic/.env
sudo chmod 600 /var/www/clinic/.env
```

Settings are read from **`config/settings.py`** and **`.env`** in the project root.

---

## Part 6 — Django setup (migrate, static, admin)

```bash
cd /var/www/clinic

sudo -u www-data .venv/bin/python manage.py check
sudo -u www-data .venv/bin/python manage.py migrate
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
```

Create admin user (interactive):

```bash
sudo -u www-data .venv/bin/python manage.py createsuperuser
```

---

## Part 7 — Gunicorn (systemd service)

### 7.1 Install systemd unit

```bash
sudo cp /var/www/clinic/deploy/gunicorn.service /etc/systemd/system/clinic.service
```

If your path is different, edit the service file first:

```bash
sudo nano /etc/systemd/system/clinic.service
```

### 7.2 Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable clinic
sudo systemctl start clinic
sudo systemctl status clinic
```

Should show **active (running)**.

### 7.3 Logs if it fails

```bash
sudo journalctl -u clinic -n 50 --no-pager
```

---

## Part 8 — Nginx (public web access)

### 8.1 Configure site

Edit the example config (set your domain or IP):

```bash
sudo nano /var/www/clinic/deploy/nginx-clinic.conf
```

Change `server_name` to your domain or `_` for default.

Copy to Nginx:

```bash
sudo cp /var/www/clinic/deploy/nginx-clinic.conf /etc/nginx/sites-available/clinic
sudo ln -sf /etc/nginx/sites-available/clinic /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 8.2 Open firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### 8.3 Test in browser

- **http://YOUR_SERVER_IP/**  
- **http://your-domain.com/**  
- Login: **/accounts/login/**  
- Admin: **/admin/**

---

## Part 9 — HTTPS (recommended for live site)

Only if you have a **domain** pointing to the server IP.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Certbot updates Nginx for HTTPS. Renewals are automatic.

Update `.env`:

```env
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Then:

```bash
sudo systemctl restart clinic
```

---

## Part 10 — Checklist (start to end)

| Step | Command / action | Done |
|------|------------------|------|
| 1 | `apt update && apt upgrade` | ☐ |
| 2 | Install python3, postgresql, nginx | ☐ |
| 3 | Create `clinic_db` + `clinic_user` in PostgreSQL | ☐ |
| 4 | Project in `/var/www/clinic` | ☐ |
| 5 | `python3 -m venv .venv` + `pip install -r requirements.txt` | ☐ |
| 6 | Create `.env` with `USE_SQLITE=0` | ☐ |
| 7 | `manage.py migrate` | ☐ |
| 8 | `manage.py collectstatic` | ☐ |
| 9 | `manage.py createsuperuser` | ☐ |
| 10 | Enable `clinic` systemd service | ☐ |
| 11 | Configure Nginx + `ufw` | ☐ |
| 12 | Optional: Certbot HTTPS | ☐ |
| 13 | Open site in browser & login | ☐ |

---

## Daily commands (after deployment)

| Task | Command |
|------|---------|
| Restart app | `sudo systemctl restart clinic` |
| View app logs | `sudo journalctl -u clinic -f` |
| Nginx reload | `sudo systemctl reload nginx` |
| New code deploy | `cd /var/www/clinic && sudo -u www-data git pull` (if using git) |
| After code update | `sudo -u www-data .venv/bin/pip install -r requirements.txt` |
| | `sudo -u www-data .venv/bin/python manage.py migrate` |
| | `sudo -u www-data .venv/bin/python manage.py collectstatic --noinput` |
| | `sudo systemctl restart clinic` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `DisallowedHost` | Add domain/IP to `ALLOWED_HOSTS` in `.env`, restart `clinic` |
| `502 Bad Gateway` | `sudo systemctl status clinic` — Gunicorn not running |
| Database connection error | Check `.env` `DB_*` values; test with `psql` |
| Static CSS missing | Run `collectstatic`; check Nginx `alias` path `/var/www/clinic/staticfiles/` |
| CSRF error on HTTPS | Set `CSRF_TRUSTED_ORIGINS` with `https://...` |
| Permission denied on socket | `sudo chown www-data:www-data /var/www/clinic/run` |

---

## File reference

| File | Purpose |
|------|---------|
| `config/settings.py` | Django + DB config (reads `.env`) |
| `.env` | Secrets on server (not in git) |
| `.env.production.example` | Template for production |
| `deploy/gunicorn.service` | systemd unit |
| `deploy/nginx-clinic.conf` | Nginx site |
| `requirements.txt` | Includes `gunicorn`, `psycopg2-binary` |

---

## Security reminders (live server)

- Set `DEBUG=False` in `.env`
- Use a strong `SECRET_KEY` and `DB_PASSWORD`
- Use HTTPS (Certbot) when you have a domain
- Keep Ubuntu updated: `sudo apt update && sudo apt upgrade`
- Do not expose PostgreSQL port `5432` to the internet

---

## Related docs

- [PostgreSQL on Windows/local](POSTGRESQL_SETUP.md)
- [Simple local run](RUN_GUIDE.md)
