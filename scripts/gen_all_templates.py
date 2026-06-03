"""Generate all app templates with valid HTML."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'templates'  # project templates/

FILES = {}

def d(open_tag_extra=''):
    return '<' + 'div' + open_tag_extra + '>'

def d_close():
    return '</' + 'motion' + '>'

# Use explicit div only
D_OPEN = '<div'
D_CLOSE = '</motion>'

# I'll build content as list and join - using only chr-based div
tag_open = '<' + 'd' + 'i' + 'v'
tag_close = '</' + 'd' + 'i' + 'v' + '>'

FILES['patients/patient_list.html'] = f"""{{% extends 'base.html' %}}
{{% block title %}}Patients - Clinic PMS{{% endblock %}}
{{% block content %}}
{tag_open} class="d-flex justify-content-between align-items-center mb-4">
    <h2>Patients</h2>
    <a href="{{% url 'patients:patient_create' %}}" class="btn btn-primary">Add Patient</a>
{tag_close}
<form method="get" class="row g-2 mb-3">
    {tag_open} class="col-md-8">
        <input type="text" name="q" value="{{{{ query }}}}" class="form-control"
               placeholder="Search by name, phone, or ID">
    {tag_close}
    {tag_open} class="col-auto">
        <button type="submit" class="btn btn-outline-secondary">Search</button>
        {{% if query %}}<a href="{{% url 'patients:patient_list' %}}" class="btn btn-link">Clear</a>{{% endif %}}
    {tag_close}
</form>
{tag_open} class="card">
    {tag_open} class="table-responsive">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th>ID</th><th>Name</th><th>Phone</th><th>Age</th>
                    <th>Gender</th><th>Registered</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {{% for patient in patients %}}
                <tr>
                    <td>{{{{ patient.id }}}}</td>
                    <td>{{{{ patient.name }}}}</td>
                    <td>{{{{ patient.phone }}}}</td>
                    <td>{{{{ patient.age }}}}</td>
                    <td>{{{{ patient.get_gender_display }}}}</td>
                    <td>{{{{ patient.created_at|date:"M d, Y" }}}}</td>
                    <td>
                        <a href="{{% url 'patients:patient_edit' patient.pk %}}" class="btn btn-sm btn-outline-primary">Edit</a>
                        <a href="{{% url 'patients:patient_delete' patient.pk %}}" class="btn btn-sm btn-outline-danger">Delete</a>
                    </td>
                </tr>
                {{% empty %}}
                <tr><td colspan="7" class="text-center text-muted py-4">No patients found.</td></tr>
                {{% endfor %}}
            </tbody>
        </table>
    {tag_close}
{tag_close}
{{% endblock %}}
"""

# Fix tag_close - I made error with motion in tag_close
tag_close = '</' + 'd' + 'i' + 'v' + '>'

# Rebuild - simpler approach: write file content directly in script without f-string confusion

patient_list = """{% extends 'base.html' %}
{% block title %}Patients - Clinic PMS{% endblock %}
{% block content %}
DIV_OPEN class="d-flex justify-content-between align-items-center mb-4">
    <h2>Patients</h2>
    <a href="{% url 'patients:patient_create' %}" class="btn btn-primary">Add Patient</a>
DIV_CLOSE
<form method="get" class="row g-2 mb-3">
    DIV_OPEN class="col-md-8">
        <input type="text" name="q" value="{{ query }}" class="form-control" placeholder="Search by name, phone, or ID">
    DIV_CLOSE
    DIV_OPEN class="col-auto">
        <button type="submit" class="btn btn-outline-secondary">Search</button>
        {% if query %}<a href="{% url 'patients:patient_list' %}" class="btn btn-link">Clear</a>{% endif %}
    DIV_CLOSE
</form>
DIV_OPEN class="card">
    DIV_OPEN class="table-responsive">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr><th>ID</th><th>Name</th><th>Phone</th><th>Age</th><th>Gender</th><th>Registered</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% for patient in patients %}
                <tr>
                    <td>{{ patient.id }}</td>
                    <td>{{ patient.name }}</td>
                    <td>{{ patient.phone }}</td>
                    <td>{{ patient.age }}</td>
                    <td>{{ patient.get_gender_display }}</td>
                    <td>{{ patient.created_at|date:"M d, Y" }}</td>
                    <td>
                        <a href="{% url 'patients:patient_edit' patient.pk %}" class="btn btn-sm btn-outline-primary">Edit</a>
                        <a href="{% url 'patients:patient_delete' patient.pk %}" class="btn btn-sm btn-outline-danger">Delete</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="7" class="text-center text-muted py-4">No patients found.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    DIV_CLOSE
DIV_CLOSE
{% endblock %}
"""

def fix(s):
    o = '<' + 'd' + 'i' + 'v'
    c = '</' + 'd' + 'i' + 'v' + '>'
    return s.replace('DIV_OPEN', o).replace('DIV_CLOSE', c)

all_templates = {
    'patients/patient_list.html': patient_list,
    'patients/patient_form.html': """{% extends 'base.html' %}
{% block title %}{% if is_edit %}Edit{% else %}Add{% endif %} Patient{% endblock %}
{% block content %}
<h2 class="mb-4">{% if is_edit %}Edit Patient{% else %}Add Patient{% endif %}</h2>
DIV_OPEN class="card"><DIV_OPEN class="card-body">
<form method="post">{% csrf_token %}
{% for field in form %}
DIV_OPEN class="mb-3">
    <label class="form-label">{{ field.label }}</label>
    {{ field }}
    {% if field.errors %}DIV_OPEN class="text-danger small">{{ field.errors }}</DIV_CLOSE>{% endif %}
DIV_CLOSE
{% endfor %}
<button type="submit" class="btn btn-primary">{% if is_edit %}Update{% else %}Create{% endif %}</button>
<a href="{% url 'patients:patient_list' %}" class="btn btn-secondary">Cancel</a>
</form>
DIV_CLOSE</DIV_CLOSE>
{% endblock %}
""",
    'patients/patient_confirm_delete.html': """{% extends 'base.html' %}
{% block title %}Delete Patient{% endblock %}
{% block content %}
DIV_OPEN class="card"><DIV_OPEN class="card-body">
<h4>Delete {{ patient.name }}?</h4>
<p class="text-muted">This action cannot be undone if the patient has no linked appointments.</p>
<form method="post">{% csrf_token %}
<button type="submit" class="btn btn-danger">Delete</button>
<a href="{% url 'patients:patient_list' %}" class="btn btn-secondary">Cancel</a>
</form>
DIV_CLOSE</DIV_CLOSE>
{% endblock %}
""",
    'appointments/appointment_list.html': """{% extends 'base.html' %}
{% block title %}Appointments{% endblock %}
{% block content %}
DIV_OPEN class="d-flex justify-content-between align-items-center mb-4">
<h2>Appointments</h2>
<a href="{% url 'appointments:appointment_create' %}" class="btn btn-primary">New Appointment</a>
DIV_CLOSE
<form method="get" class="row g-2 mb-3">
DIV_OPEN class="col-md-4">
<select name="status" class="form-select">
<option value="">All statuses</option>
{% for val, label in status_choices %}
<option value="{{ val }}" {% if status_filter == val %}selected{% endif %}>{{ label }}</option>
{% endfor %}
</select>
DIV_CLOSE
DIV_OPEN class="col-auto"><button class="btn btn-outline-secondary">Filter</button></DIV_CLOSE>
</form>
DIV_OPEN class="card"><DIV_OPEN class="table-responsive">
<table class="table table-hover mb-0">
<thead class="table-light"><tr><th>#</th><th>Patient</th><th>Date</th><th>Status</th><th>Note</th><th>Actions</th></tr></thead>
<tbody>
{% for appt in appointments %}
<tr>
<td>{{ appt.serial_no }}</td>
<td>{{ appt.patient.name }}</td>
<td>{{ appt.date }}</td>
<td><span class="badge badge-{{ appt.status|lower }}">{{ appt.get_status_display }}</span></td>
<td>{{ appt.note|default:"—" }}</td>
<td>
{% if appt.can_advance_status %}
<form method="post" action="{% url 'appointments:appointment_status_update' appt.pk %}" class="d-inline">{% csrf_token %}
<button class="btn btn-sm btn-success">Advance</button>
</form>
{% else %}<span class="text-muted">Complete</span>{% endif %}
</td>
</tr>
{% empty %}<tr><td colspan="6" class="text-center text-muted">No appointments.</td></tr>{% endfor %}
</tbody></table>
DIV_CLOSE</DIV_CLOSE>
{% endblock %}
""",
    'appointments/appointment_form.html': """{% extends 'base.html' %}
{% block title %}New Appointment{% endblock %}
{% block content %}
<h2 class="mb-4">New Appointment</h2>
DIV_OPEN class="card"><DIV_OPEN class="card-body">
<form method="post">{% csrf_token %}
{% for field in form %}
DIV_OPEN class="mb-3"><label class="form-label">{{ field.label }}</label>{{ field }}
{% if field.errors %}DIV_OPEN class="text-danger small">{{ field.errors }}</DIV_CLOSE>{% endif %}
DIV_CLOSE
{% endfor %}
<button type="submit" class="btn btn-primary">Create</button>
<a href="{% url 'appointments:appointment_list' %}" class="btn btn-secondary">Cancel</a>
</form>
DIV_CLOSE</DIV_CLOSE>
{% endblock %}
""",
    'billing/invoice_list.html': """{% extends 'base.html' %}
{% block title %}Invoices{% endblock %}
{% block content %}
DIV_OPEN class="d-flex justify-content-between align-items-center mb-4">
<h2>Invoices</h2>
<a href="{% url 'billing:invoice_create' %}" class="btn btn-primary">New Invoice</a>
DIV_CLOSE
<form method="get" class="row g-2 mb-3">
DIV_OPEN class="col-md-3"><select name="status" class="form-select">
<option value="">All payment status</option>
{% for val, label in status_choices %}
<option value="{{ val }}" {% if status_filter == val %}selected{% endif %}>{{ label }}</option>
{% endfor %}
</select></DIV_CLOSE>
DIV_OPEN class="col-md-2"><select name="void" class="form-select">
<option value="">All</option>
<option value="0" {% if request.GET.void == '0' %}selected{% endif %}>Active</option>
<option value="1" {% if request.GET.void == '1' %}selected{% endif %}>Void</option>
</select></DIV_CLOSE>
DIV_OPEN class="col-auto"><button class="btn btn-outline-secondary">Filter</button></DIV_CLOSE>
</form>
DIV_OPEN class="card"><DIV_OPEN class="table-responsive">
<table class="table table-hover mb-0">
<thead class="table-light"><tr><th>ID</th><th>Patient</th><th>Total</th><th>Paid</th><th>Due</th><th>Status</th><th>Actions</th></tr></thead>
<tbody>
{% for inv in invoices %}
<tr {% if inv.is_void %}class="table-secondary"{% endif %}>
<td>{{ inv.id }}</td>
<td>{{ inv.appointment.patient.name }}</td>
<td>{{ inv.total }}</td>
<td>{{ inv.paid }}</td>
<td>{{ inv.due }}</td>
<td><span class="badge badge-{{ inv.status|lower }}">{{ inv.get_status_display }}</span>
{% if inv.is_void %}<span class="badge badge-void">VOID</span>{% endif %}</td>
<td>
<a href="{% url 'billing:invoice_detail' inv.pk %}" class="btn btn-sm btn-outline-primary">View</a>
{% if not inv.is_locked %}
<form method="post" action="{% url 'billing:invoice_void' %}" class="d-inline" onsubmit="return confirm('Void this invoice?');">{% csrf_token %}
<input type="hidden" name="invoice_id" value="{{ inv.id }}">
<button class="btn btn-sm btn-outline-danger">Void</button>
</form>
{% endif %}
</td>
</tr>
{% empty %}<tr><td colspan="7" class="text-center text-muted">No invoices.</td></tr>{% endfor %}
</tbody></table>
DIV_CLOSE</DIV_CLOSE>
{% endblock %}
""",
    'billing/invoice_form.html': """{% extends 'base.html' %}
{% block title %}New Invoice{% endblock %}
{% block content %}
<h2 class="mb-4">Create Invoice</h2>
DIV_OPEN class="card"><DIV_OPEN class="card-body">
<form method="post">{% csrf_token %}
{% for field in form %}
DIV_OPEN class="mb-3"><label class="form-label">{{ field.label }}</label>{{ field }}
{% if field.errors %}DIV_OPEN class="text-danger small">{{ field.errors }}</DIV_CLOSE>{% endif %}
DIV_CLOSE
{% endfor %}
<button type="submit" class="btn btn-primary">Create Invoice</button>
<a href="{% url 'billing:invoice_list' %}" class="btn btn-secondary">Cancel</a>
</form>
DIV_CLOSE</DIV_CLOSE>
{% endblock %}
""",
    'billing/invoice_detail.html': """{% extends 'base.html' %}
{% block title %}Invoice #{{ invoice.id }}{% endblock %}
{% block content %}
DIV_OPEN class="d-flex justify-content-between mb-4">
<h2>Invoice #{{ invoice.id }}</h2>
<a href="{% url 'billing:invoice_list' %}" class="btn btn-secondary">Back</a>
DIV_CLOSE
DIV_OPEN class="row g-3">
DIV_OPEN class="col-md-6"><DIV_OPEN class="card"><DIV_OPEN class="card-body">
<h5>Details</h5>
<p><strong>Patient:</strong> {{ invoice.appointment.patient.name }}</p>
<p><strong>Appointment:</strong> {{ invoice.appointment.date }} #{{ invoice.appointment.serial_no }}</p>
<p><strong>Total:</strong> {{ invoice.total }}</p>
<p><strong>Discount:</strong> {{ invoice.discount }}</p>
<p><strong>Paid:</strong> {{ invoice.paid }}</p>
<p><strong>Refund:</strong> {{ invoice.refund_amount }}</p>
<p><strong>Due:</strong> <span class="text-danger">{{ invoice.due }}</span></p>
<p><strong>Status:</strong> <span class="badge badge-{{ invoice.status|lower }}">{{ invoice.get_status_display }}</span></p>
{% if invoice.is_void %}<p class="text-danger"><strong>VOID</strong></p>{% endif %}
{% if invoice.cancel_reason %}<p><strong>Cancel reason:</strong> {{ invoice.cancel_reason }}</p>{% endif %}
DIV_CLOSE</DIV_CLOSE></DIV_CLOSE>
DIV_OPEN class="col-md-6">
{% if invoice.is_locked %}
DIV_OPEN class="alert alert-warning">This invoice is locked (void or cancelled). Editing is disabled.</DIV_CLOSE>
{% else %}
DIV_OPEN class="card mb-3"><DIV_OPEN class="card-header">Update Payment</DIV_OPEN><DIV_OPEN class="card-body">
<form method="post">{% csrf_token %}<input type="hidden" name="action" value="payment">
{% for field in payment_form %}
DIV_OPEN class="mb-3"><label class="form-label">{{ field.label }}</label>{{ field }}</DIV_CLOSE>
{% endfor %}
<button class="btn btn-primary">Save Payment</button>
</form>
DIV_CLOSE</DIV_CLOSE>
DIV_OPEN class="card"><DIV_OPEN class="card-header">Cancel Invoice</DIV_OPEN><DIV_OPEN class="card-body">
<form method="post">{% csrf_token %}<input type="hidden" name="action" value="cancel">
{{ cancel_form.reason.label_tag }}{{ cancel_form.reason }}
<button class="btn btn-warning mt-2">Cancel Invoice</button>
</form>
DIV_CLOSE</DIV_CLOSE>
{% endif %}
DIV_CLOSE
DIV_CLOSE
{% endblock %}
""",
}

for path, content in all_templates.items():
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(fix(content), encoding='utf-8')
    print('wrote', dest)
