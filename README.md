# Patient Management System

Django clinic management app with organized folder structure.

## Project folders

| Folder | Purpose |
|--------|---------|
| `config/` | Django settings, URLs, WSGI, dashboard view |
| `apps/` | Django apps (`accounts`, `patients`, `appointments`, `billing`) |
| `templates/` | HTML templates (Bootstrap 5) |
| `static/` | CSS, JS, images |
| `tests/` | Project test suite |
| `docs/` | README details & SDLC documentation |
| `scripts/` | Utility scripts |
| `data/` | SQLite database (auto-created) |

## Quick start

**Step-by-step run guide:** **[docs/RUN_GUIDE.md](docs/RUN_GUIDE.md)** (recommended for first-time setup)

```powershell
cd "C:\shiab\Simple Patient Management System"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**SQLite (default):** `data/db.sqlite3` — no extra install.

**PostgreSQL (local):** copy `.env.example` to `.env`, set `USE_SQLITE=0` → **[PostgreSQL setup](docs/POSTGRESQL_SETUP.md)**.

**Ubuntu server (IP / LAN, full dev guide):** → **[Ubuntu dev deploy — step by step](docs/UBUNTU_DEV_DEPLOY.md)**  
**Ubuntu server (domain + HTTPS):** → **[Ubuntu production deploy](docs/UBUNTU_SERVER_DEPLOYMENT.md)**

Open **http://127.0.0.1:8000/** — you will be redirected to **sign in** (`/accounts/login/`). Use the superuser you created, or add staff users in **Django Admin** (`/admin/`) and set their **Clinic role** there.

Full guides:

- **[How to run (step by step)](docs/RUN_GUIDE.md)** — this PC, **another device**, and LAN access from phone/tablet  
- **[Create super admin (troubleshooting)](docs/SUPERUSER_SETUP.md)** — if `createsuperuser` fails on Windows  
- **[Full documentation](docs/FULL_DOCUMENTATION.md)** — security, roles, structure, development  
- **[Setup & URL map](docs/README.md)** — install, PostgreSQL, tests  

Your **admin password** is the one you set with `python manage.py createsuperuser` (there is no default).
