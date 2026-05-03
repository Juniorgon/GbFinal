"""
apps/documents/views.py
-----------------------
Módulo removido conforme solicitação.
As rotas não existem mais no config/urls.py.
Este arquivo existe apenas para não quebrar imports históricos.
"""
from django.http import Http404

def document_list(request):
    raise Http404

def document_upload(request):
    raise Http404

def document_delete(request, pk):
    raise Http404

def document_download(request, pk):
    raise Http404
