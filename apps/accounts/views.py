from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View

from .forms import ClinicLoginForm


class ClinicLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = ClinicLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


class ClinicLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been signed out.')
        return redirect('accounts:login')

    def post(self, request):
        return self.get(request)
