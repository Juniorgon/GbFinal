"""
apps/tasks/views.py
-------------------
Tarefas com dupla confirmacao:
  1. Advogado responsavel marca como "Aguardando Validacao"
  2. Administrador valida -> status "Concluida"

Permissoes reforcadas no backend.
"""

from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.accounts.permissions import get_branch_object_or_403
from apps.clients.models import Client
from apps.lawyers.models import Lawyer
from apps.processes.models import Process

from .models import PersonalAppointment, Task


def get_branch(request):
    return getattr(request, 'current_branch', None) or request.user.branch


def get_task_type_data(request):
    task_type = request.POST.get('type', 'outro')
    custom_type = request.POST.get('custom_type', '').strip()
    if task_type == 'outro' and not custom_type:
        raise ValueError('Informe o novo tipo de tarefa.')
    if task_type != 'outro':
        custom_type = ''
    return task_type, custom_type


def get_current_lawyer(user):
    lawyer = getattr(user, 'lawyer_profile', None)
    if not lawyer:
        raise Http404
    return lawyer


def parse_agenda_date(value):
    if not value:
        return timezone.localdate()
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return timezone.localdate()


def week_days_for(reference_date):
    days_since_sunday = (reference_date.weekday() + 1) % 7
    start = reference_date - timedelta(days=days_since_sunday)
    return [start + timedelta(days=i) for i in range(7)]


@login_required
def agenda(request):
    lawyer = get_current_lawyer(request.user)
    selected_date = parse_agenda_date(request.GET.get('date'))
    days = week_days_for(selected_date)
    start_date, end_date = days[0], days[-1]

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        date = request.POST.get('date', '')
        if not title or not date:
            messages.error(request, 'Informe o titulo e a data do compromisso.')
            return redirect(f"{request.path}?date={selected_date.isoformat()}")

        PersonalAppointment.objects.create(
            owner=request.user,
            title=title,
            description=request.POST.get('description', '').strip(),
            date=date,
            start_time=request.POST.get('start_time') or None,
            end_time=request.POST.get('end_time') or None,
        )
        messages.success(request, 'Compromisso adicionado a sua agenda.')
        return redirect(f"{request.path}?date={date}")

    tasks = Task.objects.filter(
        assigned_to=lawyer,
        due_date__range=(start_date, end_date),
    ).select_related('client', 'process').order_by('due_date', '-priority', 'title')
    appointments = PersonalAppointment.objects.filter(
        owner=request.user,
        date__range=(start_date, end_date),
    ).order_by('date', 'start_time', 'title')

    tasks_by_day = {day: [] for day in days}
    appointments_by_day = {day: [] for day in days}
    for task in tasks:
        tasks_by_day.setdefault(task.due_date, []).append(task)
    for appointment in appointments:
        appointments_by_day.setdefault(appointment.date, []).append(appointment)

    today = timezone.localdate()
    context_days = [
        {
            'date': day,
            'tasks': tasks_by_day.get(day, []),
            'appointments': appointments_by_day.get(day, []),
            'is_today': day == today,
        }
        for day in days
    ]

    all_week_tasks = list(tasks)
    context = {
        'days': context_days,
        'selected_date': selected_date,
        'prev_week': (start_date - timedelta(days=7)).isoformat(),
        'next_week': (start_date + timedelta(days=7)).isoformat(),
        'total_tasks': len(all_week_tasks),
        'pending_tasks': len([t for t in all_week_tasks if t.status in (Task.STATUS_PENDENTE, Task.STATUS_EM_ANDAMENTO, Task.STATUS_AGUARDANDO)]),
        'overdue_tasks': len([t for t in all_week_tasks if t.status == Task.STATUS_PENDENTE and t.due_date < today]),
        'done_tasks': len([t for t in all_week_tasks if t.status == Task.STATUS_CONCLUIDA]),
        'total_appointments': appointments.count(),
    }
    return render(request, 'tasks/agenda.html', context)


@login_required
def appointment_delete(request, pk):
    appointment = PersonalAppointment.objects.filter(pk=pk, owner=request.user).first()
    if not appointment:
        raise Http404
    agenda_date = appointment.date.isoformat()
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Compromisso removido da agenda.')
    return redirect(f"{reverse('tasks:agenda')}?date={agenda_date}")


@login_required
def task_list(request):
    branch = get_branch(request)
    lawyers = Lawyer.objects.filter(branch=branch, is_active=True)
    qs = Task.objects.filter(branch=branch).select_related(
        'client', 'assigned_to', 'process', 'completed_by', 'validated_by'
    )

    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')

    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)

    if not request.user.is_admin:
        lp = getattr(request.user, 'lawyer_profile', None)
        if lp:
            qs = qs.filter(assigned_to=lp)

    pending_validation = Task.objects.filter(branch=branch, status=Task.STATUS_AGUARDANDO).count()

    return render(request, 'tasks/list.html', {
        'tasks': qs,
        'status': status,
        'priority': priority,
        'pending_validation': pending_validation,
        'priority_choices': Task.PRIORITY_CHOICES,
        'status_choices': Task.STATUS_CHOICES,
        'type_choices': Task.TYPE_CHOICES,
        'lawyers': lawyers,
    })


@login_required
def task_create(request):
    branch = get_branch(request)
    clients = Client.objects.filter(branch=branch, is_active=True)
    processes = Process.objects.filter(branch=branch, is_active=True)
    lawyers = Lawyer.objects.filter(branch=branch, is_active=True)

    if request.method == 'POST':
        try:
            task_type, custom_type = get_task_type_data(request)
            task = Task(
                branch=branch,
                title=request.POST.get('title', ''),
                type=task_type,
                custom_type=custom_type,
                description=request.POST.get('description', ''),
                due_date=request.POST.get('due_date'),
                priority=request.POST.get('priority', 'media'),
                status=Task.STATUS_PENDENTE,
                created_by=request.user,
            )
            client_id = request.POST.get('client')
            process_id = request.POST.get('process')
            lawyer_id = request.POST.get('assigned_to')
            if client_id:
                task.client_id = client_id
            if process_id:
                task.process_id = process_id
            if lawyer_id:
                task.assigned_to_id = lawyer_id
            task.save()
            messages.success(request, 'Tarefa criada com sucesso!')
            return redirect('tasks:list')
        except Exception as e:
            messages.error(request, f'Erro ao criar tarefa: {e}')

    return render(request, 'tasks/form.html', {
        'title': 'Nova Tarefa',
        'clients': clients,
        'processes': processes,
        'lawyers': lawyers,
        'priority_choices': Task.PRIORITY_CHOICES,
        'type_choices': Task.TYPE_CHOICES,
    })


@login_required
def task_edit(request, pk):
    branch = get_branch(request)
    task = get_branch_object_or_403(Task, request, pk=pk)

    if not request.user.is_admin:
        lp = getattr(request.user, 'lawyer_profile', None)
        if not lp or task.assigned_to_id != lp.id:
            messages.error(request, 'Sem permissao para editar esta tarefa.')
            return redirect('tasks:list')

    clients = Client.objects.filter(branch=branch, is_active=True)
    processes = Process.objects.filter(branch=branch, is_active=True)
    lawyers = Lawyer.objects.filter(branch=branch, is_active=True)

    if request.method == 'POST':
        try:
            task_type, custom_type = get_task_type_data(request)
            task.title = request.POST.get('title', '')
            task.type = task_type
            task.custom_type = custom_type
            task.description = request.POST.get('description', '')
            task.due_date = request.POST.get('due_date')
            task.priority = request.POST.get('priority', 'media')

            new_status = request.POST.get('status', task.status)
            if request.user.is_admin:
                task.status = new_status
            else:
                allowed = {Task.STATUS_PENDENTE, Task.STATUS_EM_ANDAMENTO}
                if new_status in allowed:
                    task.status = new_status

            client_id = request.POST.get('client')
            process_id = request.POST.get('process')
            lawyer_id = request.POST.get('assigned_to')
            task.client_id = client_id if client_id else None
            task.process_id = process_id if process_id else None
            if request.user.is_admin:
                task.assigned_to_id = lawyer_id if lawyer_id else None

            task.save()
            messages.success(request, 'Tarefa atualizada!')
            return redirect('tasks:list')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar tarefa: {e}')

    return render(request, 'tasks/form.html', {
        'title': 'Editar Tarefa',
        'task': task,
        'clients': clients,
        'processes': processes,
        'lawyers': lawyers,
        'priority_choices': Task.PRIORITY_CHOICES,
        'type_choices': Task.TYPE_CHOICES,
        'status_choices': Task.STATUS_CHOICES,
    })


@login_required
def task_mark_done(request, pk):
    task = get_branch_object_or_403(Task, request, pk=pk)

    if not task.can_be_completed_by(request.user):
        messages.error(request, 'Apenas o advogado responsavel pode marcar como concluida.')
        return redirect('tasks:list')

    if task.status in (Task.STATUS_CONCLUIDA, Task.STATUS_CANCELADA):
        messages.warning(request, 'Esta tarefa ja esta finalizada.')
        return redirect('tasks:list')

    if request.method == 'POST':
        note = request.POST.get('completion_note', '')
        task.status = Task.STATUS_AGUARDANDO
        task.completed_by = request.user
        task.completed_at = timezone.now()
        task.completion_note = note
        task.save()
        messages.success(request, 'Tarefa marcada como concluida. Aguardando validacao do administrador.')
        return redirect('tasks:list')

    return render(request, 'tasks/confirm_done.html', {'task': task})


@login_required
def task_validate(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Apenas administradores podem validar tarefas.')
        return redirect('tasks:list')

    task = get_branch_object_or_403(Task, request, pk=pk)

    if task.status != Task.STATUS_AGUARDANDO:
        messages.warning(request, 'Esta tarefa nao esta aguardando validacao.')
        return redirect('tasks:list')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            task.status = Task.STATUS_CONCLUIDA
            task.validated_by = request.user
            task.validated_at = timezone.now()
            task.save()
            messages.success(request, f'Tarefa "{task.title}" validada e concluida.')
        elif action == 'reject':
            task.status = Task.STATUS_EM_ANDAMENTO
            task.completed_by = None
            task.completed_at = None
            task.completion_note = ''
            task.save()
            messages.warning(request, f'Tarefa "{task.title}" devolvida para o advogado.')
        return redirect('tasks:list')

    return render(request, 'tasks/validate.html', {'task': task})


@login_required
def task_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Apenas administradores podem excluir tarefas.')
        return redirect('tasks:list')
    task = get_branch_object_or_403(Task, request, pk=pk)
    task.delete()
    messages.success(request, 'Tarefa removida.')
    return redirect('tasks:list')
