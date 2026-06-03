# Create super admin — troubleshooting (Windows)

Superuser creation **does work** with this project when you use the **same Python** as your venv and a **strong password**.

---

## Method A — Non-interactive (most reliable in PowerShell)

Use your **own** password instead of the example.

```powershell
cd "C:\shiab\Simple Patient Management System"

# Your choice: username + strong password (8+ chars, not too simple)
$env:DJANGO_SUPERUSER_PASSWORD = "YourStrongPasswordHere!123"

C:\shiab\.venv\Scripts\python.exe manage.py migrate --noinput
C:\shiab\.venv\Scripts\python.exe manage.py createsuperuser --noinput --username admin --email admin@example.com

# Remove password from environment (security)
Remove-Item Env:DJANGO_SUPERUSER_PASSWORD
```

Then sign in at **http://127.0.0.1:8000/accounts/login/** with username `admin` and the password you set.

**Clear the password from the terminal history** if you share your PC (or change the password after first login in `/admin/`).

---

## Method B — Interactive

```powershell
cd "C:\shiab\Simple Patient Management System"
C:\shiab\.venv\Scripts\python.exe manage.py migrate
C:\shiab\.venv\Scripts\python.exe manage.py createsuperuser
```

Type username, email (optional), password twice.

---

## Common reasons it “does not work”

| Problem | What to do |
|--------|------------|
| **Wrong folder** | You must be in `Simple Patient Management System` (where `manage.py` is). `dir manage.py` should list the file. |
| **Wrong Python** | Always use **`C:\shiab\.venv\Scripts\python.exe`** before `manage.py`, not `python` from elsewhere, unless you activated the venv: `..\.venv\Scripts\activate`. |
| **Password rejected** | Django requires a **strong** password (length, not “password123”, etc.). Use **Method A** with something like `ClinicAdmin2026!Secure`. |
| **“no such table”** | Run: `C:\shiab\.venv\Scripts\python.exe manage.py migrate` |
| **PostgreSQL errors** | Use SQLite for local setup: `$env:USE_SQLITE="1"` (or unset `USE_SQLITE` if your project defaults to SQLite — check `config/settings.py`). |
| **Nothing happens / freezes** | Run commands in **PowerShell** or **cmd**, not inside a broken shell. |

---

## Check that Django is OK

```powershell
cd "C:\shiab\Simple Patient Management System"
C:\shiab\.venv\Scripts\python.exe manage.py check
C:\shiab\.venv\Scripts\python.exe manage.py migrate --noinput
```

Both should finish without errors.

---

## After you have a superuser

- **App:** http://127.0.0.1:8000/accounts/login/  
- **Django admin (users / roles):** http://127.0.0.1:8000/admin/  

If you **already** have a superuser but forgot the password:

```powershell
cd "C:\shiab\Simple Patient Management System"
C:\shiab\.venv\Scripts\python.exe manage.py changepassword YOUR_USERNAME
```

If you tell me the **exact error message** (copy-paste from the terminal), I can narrow it down further.
