from django.urls import path
from . import views
app_name = 'branches'
urlpatterns = [
    path("trocar-filial/", views.switch_branch, name="switch_branch"),
]