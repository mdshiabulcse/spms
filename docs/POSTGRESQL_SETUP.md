# PostgreSQL setup — Patient Management System

## 1. Install PostgreSQL (Windows)

1. Download: https://www.postgresql.org/download/windows/
2. Install (remember the **postgres user password** you set).
3. Default port: **5432**.

## 2. Create the database

Open **pgAdmin** or **SQL Shell (psql)** and run:

```sql
CREATE DATABASE clinic_db;
```

Or in PowerShell (if `psql` is on PATH):

```powershell
psql -U postgres -c "CREATE DATABASE clinic_db;"
```

## 3. Project settings (already in code)

File: **`config/settings.py`**

When `USE_SQLITE=0`, Django uses PostgreSQL:

| Variable | Meaning | Example |
|----------|---------|---------|
| `USE_SQLITE` | `0` = PostgreSQL, `1` = SQLite | `0` |
| `DB_NAME` | Database name | `clinic_db` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | User password | your password |
| `DB_HOST` | Server host | `localhost` |
| `DB_PORT` | Port | `5432` |

## 4. Create `.env` file (easiest)

In the project folder:

```powershell
cd "C:\shiab\Simple Patient Management System"
Copy-Item .env.example .env
notepad .env
```

Edit `.env` — example for PostgreSQL:

```env
USE_SQLITE=0
DB_NAME=clinic_db
DB_USER=postgres
DB_PASSWORD=YourActualPostgresPassword
DB_HOST=localhost
DB_PORT=5432
```

Save the file. **Do not share `.env`** (it has your password).

## 5. Install Python packages & migrate

```powershell
cd "C:\shiab\Simple Patient Management System"
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 6. Without `.env` — PowerShell variables

Same session, before `migrate` / `runserver`:

```powershell
$env:USE_SQLITE="0"
$env:DB_NAME="clinic_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="YourActualPostgresPassword"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
python manage.py migrate
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `password authentication failed` | Wrong `DB_PASSWORD` in `.env` |
| `database "clinic_db" does not exist` | Run `CREATE DATABASE clinic_db;` |
| `could not connect to server` | Start PostgreSQL service (Windows Services → postgresql) |
| `No module named 'psycopg2'` | `pip install -r requirements.txt` |
| Still uses SQLite | Set `USE_SQLITE=0` in `.env` or `$env:USE_SQLITE="0"` |

## Switch back to SQLite

In `.env`:

```env
USE_SQLITE=1
```

Or remove `.env` and run:

```powershell
$env:USE_SQLITE="1"
```
