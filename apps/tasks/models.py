from django.db import models
from simple_history.models import HistoricalRecords


class Task(models.Model):
    PRIORITY_ALTA = 'alta'
    PRIORITY_MEDIA = 'media'
    PRIORITY_BAIXA = 'baixa'
    PRIORITY_CHOICES = [
        (PRIORITY_ALTA, 'Alta'), (PRIORITY_MEDIA, 'Média'), (PRIORITY_BAIXA, 'Baixa'),
    ]

    STATUS_PENDENTE = 'pendente'
    STATUS_EM_ANDAMENTO = 'andamento'
    # Lawyer marks done → awaits admin validation
    STATUS_AGUARDANDO = 'aguardando'
    STATUS_CONCLUIDA = 'concluida'
    STATUS_CANCELADA = 'cancelada'

    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_EM_ANDAMENTO, 'Em Andamento'),
        (STATUS_AGUARDANDO, 'Aguardando Validação'),
        (STATUS_CONCLUIDA, 'Concluída'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]

    TYPE_CHOICES = [
        ('audiencia', 'Audiência'), ('prazo', 'Prazo'), ('reuniao', 'Reunião'),
        ('protocolo', 'Protocolo'), ('ligacao', 'Ligação'), ('outro', 'Outro'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, verbose_name='Título')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='outro', verbose_name='Tipo')
    custom_type = models.CharField(max_length=100, blank=True, verbose_name='Outro Tipo de Tarefa')
    description = models.TextField(blank=True, default='', verbose_name='Descrição')
    due_date = models.DateField(verbose_name='Data de Vencimento')
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIA, verbose_name='Prioridade')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDENTE, verbose_name='Status')

    assigned_to = models.ForeignKey(
        'lawyers.Lawyer', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks', verbose_name='Advogado Responsável'
    )
    client = models.ForeignKey(
        'clients.Client', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks', verbose_name='Cliente'
    )
    process = models.ForeignKey(
        'processes.Process', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks', verbose_name='Processo'
    )

    # Dual-confirmation fields
    completed_by = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks_completed', verbose_name='Concluída por'
    )
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Data de Conclusão')
    validated_by = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks_validated', verbose_name='Validada por'
    )
    validated_at = models.DateTimeField(null=True, blank=True, verbose_name='Data de Validação')
    completion_note = models.TextField(blank=True, verbose_name='Nota de Conclusão')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks_created'
    )
    history = HistoricalRecords(excluded_fields=[
        'description',
        'client',
        'process',
        'completed_by',
        'completed_at',
        'validated_by',
        'validated_at',
        'completion_note',
    ])

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['due_date', '-priority']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        from datetime import date
        if not isinstance(self.due_date, date):
            return False
        return self.status == self.STATUS_PENDENTE and self.due_date < timezone.now().date()

    @property
    def priority_color(self):
        return {'alta': 'danger', 'media': 'warning', 'baixa': 'success'}.get(self.priority, 'secondary')

    @property
    def status_color(self):
        return {
            self.STATUS_PENDENTE: 'warning',
            self.STATUS_EM_ANDAMENTO: 'info',
            self.STATUS_AGUARDANDO: 'purple',
            self.STATUS_CONCLUIDA: 'success',
            self.STATUS_CANCELADA: 'secondary',
        }.get(self.status, 'secondary')

    @property
    def type_label(self):
        if self.type == 'outro' and self.custom_type:
            return self.custom_type
        return self.get_type_display()

    def can_be_completed_by(self, user):
        """Advogado responsável ou admin pode marcar como aguardando validação."""
        if user.is_admin:
            return True
        lp = getattr(user, 'lawyer_profile', None)
        return lp and self.assigned_to_id == lp.id

    def can_be_validated_by(self, user):
        """Apenas admins podem validar a conclusão."""
        return user.is_admin


class PersonalAppointment(models.Model):
    owner = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='personal_appointments',
        verbose_name='Usuario',
    )
    title = models.CharField(max_length=200, verbose_name='Titulo')
    description = models.TextField(blank=True, default='', verbose_name='Descricao')
    date = models.DateField(verbose_name='Data')
    start_time = models.TimeField(null=True, blank=True, verbose_name='Horario Inicial')
    end_time = models.TimeField(null=True, blank=True, verbose_name='Horario Final')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Compromisso pessoal'
        verbose_name_plural = 'Compromissos pessoais'
        ordering = ['date', 'start_time', 'title']

    def __str__(self):
        return self.title
