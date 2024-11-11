from django.urls import path
from .views import ManagerDashboardView, ClientDashboardView


app_name = 'dashboard'
urlpatterns = [
    path('manager_dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('client_dashboard/', ClientDashboardView.as_view(), name='client_dashboard'),


]