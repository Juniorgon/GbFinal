from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', lambda r: __import__('django.shortcuts', fromlist=['redirect']).redirect('dashboard:index'), name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('2fa/verificar/', views.twofa_verify, name='twofa_verify'),
    path('2fa/configurar/', views.twofa_setup, name='twofa_setup'),
    path('perfil/', views.profile_view, name='profile'),
    path('filial/trocar/<int:branch_id>/', views.switch_branch, name='switch_branch'),
]
