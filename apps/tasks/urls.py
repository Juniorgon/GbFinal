from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('agenda/', views.agenda, name='agenda'),
    path('agenda/compromissos/<int:pk>/excluir/', views.appointment_delete, name='appointment_delete'),
    path('nova/', views.task_create, name='create'),
    path('<int:pk>/editar/', views.task_edit, name='edit'),
    path('<int:pk>/concluir/', views.task_mark_done, name='mark_done'),
    path('<int:pk>/validar/', views.task_validate, name='validate'),
    path('<int:pk>/excluir/', views.task_delete, name='delete'),
]
