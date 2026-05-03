"""
apps/accounts/views.py
----------------------
Login com 2FA, troca de filial, perfil e configuração de 2FA.
"""

import io
import base64
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.branches.models import Branch
from .models import CustomUser
from .permissions import admin_required, twofa_required


def _get_client_ip(request):
    x_forward = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forward:
        return x_forward.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            user_obj = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'accounts/login.html')

        if user_obj.is_locked():
            messages.error(request, 'Conta bloqueada temporariamente por excesso de tentativas. Tente em 15 minutos.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        if user is None:
            user_obj.register_failed_login()
            remaining = max(0, 5 - user_obj.failed_login_attempts)
            messages.error(request, f'Usuário ou senha inválidos. {remaining} tentativas restantes.')
            return render(request, 'accounts/login.html')

        user.reset_failed_login()
        user.last_login_ip = _get_client_ip(request)
        user.save(update_fields=['last_login_ip'])

        if user.totp_enabled:
            # Salva usuário em sessão pendente de 2FA
            request.session['pending_2fa_user_id'] = user.pk
            request.session['pending_2fa_next'] = request.GET.get('next', '')
            return redirect('accounts:twofa_verify')

        login(request, user)
        _set_branch_session(request, user)
        return redirect(request.GET.get('next', 'dashboard:index'))

    return render(request, 'accounts/login.html')


def twofa_verify(request):
    """Verifica o código TOTP após login com senha."""
    user_id = request.session.get('pending_2fa_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = get_object_or_404(CustomUser, pk=user_id, is_active=True)

    if request.method == 'POST':
        token = request.POST.get('token', '').replace(' ', '')
        if user.verify_totp(token):
            login(request, user)
            request.session['2fa_verified'] = True
            del request.session['pending_2fa_user_id']
            _set_branch_session(request, user)
            next_url = request.session.pop('pending_2fa_next', '') or 'dashboard:index'
            return redirect(next_url)
        else:
            messages.error(request, 'Código inválido. Tente novamente.')

    return render(request, 'accounts/twofa_verify.html', {'username': user.display_name})


@login_required
@twofa_required
def twofa_setup(request):
    """Configuração do 2FA para o usuário atual."""
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'generate':
            user.generate_totp_secret()
            messages.info(request, 'Escaneie o QR code com seu app autenticador.')
        elif action == 'activate':
            token = request.POST.get('token', '').replace(' ', '')
            if user.verify_totp(token):
                user.totp_enabled = True
                user.save(update_fields=['totp_enabled'])
                request.session['2fa_verified'] = True
                messages.success(request, '2FA ativado com sucesso!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Código inválido. Tente novamente.')
        elif action == 'deactivate':
            if not user.is_admin:
                # Apenas admins podem desativar sem token extra
                token = request.POST.get('token', '').replace(' ', '')
                if not user.verify_totp(token):
                    messages.error(request, 'Código inválido.')
                    return redirect('accounts:twofa_setup')
            user.totp_enabled = False
            user.totp_secret = ''
            user.save(update_fields=['totp_enabled', 'totp_secret'])
            messages.success(request, '2FA desativado.')
            return redirect('accounts:profile')

    qr_data = ''
    if user.totp_secret:
        uri = user.get_totp_uri()
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_data = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'accounts/twofa_setup.html', {
        'user': user,
        'qr_data': qr_data,
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def switch_branch(request, branch_id):
    user = request.user
    branch = get_object_or_404(Branch, id=branch_id, is_active=True)

    # Super admin: acesso total
    if user.is_super_admin:
        request.session['current_branch_id'] = branch.id
        messages.success(request, f'Filial alterada para {branch.name}')
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))

    # Admin: apenas sua filial
    if user.is_admin:
        if user.branch_id == branch.id:
            request.session['current_branch_id'] = branch.id
        else:
            messages.error(request, 'Acesso negado a essa filial.')
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))

    # Advogado: apenas sua filial principal
    lp = getattr(user, 'lawyer_profile', None)
    if lp:
        allowed = lp.branch_id == branch.id or lp.accessible_branches.filter(id=branch.id).exists()
        if allowed:
            request.session['current_branch_id'] = branch.id
            messages.success(request, f'Filial alterada para {branch.name}')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))

    messages.error(request, 'Acesso negado a essa filial.')
    return redirect('dashboard:index')


@login_required
@twofa_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.save(update_fields=['first_name', 'last_name', 'email', 'phone'])
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html')


def _set_branch_session(request, user):
    lawyer_profile = getattr(user, 'lawyer_profile', None)
    if lawyer_profile and lawyer_profile.branch:
        request.session['current_branch_id'] = lawyer_profile.branch_id
    elif user.branch:
        request.session['current_branch_id'] = user.branch_id
    elif user.is_super_admin:
        first = Branch.get_default_branch()
        if first:
            request.session['current_branch_id'] = first.id
