from django.urls import path
from . import views

app_name = 'processes'

urlpatterns = [
    path('', views.process_list, name='list'),
    path('novo/', views.process_create, name='create'),
    path('<int:pk>/editar/', views.process_edit, name='edit'),
    path('<int:pk>/excluir/', views.process_delete, name='delete'),
    path('<int:pk>/detalhe/', views.process_detail, name='detail'),
    path('gerar-numero/', views.generate_number, name='generate_number'),
    path('exportar/pdf/', views.export_pdf, name='export_pdf'),
]
