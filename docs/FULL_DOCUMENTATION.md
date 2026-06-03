# Clinic PMS — Full documentation

This guide explains **how the project works**, **how to run it**, and **how to develop** it safely. There is **no built-in default admin password** (that would be insecure). You create the first admin yourself (see below).

---

## 1. Security: users and passwords

### There is no shared “project password”

- Django **never** ships with a default superuser password.
- **You** choose the username and password when you run `createsuperuser`.
- **Do not** commit real passwords, `.env` files with secrets, or database dumps to git.

### Create the main administrator (superuser)

From the project root:

```powershell
cd "C:\shiab\Simple Patient Management System"
..\.venv\Scripts\activate
python manage.py createsuperuser
```

You will be prompted for:

- **Username** — e.g. `admin` (your choice)
- **Email** — optional
- **Password** — type twice (choose something strong; only you know it)

This account:

- Can **sign in** at `/accounts/login/`
- Can open **Django Admin** at `/admin/` (manage users and **Clinic role**)
- Has **full access** to patients, appointments, and invoices in the app

### Create extra staff users

1. Sign in to `/admin/` as superuser.
2. Go to **Users** → **Add user**.
3. Set username/password; enable **Staff status** if they should access `/admin/` to manage users/roles.
4. On the same user page, set **Clinic role** (Reception, Billing, Clinic admin, Viewer).

---

## 2. What this project is

**Simple Patient Management System** — a Django web app for:

| Area | Purpose |
|------|--------|
| **Patients** | Register, search, edit (roles restrict delete). |
| **Appointments** | Schedule visits; status: Pending → Waiting → Done. |
| **Invoices** | One invoice per appointment; payments, discounts, void/cancel. |
| **Dashboard** | Counts and today’s appointments. |

Stack: **Django 6**, **SQLite by default** (optional PostgreSQL), **Bootstrap 5** UI.

---

## 3. Folder structure (where things live)

```
Simple Patient Management System/
├── manage.py                 # Run Django commands
├── requirements.txt
├── config/                   # Settings, root URLs, dashboard view
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── apps/
│   ├── accounts/             # Login, logout, UserProfile (role)
│   ├── patients/
│   ├── appointments/
│   └── billing/
├── templates/                # HTML (Bootstrap)
├── static/css/               # Custom styles (e.g. clinic.css)
├── tests/                    # Automated tests
├── docs/                     # Documentation
└── data/                     # SQLite file (default): db.sqlite3
```

Request flow: **URL** → **view** (in `apps/*` or `config`) → **models** → **database** → **template** response.

---

## 4. How to run locally

### One-time setup

```powershell
cd "C:\shiab\Simple Patient Management System"
..\.venv\Scripts\activate
pip install -r requirements.txt
```

### Database

**SQLite (default)** — no extra install. DB path: `data/db.sqlite3`.

**PostgreSQL** — set environment variables and **do not** set `USE_SQLITE=1`:

```powershell
$env:USE_SQLITE="0"
$env:DB_NAME="clinic_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="YOUR_PASSWORD"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

### Migrate and create superuser

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### Start the server

```powershell
python manage.py runserver
```

URLs:

| URL | Description |
|-----|--------------|
| http://127.0.0.1:8000/ | Dashboard (requires login) |
| http://127.0.0.1:8000/accounts/login/ | Staff login |
| http://127.0.0.1:8000/admin/ | Django admin (users, roles) |
| http://127.0.0.1:8000/patients/ | Patients |
| http://127.0.0.1:8000/appointments/ | Appointments |
| http://127.0.0.1:8000/invoices/ | Invoices |

---

## 5. Roles and permissions (how access works)

Roles are stored in **`UserProfile`** (`apps/accounts/models.py`), linked 1:1 to Django **`User`**.

Logic lives in **`apps/accounts/permissions.py`**. Templates get flags from **`apps/accounts/context_processors.py`** (e.g. `can_edit_billing`, `show_patients_nav`).

| Role | Typical use |
|------|----------------|
| **Superuser** (`createsuperuser`) | Everything + Django admin. |
| **Clinic admin** | Full app modules; use Admin to give others roles. |
| **Reception** | Patients + appointments only. |
| **Billing** | Invoices only (no patient add/edit). |
| **Viewer** | Read-only. |

Views use `@login_required` plus decorators like `require_patients_section`, `require_edit_billing`, etc.

---

## 6. Development guide

### Daily workflow

1. Activate venv: `..\.venv\Scripts\activate`
2. Pull latest code (if using git).
3. Install deps if `requirements.txt` changed: `pip install -r requirements.txt`
4. Apply migrations if models changed: `python manage.py migrate`
5. Run server: `python manage.py runserver`
6. Run tests before committing: `python manage.py test tests`

### After changing models

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Running tests

```powershell
python manage.py test tests
```

### Useful commands

```powershell
python manage.py shell          # Django shell
python manage.py dbshell        # Raw DB shell (SQLite/psql)
python manage.py check          # System checks
```

### Where to change behavior

| Task | Look at |
|------|--------|
| URL routes | `config/urls.py`, `apps/*/urls.py` |
| Page logic | `config/views.py`, `apps/*/views.py` |
| Forms / validation | `apps/*/forms.py` |
| Database schema | `apps/*/models.py` |
| Access control | `apps/accounts/permissions.py`, view decorators |
| HTML / UI | `templates/`, `static/css/clinic.css` |
| Login / roles admin | `apps/accounts/admin.py`, Django `/admin/` |

### IDE / Cursor tips

- Open the folder **`Simple Patient Management System`** as the workspace root.
- Use breakpoints on views or run `manage.py runserver` from the integrated terminal.
- After template changes, refresh the browser (no restart usually needed).

### Git (if you use it)

- Ignore: `.venv/`, `data/db.sqlite3`, `*.pyc`, `.env` with secrets.
- Do not commit superuser passwords or production `SECRET_KEY`.

---

## 7. Configuration reference (`config/settings.py`)

| Setting | Meaning |
|---------|--------|
| `USE_SQLITE` env `1` (default) | Use `data/db.sqlite3` |
| `SECRET_KEY` | Set in production via env |
| `DEBUG` | `False` in production |
| `LOGIN_URL` | `accounts:login` |
| `INSTALLED_APPS` | Includes `apps.accounts`, patients, appointments, billing |

---

## 8. Troubleshooting

| Problem | What to try |
|---------|--------------|
| Redirect to login | Normal if not signed in; use `/accounts/login/`. |
| No such table | Run `python manage.py migrate`. |
| PostgreSQL password error | Fix `DB_*` env vars or use SQLite (`USE_SQLITE=1`). |
| 403 / “no permission” | Check user’s **Clinic role** in `/admin/`. |
| Static CSS missing | Ensure `STATICFILES_DIRS` includes `static/`; for production run `collectstatic`. |

---

## 9. Quick reference card

```text
CREATE ADMIN:     python manage.py createsuperuser
RUN:              python manage.py runserver
MIGRATE:          python manage.py migrate
TESTS:            python manage.py test tests
LOGIN PAGE:       /accounts/login/
DJANGO ADMIN:     /admin/
```

Your **admin username and password** are exactly what you typed during `createsuperuser` — store them in a password manager, not in the repo.
