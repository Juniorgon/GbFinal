from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('clientes/', include('apps.clients.urls')),
    path('processos/', include('apps.processes.urls')),
    path('financeiro/', include('apps.financial.urls')),
    path('contratos/', include('apps.contracts.urls')),
    path('tarefas/', include('apps.tasks.urls')),
    # documentos removido conforme solicitação
    path('advogados/', include('apps.lawyers.urls')),
    path('filiais/', include('apps.branches.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'GB & N.Comin Advocacia — Admin'
admin.site.site_title = 'Advocacia Admin'
admin.site.index_title = 'Painel Administrativo'
