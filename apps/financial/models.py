from django.db import models
from simple_history.models import HistoricalRecords


class Transaction(models.Model):
    TYPE_RECEITA = 'receita'
    TYPE_DESPESA = 'despesa'
    TYPE_CHOICES = [(TYPE_RECEITA, 'Receita'), (TYPE_DESPESA, 'Despesa')]

    STATUS_PENDENTE = 'pendente'
    STATUS_PAGO = 'pago'
    STATUS_VENCIDO = 'vencido'
    STATUS_CANCELADO = 'cancelado'
    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'), (STATUS_PAGO, 'Pago'),
        (STATUS_VENCIDO, 'Vencido'), (STATUS_CANCELADO, 'Cancelado'),
    ]

    CATEGORY_CHOICES_RECEITA = [
        ('honorarios', 'Honorários'), ('consulta', 'Consulta'),
        ('sucumbencia', 'Sucumbência'), ('acordo', 'Acordo'), ('outro', 'Outro'),
    ]
    CATEGORY_CHOICES_DESPESA = [
        ('aluguel', 'Aluguel'), ('salario', 'Salário'), ('custas', 'Custas Judiciais'),
        ('material', 'Material de Escritório'), ('servicos', 'Serviços'), ('outro', 'Outro'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Tipo')
    category = models.CharField(max_length=100, verbose_name='Categoria')
    description = models.TextField(blank=True, default='', verbose_name='Descrição')
    value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    due_date = models.DateField(verbose_name='Vencimento')
    payment_date = models.DateField(null=True, blank=True, verbose_name='Data de Pagamento')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDENTE, verbose_name='Status')
    client = models.ForeignKey('clients.Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Cliente')
    process = models.ForeignKey('processes.Process', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Processo')
    notes = models.TextField(blank=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords(excluded_fields=[
        'payment_date',
        'client',
        'process',
        'notes',
    ])

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.get_type_display()} - {self.description[:50]} - R$ {self.value}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        from datetime import date
        if self.status == self.STATUS_PENDENTE and isinstance(self.due_date, date) and self.due_date < timezone.now().date():
            self.status = self.STATUS_VENCIDO
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        from django.utils import timezone
        from datetime import date
        return self.status == self.STATUS_PENDENTE and isinstance(self.due_date, date) and self.due_date < timezone.now().date()
