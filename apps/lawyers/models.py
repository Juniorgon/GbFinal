from django.db import models


class Lawyer(models.Model):
    ESTADO_CHOICES = [
        ('AC','AC'),('AL','AL'),('AP','AP'),('AM','AM'),('BA','BA'),('CE','CE'),
        ('DF','DF'),('ES','ES'),('GO','GO'),('MA','MA'),('MT','MT'),('MS','MS'),
        ('MG','MG'),('PA','PA'),('PB','PB'),('PR','PR'),('PE','PE'),('PI','PI'),
        ('RJ','RJ'),('RN','RN'),('RS','RS'),('RO','RO'),('RR','RR'),('SC','SC'),
        ('SP','SP'),('SE','SE'),('TO','TO'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='lawyers')
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='lawyer_profile')
    name = models.CharField(max_length=200, verbose_name='Nome Completo')
    email = models.EmailField(verbose_name='Email')
    oab_number = models.CharField(max_length=20, verbose_name='Número OAB')
    oab_state = models.CharField(max_length=2, choices=ESTADO_CHOICES, default='RS', verbose_name='Estado OAB')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    specialization = models.CharField(max_length=200, blank=True, verbose_name='Especialização')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    accessible_branches = models.ManyToManyField(
        'branches.Branch',
        blank=True,
        related_name='accessible_lawyers',
        verbose_name='Filiais com Acesso',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Advogado'
        verbose_name_plural = 'Advogados'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - OAB {self.oab_number}/{self.oab_state}"

    @property
    def oab_display(self):
        return f"{self.oab_number}/{self.oab_state}"
