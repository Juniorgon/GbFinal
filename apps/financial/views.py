"""
apps/financial/views.py
-----------------------
Financeiro: leitura para todos os usuarios da filial.
Criacao/edicao/exclusao: apenas administradores.
Isolamento de filial garantido no backend.
"""

import io
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render

from apps.accounts.permissions import financial_edit_required, get_branch_object_or_403
from apps.clients.models import Client
from apps.processes.models import Process

from .models import Transaction


def get_branch(request):
    return getattr(request, 'current_branch', None) or request.user.branch


def get_transaction_category(request):
    category = request.POST.get('category', '').strip()
    custom_category = request.POST.get('custom_category', '').strip()
    if category == 'outro':
        if not custom_category:
            raise ValueError('Informe a nova categoria da transacao.')
        return custom_category
    return category


@login_required
def transaction_list(request):
    branch = get_branch(request)
    qs = Transaction.objects.filter(branch=branch).select_related('client', 'process')

    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    if tipo:
        qs = qs.filter(type=tipo)
    if status:
        qs = qs.filter(status=status)

    base = Transaction.objects.filter(branch=branch)
    total_receitas = base.filter(type='receita', status='pago').aggregate(t=Sum('value'))['t'] or 0
    total_despesas = base.filter(type='despesa', status='pago').aggregate(t=Sum('value'))['t'] or 0
    a_receber = base.filter(type='receita', status__in=['pendente', 'vencido']).aggregate(t=Sum('value'))['t'] or 0
    a_pagar = base.filter(type='despesa', status__in=['pendente', 'vencido']).aggregate(t=Sum('value'))['t'] or 0

    return render(request, 'financial/list.html', {
        'transactions': qs,
        'tipo': tipo,
        'status': status,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'a_receber': a_receber,
        'a_pagar': a_pagar,
        'can_edit': request.user.is_admin,
        'category_choices_receita': Transaction.CATEGORY_CHOICES_RECEITA,
        'category_choices_despesa': Transaction.CATEGORY_CHOICES_DESPESA,
    })


@login_required
@financial_edit_required
def transaction_create(request):
    branch = get_branch(request)
    clients = Client.objects.filter(branch=branch, is_active=True)
    processes = Process.objects.filter(branch=branch, is_active=True)

    if request.method == 'POST':
        try:
            due_date_str = request.POST.get('due_date', '')
            if not due_date_str:
                raise ValueError('Data de vencimento é obrigatória.')
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Data de vencimento inválida.')
            transaction = Transaction(
                branch=branch,
                type=request.POST.get('type', 'receita'),
                category=get_transaction_category(request),
                description=request.POST.get('description', ''),
                value=request.POST.get('value', 0),
                due_date=due_date,
                status=request.POST.get('status', 'pendente'),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            client_id = request.POST.get('client')
            process_id = request.POST.get('process')
            payment_date_str = request.POST.get('payment_date', '')
            if client_id:
                transaction.client_id = client_id
            if process_id:
                transaction.process_id = process_id
            if payment_date_str:
                try:
                    transaction.payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('Data de pagamento inválida.')
            transaction.save()
            messages.success(request, 'Transacao salva com sucesso!')
            return redirect('financial:list')
        except Exception as e:
            messages.error(request, f'Erro: {e}')

    return render(request, 'financial/form.html', {
        'title': 'Nova Transacao',
        'clients': clients,
        'processes': processes,
        'category_choices_receita': Transaction.CATEGORY_CHOICES_RECEITA,
        'category_choices_despesa': Transaction.CATEGORY_CHOICES_DESPESA,
    })


@login_required
@financial_edit_required
def transaction_edit(request, pk):
    transaction = get_branch_object_or_403(Transaction, request, pk=pk)
    branch = get_branch(request)
    clients = Client.objects.filter(branch=branch, is_active=True)
    processes = Process.objects.filter(branch=branch, is_active=True)

    if request.method == 'POST':
        try:
            due_date_str = request.POST.get('due_date', '')
            if not due_date_str:
                raise ValueError('Data de vencimento é obrigatória.')
            try:
                transaction.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Data de vencimento inválida.')
            transaction.type = request.POST.get('type', transaction.type)
            transaction.category = get_transaction_category(request)
            transaction.description = request.POST.get('description', '')
            transaction.value = request.POST.get('value', 0)
            transaction.status = request.POST.get('status', 'pendente')
            transaction.notes = request.POST.get('notes', '')
            client_id = request.POST.get('client')
            process_id = request.POST.get('process')
            payment_date_str = request.POST.get('payment_date', '')
            transaction.client_id = client_id if client_id else None
            transaction.process_id = process_id if process_id else None
            if payment_date_str:
                try:
                    transaction.payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('Data de pagamento inválida.')
            else:
                transaction.payment_date = None
            transaction.save()
            messages.success(request, 'Transacao atualizada!')
            return redirect('financial:list')
        except Exception as e:
            messages.error(request, f'Erro: {e}')

    return render(request, 'financial/form.html', {
        'title': 'Editar Transacao',
        'transaction': transaction,
        'clients': clients,
        'processes': processes,
        'category_choices_receita': Transaction.CATEGORY_CHOICES_RECEITA,
        'category_choices_despesa': Transaction.CATEGORY_CHOICES_DESPESA,
    })


@login_required
@financial_edit_required
def transaction_delete(request, pk):
    transaction = get_branch_object_or_403(Transaction, request, pk=pk)
    transaction.delete()
    messages.success(request, 'Transacao removida.')
    return redirect('financial:list')


@login_required
def export_pdf(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    branch = get_branch(request)
    transactions = Transaction.objects.filter(branch=branch).order_by('-due_date')

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setFillColor(colors.HexColor('#1a1a2e'))
    pdf.rect(0, height - 60, width, 60, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, height - 38, 'GB & N.Comin Advocacia - Financeiro')
    y = height - 90
    pdf.setFillColor(colors.HexColor('#e8650a'))
    pdf.setFont('Helvetica-Bold', 9)
    for text, x in [('Tipo', 40), ('Descricao', 100), ('Valor', 300), ('Vencimento', 380), ('Status', 460)]:
        pdf.drawString(x, y, text)
    y -= 20
    pdf.setFont('Helvetica', 8)
    for transaction in transactions:
        if y < 60:
            pdf.showPage()
            y = height - 60
        color = colors.HexColor('#00aa44') if transaction.type == 'receita' else colors.HexColor('#cc3333')
        pdf.setFillColor(color)
        pdf.drawString(40, y, transaction.get_type_display())
        pdf.setFillColor(colors.black)
        pdf.drawString(100, y, transaction.description[:30])
        pdf.drawString(300, y, f'R$ {transaction.value:,.2f}')
        pdf.drawString(380, y, transaction.due_date.strftime('%d/%m/%Y'))
        pdf.drawString(460, y, transaction.get_status_display())
        y -= 16
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financeiro.pdf"'
    return response
