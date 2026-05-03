"""
apps/dashboard/views.py
------------------------
Dashboard principal — visível para todos os usuários autenticados da filial.
"""

import json
from datetime import timedelta, date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count

from apps.clients.models import Client
from apps.processes.models import Process
from apps.financial.models import Transaction
from apps.tasks.models import Task


def get_branch(request):
    return getattr(request, 'current_branch', None) or request.user.branch


@login_required
def index(request):
    branch = get_branch(request)
    if not branch:
        from apps.branches.models import Branch
        branch = Branch.get_default_branch()

    period = request.GET.get('period', 'mes')
    today = timezone.now().date()

    if period == 'semana':
        start_date = today - timedelta(days=7)
    elif period == 'ano':
        start_date = date(today.year, 1, 1)
    else:
        start_date = date(today.year, today.month, 1)

    f = {'branch': branch} if branch else {}

    total_clients   = Client.objects.filter(**f, is_active=True).count()
    total_processes = Process.objects.filter(**f, is_active=True).count()

    receitas_qs = Transaction.objects.filter(**f, type='receita', status='pago')
    despesas_qs = Transaction.objects.filter(**f, type='despesa', status='pago')

    receita_total   = receitas_qs.aggregate(t=Sum('value'))['t'] or 0
    despesa_total   = despesas_qs.aggregate(t=Sum('value'))['t'] or 0
    receita_mensal  = receitas_qs.filter(payment_date__gte=start_date).aggregate(t=Sum('value'))['t'] or 0
    despesa_mensal  = despesas_qs.filter(payment_date__gte=start_date).aggregate(t=Sum('value'))['t'] or 0

    pag_pendentes = Transaction.objects.filter(**f, status='pendente').count()
    pag_vencidos  = Transaction.objects.filter(**f, status='vencido').count()

    # Last 6 months chart
    chart_labels, chart_receitas, chart_despesas = [], [], []
    for i in range(5, -1, -1):
        d = today.replace(day=1) - timedelta(days=i * 28)
        chart_labels.append(d.strftime('%b/%y'))
        r  = Transaction.objects.filter(**f, type='receita', status='pago',
             payment_date__year=d.year, payment_date__month=d.month
             ).aggregate(t=Sum('value'))['t'] or 0
        de = Transaction.objects.filter(**f, type='despesa', status='pago',
             payment_date__year=d.year, payment_date__month=d.month
             ).aggregate(t=Sum('value'))['t'] or 0
        chart_receitas.append(float(r))
        chart_despesas.append(float(de))

    proc_qs       = Process.objects.filter(**f, is_active=True)
    proc_andamento = proc_qs.filter(status='andamento').count()
    proc_concluido = proc_qs.filter(status='concluido').count()
    proc_suspenso  = proc_qs.filter(status='suspenso').count()

    # Tasks pending validation (for admins)
    pending_validation = Task.objects.filter(**f, status='aguardando').count() if request.user.is_admin else 0

    # Recent pending tasks (filtered by lawyer for non-admins)
    task_qs = Task.objects.filter(**f).exclude(status__in=['concluida', 'cancelada']).order_by('due_date')
    if not request.user.is_admin:
        lp = getattr(request.user, 'lawyer_profile', None)
        if lp:
            task_qs = task_qs.filter(assigned_to=lp)
    recent_tasks = task_qs[:6]

    context = {
        'period': period,
        'branch': branch,
        'total_clients': total_clients,
        'total_processes': total_processes,
        'receita_total': receita_total,
        'despesa_total': despesa_total,
        'receita_mensal': receita_mensal,
        'despesa_mensal': despesa_mensal,
        'pag_pendentes': pag_pendentes,
        'pag_vencidos': pag_vencidos,
        'chart_labels': json.dumps(chart_labels),
        'chart_receitas': json.dumps(chart_receitas),
        'chart_despesas': json.dumps(chart_despesas),
        'proc_andamento': proc_andamento,
        'proc_concluido': proc_concluido,
        'proc_suspenso': proc_suspenso,
        'recent_tasks': recent_tasks,
        'pending_validation': pending_validation,
    }
    return render(request, 'dashboard/index.html', context)
