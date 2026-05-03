from django.db import models
from simple_history.models import HistoricalRecords


class Contract(models.Model):
    TYPE_CHOICES = [
        ('honorarios', 'Honorários Advocatícios'),
        ('prestacao_servicos', 'Prestação de Serviços'),
        ('consultoria', 'Consultoria Jurídica'),
        ('retainer', 'Contrato de Retainer'),
        ('sucumbencia', 'Honorários de Sucumbência'),
        ('outro', 'Outro'),
    ]
    STATUS_ATIVO = 'ativo'
    STATUS_CONCLUIDO = 'concluido'
    STATUS_SUSPENSO = 'suspenso'
    STATUS_CANCELADO = 'cancelado'
    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'), (STATUS_CONCLUIDO, 'Concluído'),
        (STATUS_SUSPENSO, 'Suspenso'), (STATUS_CANCELADO, 'Cancelado'),
    ]
    JUDICIAL_CHOICES = [
        ('judicial', 'Judicial'), ('extrajudicial', 'Extrajudicial'), ('ambos', 'Ambos'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='contracts')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='contracts', verbose_name='Cliente')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Tipo de Contrato')
    custom_type = models.CharField(max_length=100, blank=True, verbose_name='Outro Tipo de Contrato')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, default='', verbose_name='Descrição Detalhada')
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor Total (R$)')
    installments = models.PositiveIntegerField(default=1, verbose_name='Número de Parcelas')
    payment_conditions = models.TextField(verbose_name='Condições de Pagamento')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ATIVO, verbose_name='Status')
    judicial_type = models.CharField(max_length=15, choices=JUDICIAL_CHOICES, default='judicial', verbose_name='Judicial/Extrajudicial')
    start_date = models.DateField(verbose_name='Data de Início')
    end_date = models.DateField(verbose_name='Data de Término')
    notes = models.TextField(blank=True, verbose_name='Observações Adicionais')
    process = models.ForeignKey('processes.Process', on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts', verbose_name='Processo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords(excluded_fields=[
        'description',
        'installments',
        'payment_conditions',
        'judicial_type',
        'notes',
        'process',
    ])

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.client.name}"

    @property
    def is_expiring_soon(self):
        from django.utils import timezone
        import datetime
        return self.end_date and (self.end_date - timezone.now().date()).days <= 30 and self.status == self.STATUS_ATIVO

    @property
    def installment_value(self):
        if self.installments and self.installments > 0:
            return self.total_value / self.installments
        return self.total_value

    @property
    def type_label(self):
        if self.type == 'outro' and self.custom_type:
            return self.custom_type
        return self.get_type_display()
