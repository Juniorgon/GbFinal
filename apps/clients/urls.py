from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('novo/', views.client_create, name='create'),
    path('<int:pk>/editar/', views.client_edit, name='edit'),
    path('<int:pk>/excluir/', views.client_delete, name='delete'),
    path('<int:pk>/detalhe/', views.client_detail, name='detail'),
    path('<int:pk>/procuracao/', views.generate_procuracao, name='procuracao'),
    path('exportar/pdf/', views.export_pdf, name='export_pdf'),
    path('exportar/excel/', views.export_excel, name='export_excel'),
]
