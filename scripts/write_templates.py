"""Generate remaining HTML templates."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'templates'

TEMPLATES = {
    'patients/patient_list.html': r'''{% extends 'base.html' %}
{% block title %}Patients - Clinic PMS{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2>Patients</h2>
    <a href="{% url 'patients:patient_create' %}" class="btn btn-primary">Add Patient</a>
</motion>

<form method="get" class="row g-2 mb-3">
    <div class="col-md-8">
        <input type="text" name="q" value="{{ query }}" class="form-control"
               placeholder="Search by name, phone, or ID">
    </div>
    <div class="col-auto">
        <button type="submit" class="btn btn-outline-secondary">Search</button>
        {% if query %}<a href="{% url 'patients:patient_list' %}" class="btn btn-link">Clear</a>{% endif %}
    </div>
</form>

<div class="card">
    <motion class="table-responsive">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th>ID</th><th>Name</th><th>Phone</th><th>Age</th>
                    <th>Gender</th><th>Registered</th><th>Actions</th>
                </tr>
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
    </motion>
</div>
{% endblock %}
''',
}

# Fix motion in template strings before writing
for path, content in TEMPLATES.items():
    content = content.replace('<motion', '<div').replace('</motion>', '</div>')
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding='utf-8')
    print('wrote', dest)
