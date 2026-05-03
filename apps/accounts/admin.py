from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'branch', 'totp_enabled', 'is_active']
    list_filter = ['role', 'branch', 'is_active', 'totp_enabled']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil GB Advocacia', {'fields': ('role', 'branch', 'phone')}),
        ('Segurança 2FA', {'fields': ('totp_secret', 'totp_enabled', 'failed_login_attempts', 'locked_until', 'last_login_ip')}),
    )
    readonly_fields = ['last_login_ip', 'failed_login_attempts', 'locked_until']
    actions = ['reset_2fa', 'unlock_accounts']

    def reset_2fa(self, request, queryset):
        queryset.update(totp_enabled=False, totp_secret='')
        self.message_user(request, f'2FA resetado para {queryset.count()} usuários.')
    reset_2fa.short_description = 'Resetar 2FA dos usuários selecionados'

    def unlock_accounts(self, request, queryset):
        queryset.update(failed_login_attempts=0, locked_until=None)
        self.message_user(request, f'{queryset.count()} contas desbloqueadas.')
    unlock_accounts.short_description = 'Desbloquear contas selecionadas'
