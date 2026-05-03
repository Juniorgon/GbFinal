from django.db import models
from simple_history.models import HistoricalRecords


class Process(models.Model):
    STATUS_ANDAMENTO = 'andamento'
    STATUS_CONCLUIDO = 'concluido'
    STATUS_SUSPENSO = 'suspenso'
    STATUS_ARQUIVADO = 'arquivado'
    STATUS_CHOICES = [
        (STATUS_ANDAMENTO, 'Em Andamento'),
        (STATUS_CONCLUIDO, 'Concluído'),
        (STATUS_SUSPENSO, 'Suspenso'),
        (STATUS_ARQUIVADO, 'Arquivado'),
    ]

    TYPE_CHOICES = [
        ('civil', 'Cível'), ('trabalhista', 'Trabalhista'), ('criminal', 'Criminal'),
        ('familia', 'Família'), ('previdenciario', 'Previdenciário'), ('tributario', 'Tributário'),
        ('empresarial', 'Empresarial'), ('administrativo', 'Administrativo'), ('outro', 'Outro'),
    ]

    POSITION_CHOICES = [
        ('autor', 'Credor (Autor)'), ('reu', 'Devedor (Réu)'),
        ('terceiro', 'Terceiro Interessado'), ('outro', 'Outro'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='processes')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='processes', verbose_name='Cliente')
    lawyer = models.ForeignKey('lawyers.Lawyer', on_delete=models.SET_NULL, null=True, blank=True, related_name='processes', verbose_name='Advogado')
    number = models.CharField(max_length=50, verbose_name='Número do Processo', blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    custom_type = models.CharField(max_length=100, blank=True, verbose_name='Outro Tipo de Processo')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ANDAMENTO, verbose_name='Status')
    client_position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='autor', verbose_name='Posição do Cliente')
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor da Causa')
    description = models.TextField(blank=True, default='', verbose_name='Descrição')
    court = models.CharField(max_length=200, blank=True, verbose_name='Vara/Tribunal')
    opposing_party = models.CharField(max_length=200, blank=True, verbose_name='Parte Contrária')
    notes = models.TextField(blank=True, default='', verbose_name='Observações')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords(excluded_fields=[
        'client_position',
        'description',
        'court',
        'opposing_party',
        'notes',
        'lawyer',
    ])

    class Meta:
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number or 'S/N'} - {self.client.name}"

    @property
    def status_color(self):
        colors = {
            self.STATUS_ANDAMENTO: 'warning',
            self.STATUS_CONCLUIDO: 'success',
            self.STATUS_SUSPENSO: 'danger',
            self.STATUS_ARQUIVADO: 'secondary',
        }
        return colors.get(self.status, 'secondary')

    @property
    def type_label(self):
        if self.type == 'outro' and self.custom_type:
            return self.custom_type
        return self.get_type_display()


class ProcessUpdate(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='updates')
    date = models.DateField(verbose_name='Data')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, default='', verbose_name='Descrição')
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Andamento'
        verbose_name_plural = 'Andamentos'
        ordering = ['-date']

    def __str__(self):
        return f"{self.process} - {self.title}"
