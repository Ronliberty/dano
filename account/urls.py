from django.urls import path
from . import views
from .views import role_based_redirect

app_name = 'account'
urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('account/', views.accountSettings, name="account"),
    path('role-based-redirect/', role_based_redirect, name='role_based_redirect'),

    ]