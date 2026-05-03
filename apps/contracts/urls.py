from django.urls import path
from . import views
app_name = 'contracts'
urlpatterns = [
    path('', views.contract_list, name='list'),
    path('novo/', views.contract_create, name='create'),
    path('<int:pk>/editar/', views.contract_edit, name='edit'),
    path('<int:pk>/excluir/', views.contract_delete, name='delete'),
    path('exportar/pdf/', views.export_pdf, name='export_pdf'),
    path('exportar/excel/', views.export_excel, name='export_excel'),
]
