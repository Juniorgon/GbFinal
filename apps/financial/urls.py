from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.transaction_list, name='list'),
    path('nova/', views.transaction_create, name='create'),
    path('<int:pk>/editar/', views.transaction_edit, name='edit'),
    path('<int:pk>/excluir/', views.transaction_delete, name='delete'),
    path('exportar/pdf/', views.export_pdf, name='export_pdf'),
]
