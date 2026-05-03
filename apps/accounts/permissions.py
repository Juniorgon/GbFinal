"""
apps/accounts/permissions.py
----------------------------
Permissões centralizadas do sistema GB & N.Comin Advocacia.

Todas as verificações são feitas no backend.
Nunca confiar apenas em esconder elementos no frontend.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _get_branch(request):
    """Retorna a filial atual da request (set pelo BranchMiddleware)."""
    return getattr(request, 'current_branch', None) or getattr(request.user, 'branch', None)


def _user_can_access_branch(user, branch):
    """
    Retorna True se o usuário pode acessar a filial dada.
    Super admin: todas. Admin: sua filial. Advogado: filial principal e filiais liberadas.
    """
    if not user.is_authenticated or not branch:
        return False
    if user.is_super_admin:
        return True
    if user.is_admin:
        return user.branch_id == branch.id
    # Advogado / Secretário
    if hasattr(user, 'lawyer_profile') and user.lawyer_profile:
        lp = user.lawyer_profile
        return lp.branch_id == branch.id or lp.accessible_branches.filter(id=branch.id).exists()
    return user.branch_id == branch.id


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def admin_required(view_func):
    """Apenas admins e super admins podem acessar."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, 'Acesso negado. Apenas administradores.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped


def super_admin_required(view_func):
    """Apenas super admins podem acessar."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_super_admin:
            messages.error(request, 'Acesso negado. Apenas Super Administradores.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped


def branch_access_required(view_func):
    """Garante que o usuário tem acesso à filial atual."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        branch = _get_branch(request)
        if not branch:
            messages.error(request, 'Nenhuma filial associada. Contate o administrador.')
            return redirect('accounts:login')
        if not _user_can_access_branch(request.user, branch):
            messages.error(request, 'Acesso negado a esta filial.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped


def financial_edit_required(view_func):
    """Financeiro: leitura para todos, edição apenas para admins."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, 'Apenas administradores podem modificar registros financeiros.')
            return redirect('financial:list')
        return view_func(request, *args, **kwargs)
    return _wrapped


def twofa_required(view_func):
    """Garante que o 2FA foi completado na sessão atual."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.totp_enabled and not request.session.get('2fa_verified'):
            return redirect('accounts:twofa_verify')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ---------------------------------------------------------------------------
# Utilitários para queries com isolamento de filial
# ---------------------------------------------------------------------------

def branch_queryset(model, request, extra_filters=None):
    """
    Retorna um queryset do model filtrado pela filial atual do request.
    Lança PermissionDenied se não houver filial acessível.
    extra_filters: dict adicional de filtros
    """
    branch = _get_branch(request)
    if not branch:
        raise PermissionDenied("Nenhuma filial associada.")
    if not _user_can_access_branch(request.user, branch):
        raise PermissionDenied("Sem acesso a esta filial.")
    filters = {'branch': branch}
    if extra_filters:
        filters.update(extra_filters)
    return model.objects.filter(**filters)


def get_branch_object_or_403(model, request, **kwargs):
    """
    Equivalente a get_object_or_404 mas também verifica isolamento de filial.
    """
    branch = _get_branch(request)
    if not branch or not _user_can_access_branch(request.user, branch):
        raise PermissionDenied("Sem acesso a esta filial.")
    try:
        return model.objects.get(branch=branch, **kwargs)
    except model.DoesNotExist:
        raise Http404
