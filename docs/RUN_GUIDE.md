# Simple Run Guide — Patient Management System

Django app. You need **Python 3.10+** and a **`.venv`** folder (virtual environment) in the project.

---

## Database — which one, where is the file, where are settings?

| Item | Answer |
|------|--------|
| **Default database** | **SQLite** (file on disk, no separate server) |
| **Database file location** | `data\db.sqlite3` inside the project folder |
| **Full path (your PC)** | `C:\shiab\Simple Patient Management System\data\db.sqlite3` |
| **Settings file** | `config\settings.py` (lines 62–86) |
| **Env template** | `.env.example` (optional variables) |

**PostgreSQL:** see **[POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)** — copy `.env.example` to `.env`, set `USE_SQLITE=0` and your DB password.

The `data` folder is created automatically when Django starts. The file `db.sqlite3` appears after you run `python manage.py migrate`.

**Manage data in the app:** use the website (patients, appointments, invoices) or **Django Admin** at http://127.0.0.1:8000/admin/

**Backup:** copy `data\db.sqlite3` to a safe place.

---

## What is `.venv`?

`.venv` is a folder that holds Python packages for **this project only** (Django, etc.).

- You **create** it once per computer with one command.
- You **do not** copy `.venv` from another PC — create it again on each device.
- After creating it, you **activate** it before running the app.

---

## Step 1 — Install Python (if needed)

1. Download: https://www.python.org/downloads/
2. Install and check **“Add python.exe to PATH”**.
3. Open **PowerShell** and check:

```powershell
python --version
```

---

## Step 2 — Go to project folder

```powershell
cd "C:\shiab\Simple Patient Management System"
```

*(On another PC, use your folder path — the folder that contains `manage.py`.)*

---

## Step 3 — Create `.venv` folder (first time only)

Run this **inside** the project folder:

```powershell
python -m venv .venv
```

This creates a folder named `.venv` next to `manage.py`.

**Check it exists:**

```powershell
dir .venv
```

You should see `Scripts` inside `.venv`.

---

## Step 4 — Activate `.venv`

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\activate
```

You should see `(.venv)` at the start of your line.

**macOS / Linux:**

```bash
source .venv/bin/activate
```

---

## Step 5 — Install packages (first time only)

```powershell
pip install -r requirements.txt
```

---

## Step 6 — Database & admin (first time only)

```powershell
python manage.py migrate
python manage.py createsuperuser
```

Choose a username and password when asked.

---

## Step 7 — Run the app

```powershell
python manage.py runserver
```

### Easy way (no activate) — use project scripts

```powershell
cd "C:\shiab\Simple Patient Management System"
.\setup.ps1      # first time only — creates .venv + installs Django
.\migrate.ps1    # migrate
.\run.ps1        # start server
```

These always use `.\.venv\Scripts\python.exe` so you avoid the “No module named django” error.

Open in browser: **http://127.0.0.1:8000/**  
Login: **http://127.0.0.1:8000/accounts/login/**

Stop server: press **Ctrl+C**

---

## All commands together (copy & paste)

**First time on any PC:**

```powershell
cd "C:\shiab\Simple Patient Management System"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Every day after that:**

```powershell
cd "C:\shiab\Simple Patient Management System"
.\.venv\Scripts\activate
python manage.py runserver
```

---

## Another device (simple)

1. Copy the project folder to the new PC (USB / ZIP).
2. **Do not copy** `.venv` from the old PC.
3. On the new PC, run the **“First time”** block above (change the `cd` path to your folder).
4. That creates a **new** `.venv` on that device.

**Keep old data?** Copy `data\db.sqlite3` with the project. Then skip `createsuperuser` and use your old login.

---

## Open from phone (same Wi‑Fi)

On the PC that runs the server:

```powershell
cd "C:\shiab\Simple Patient Management System"
.\.venv\Scripts\activate
ipconfig
```

Note your **IPv4** (example: `192.168.1.105`).

```powershell
$env:ALLOWED_HOSTS="localhost,127.0.0.1,192.168.1.105"
python manage.py runserver 0.0.0.0:8000
```

On phone browser: `http://192.168.1.105:8000/`  
(Use your real IP, not this example.)

---

## Problems?

| Problem | Fix |
|---------|-----|
| No `.venv` folder | Run: `python -m venv .venv` |
| `django` not found | Run: `.\.venv\Scripts\activate` then `pip install -r requirements.txt` |
| `manage.py` not found | `cd` to folder with `manage.py` |
| Forgot password | `python manage.py changepassword YOUR_USERNAME` |

More help: [SUPERUSER_SETUP.md](SUPERUSER_SETUP.md)
