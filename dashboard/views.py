from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/client_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='default').exists():
            messages.error(request, "You are not authorized to access this page.")
            return redirect('base:index')
        return super().dispatch(request, *args, **kwargs)


class ManagerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/manager_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='manager').exists():
            messages.error(request, "You are not authorized to access this page.")
            return redirect('base:index')
        return super().dispatch(request, *args, **kwargs)


