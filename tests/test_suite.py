from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.appointments.models import Appointment
from apps.billing.models import Invoice
from apps.patients.models import Patient

User = get_user_model()


class LoggedInTestCase(TestCase):
    """Staff user with full clinic access for view tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True,
        )
        UserProfile.objects.filter(user=cls.user).update(role=UserProfile.ROLE_ADMIN)

    def setUp(self):
        self.client.force_login(self.user)


class PatientManagementTests(LoggedInTestCase):
    def setUp(self):
        super().setUp()
        self.patient = Patient.objects.create(
            name='John Doe', phone='01700000000', age=30, gender='M',
        )

    def test_patient_create_and_list(self):
        response = self.client.get(reverse('patients:patient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_patient_search_by_name(self):
        response = self.client.get(reverse('patients:patient_list'), {'q': 'John'})
        self.assertContains(response, 'John Doe')

    def test_patient_search_by_id(self):
        response = self.client.get(
            reverse('patients:patient_list'),
            {'q': str(self.patient.pk)},
        )
        self.assertContains(response, 'John Doe')

    def test_patient_update_form(self):
        response = self.client.post(
            reverse('patients:patient_edit', args=[self.patient.pk]),
            {'name': 'Jane Doe', 'phone': '01711111111', 'age': 31, 'gender': 'F', 'address': ''},
        )
        self.assertEqual(response.status_code, 302)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.name, 'Jane Doe')


class AppointmentTests(LoggedInTestCase):
    def setUp(self):
        super().setUp()
        self.patient = Patient.objects.create(
            name='Ali', phone='01800000000', age=25, gender='M',
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            date=date.today(),
            serial_no=1,
            status=Appointment.STATUS_PENDING,
        )

    def test_status_workflow(self):
        self.assertEqual(self.appointment.status, Appointment.STATUS_PENDING)
        self.appointment.advance_status()
        self.assertEqual(self.appointment.status, Appointment.STATUS_WAITING)
        self.appointment.advance_status()
        self.assertEqual(self.appointment.status, Appointment.STATUS_DONE)

    def test_status_filter(self):
        response = self.client.get(
            reverse('appointments:appointment_list'),
            {'status': Appointment.STATUS_PENDING},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ali')


class InvoiceTests(LoggedInTestCase):
    def setUp(self):
        super().setUp()
        patient = Patient.objects.create(
            name='Sara', phone='01900000000', age=28, gender='F',
        )
        appointment = Appointment.objects.create(
            patient=patient, date=date.today(), serial_no=1,
        )
        self.invoice = Invoice.objects.create(
            appointment=appointment,
            total=Decimal('1000.00'),
            discount=Decimal('100.00'),
            paid=Decimal('400.00'),
        )

    def test_invoice_due_calculation(self):
        self.assertEqual(self.invoice.due, Decimal('500.00'))
        self.assertEqual(self.invoice.status, Invoice.STATUS_PARTIAL)

    def test_void_prevents_payment_edit(self):
        self.invoice.void()
        response = self.client.post(
            reverse('billing:invoice_detail', args=[self.invoice.pk]),
            {
                'action': 'payment',
                'paid': '900.00',
                'discount': '100.00',
                'refund_amount': '0.00',
            },
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.paid, Decimal('400.00'))

    def test_refund_cannot_exceed_paid(self):
        inv = Invoice(
            appointment=self.invoice.appointment,
            total=Decimal('100'),
            paid=Decimal('50'),
            refund_amount=Decimal('60'),
        )
        with self.assertRaises(Exception):
            inv.full_clean()


class DashboardTests(LoggedInTestCase):
    def test_dashboard_loads(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class LoginPageTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
