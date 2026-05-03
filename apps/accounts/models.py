from django.contrib.auth.models import AbstractUser
from django.db import models
import pyotp


class CustomUser(AbstractUser):
    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_ADMIN = 'admin'
    ROLE_LAWYER = 'lawyer'
    ROLE_SECRETARY = 'secretary'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Administrador'),
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_LAWYER, 'Advogado'),
        (ROLE_SECRETARY, 'Secretário(a)'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ADMIN)
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Filial',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')

    # 2FA
    totp_secret = models.CharField(max_length=64, blank=True, verbose_name='Segredo TOTP')
    totp_enabled = models.BooleanField(default=False, verbose_name='2FA Ativado')

    # Security / brute-force
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_admin(self):
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    def get_totp_uri(self):
        if not self.totp_secret:
            return ''
        return pyotp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email or self.username,
            issuer_name='GB & N.Comin Advocacia',
        )

    def generate_totp_secret(self):
        self.totp_secret = pyotp.random_base32()
        self.save(update_fields=['totp_secret'])
        return self.totp_secret

    def verify_totp(self, token):
        if not self.totp_secret:
            return False
        return pyotp.TOTP(self.totp_secret).verify(str(token).strip(), valid_window=1)

    def is_locked(self):
        from django.utils import timezone

        return bool(self.locked_until and self.locked_until > timezone.now())

    def register_failed_login(self):
        from datetime import timedelta
        from django.utils import timezone

        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
