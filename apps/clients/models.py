from django.db import models
from simple_history.models import HistoricalRecords


class Client(models.Model):
    TYPE_FISICA = 'fisica'
    TYPE_JURIDICA = 'juridica'
    TYPE_CHOICES = [
        (TYPE_FISICA, 'Pessoa Física'),
        (TYPE_JURIDICA, 'Pessoa Jurídica'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='clients', verbose_name='Filial')
    name = models.CharField(max_length=200, verbose_name='Nome Completo')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_FISICA, verbose_name='Tipo')
    cpf_cnpj = models.CharField(max_length=20, verbose_name='CPF/CNPJ', blank=True)
    nationality = models.CharField(max_length=50, blank=True, default='Brasileira', verbose_name='Nacionalidade')
    marital_status = models.CharField(max_length=50, blank=True, verbose_name='Estado Civil')
    profession = models.CharField(max_length=100, blank=True, verbose_name='Profissão')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    phone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='Email')
    # Address
    street = models.CharField(max_length=200, blank=True, verbose_name='Rua')
    number = models.CharField(max_length=10, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    district = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    state = models.CharField(max_length=2, blank=True, verbose_name='Estado')
    zipcode = models.CharField(max_length=10, blank=True, verbose_name='CEP')
    # Metadata
    notes = models.TextField(blank=True, verbose_name='Observações')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords(excluded_fields=[
        'nationality',
        'marital_status',
        'profession',
        'birth_date',
        'email',
        'street',
        'number',
        'complement',
        'district',
        'zipcode',
        'notes',
    ])

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def city_state(self):
        if self.city and self.state:
            return f"{self.city}/{self.state}"
        return self.city or self.state or '-'

    @property
    def process_count(self):
        return self.processes.filter(is_active=True).count()

    @property
    def type_display_short(self):
        return 'P. Jurídica' if self.type == self.TYPE_JURIDICA else 'P. Física'
