# Patient Management System — SDLC Documentation

## PHASE 1: REQUIREMENT ANALYSIS

### System Overview
Simple Patient Management System built with **Django (MVT)** and **PostgreSQL**, providing patient records, appointments, billing/invoices, and an operational dashboard.

### Functional Requirements

| Module | Requirements |
|--------|-------------|
| **Patient Management** | Create, update (shared form), list, search by name/phone/ID |
| **Appointments** | Create for patient, list, statuses PENDING/WAITING/DONE, filter by status |
| **Invoices** | Create per appointment, payment tracking (paid/due/partial), discount, list & detail |
| **Invoice Control** | Void, cancel with reason, refund tracking |
| **Dashboard** | Total patients, today's appointments, pending appointments, revenue summary |

### Non-Functional Requirements
- Bootstrap 5 UI (CDN)
- PostgreSQL persistence
- Fast CRUD via indexed search fields
- Clean separation: `patients`, `appointments`, `billing` apps

---

## PHASE 2: SYSTEM DESIGN

### Architecture (Django MVT)

```
Browser → URLs → Views (FBV) → Models → PostgreSQL
                ↓
            Templates (Bootstrap 5)
```

### App Separation

| App | Responsibility |
|-----|----------------|
| `patients` | Patient CRUD, search |
| `appointments` | Appointment CRUD, status workflow |
| `billing` | Invoices, payments, void/cancel/refund |
| `config/` | Project settings, dashboard, root URLs |
| `apps/` | `patients`, `appointments`, `billing` Django apps |
| `templates/` | Bootstrap 5 HTML templates |
| `static/` | CSS/JS assets |
| `tests/` | Automated test suite |
| `docs/` | Documentation |
| `data/` | Database files (SQLite) |

### Entity Relationship Diagram

```
Patient (1) ──────< (N) Appointment (1) ────── (1) Invoice
```

### Database Design

**Patient**
- PK `id`, indexed `name`, `phone`
- `age`, `gender`, `address`, `created_at`

**Appointment**
- FK → Patient (`PROTECT`)
- `date`, `serial_no` (unique per date)
- `status`: PENDING | WAITING | DONE
- `note`

**Invoice**
- OneToOne → Appointment (`PROTECT`)
- `total`, `discount`, `paid`, `due` (computed)
- `status`: UNPAID | PARTIAL | PAID
- `is_void`, `cancel_reason`, `refund_amount`

### Business Rules
1. Single form for patient create/update
2. Appointment flow: PENDING → WAITING → DONE only
3. `due = total - discount - paid` (auto on save)
4. No negative monetary values; refund ≤ paid
5. Void/cancelled invoices block payment edits

---

## PHASE 9: TESTING CHECKLIST

- [ ] Patient create/update via same form
- [ ] Patient search (name, phone, ID)
- [ ] Appointment create and status PENDING → WAITING → DONE
- [ ] Invoice: due = total - discount - paid
- [ ] Partial/PAID/UNPAID status derived correctly
- [ ] Void prevents payment editing
- [ ] Cancel requires reason
- [ ] Refund cannot exceed paid
- [ ] Dashboard counts and revenue
- [ ] All URLs resolve (no 404)
- [ ] `python manage.py migrate` runs clean

---

## PHASE 10: RUN & DEPLOY GUIDE

See **README.md** for full commands.

### Quick Start
```powershell
cd C:\shiab
.\.venv\Scripts\activate
pip install -r requirements.txt

# Create PostgreSQL database first:
# CREATE DATABASE clinic_db;

$env:DB_NAME="clinic_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Production Notes
- Set `DEBUG=False`, strong `SECRET_KEY`, configure `ALLOWED_HOSTS`
- Use `gunicorn` + `nginx`, static files via `collectstatic`
- Use environment variables for DB credentials (never commit secrets)
- Enable HTTPS and database connection pooling
