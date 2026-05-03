from django.urls import path
from . import views
app_name = 'lawyers'
urlpatterns = [
    path('', views.lawyer_list, name='list'),
    path('registrar/', views.lawyer_create, name='create'),
    path('<int:pk>/editar/', views.lawyer_edit, name='edit'),
    path('<int:pk>/toggle/', views.lawyer_toggle, name='toggle'),
    path('<int:pk>/excluir/', views.lawyer_delete, name='delete'),
    path('exportar/pdf/', views.export_pdf, name='export_pdf'),
    path('exportar/excel/', views.export_excel, name='export_excel'),
]
