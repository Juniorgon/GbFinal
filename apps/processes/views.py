from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
from .models import Process, ProcessUpdate
from apps.clients.models import Client
from apps.lawyers.models import Lawyer
import io, random, string


def get_branch(request):
    return getattr(request, 'current_branch', request.user.branch)


def get_process_type_data(request):
    process_type = request.POST.get('type', '')
    custom_type = request.POST.get('custom_type', '').strip()
    if process_type == 'outro' and not custom_type:
        raise ValueError('Informe o novo tipo de processo.')
    if process_type != 'outro':
        custom_type = ''
    return process_type, custom_type


@login_required
def process_list(request):
    branch = get_branch(request)
    qs = Process.objects.filter(branch=branch, is_active=True).select_related('client', 'lawyer')
    status = request.GET.get('status', '')
    tipo = request.GET.get('tipo', '')
    cliente = request.GET.get('cliente', '')
    if status:
        qs = qs.filter(status=status)
    if tipo:
        qs = qs.filter(type=tipo)
    if cliente:
        qs = qs.filter(client_id=cliente)
    total = qs.count()
    andamento = qs.filter(status='andamento').count()
    concluidos = qs.filter(status='concluido').count()
    suspensos = qs.filter(status='suspenso').count()
    valor_total = qs.aggregate(t=Sum('value'))['t'] or 0
    valor_medio = valor_total / total if total else 0
    clients = Client.objects.filter(branch=branch, is_active=True)
    context = {
        'processes': qs, 'status': status, 'tipo': tipo, 'cliente': cliente,
        'total': total, 'andamento': andamento, 'concluidos': concluidos,
        'suspensos': suspensos, 'valor_total': valor_total, 'valor_medio': valor_medio,
        'clients': clients,
        'lawyers': Lawyer.objects.filter(branch=branch, is_active=True),
        'type_choices': Process.TYPE_CHOICES,
        'status_choices': Process.STATUS_CHOICES,
        'position_choices': Process.POSITION_CHOICES,
    }
    return render(request, 'processes/list.html', context)


@login_required
def process_create(request):
    branch = get_branch(request)
    clients = Client.objects.filter(branch=branch, is_active=True)
    lawyers = Lawyer.objects.filter(branch=branch, is_active=True)
    if request.method == 'POST':
        try:
            process_type, custom_type = get_process_type_data(request)
            p = Process(
                branch=branch,
                client_id=request.POST.get('client'),
                number=request.POST.get('number', ''),
                type=process_type,
                custom_type=custom_type,
                status=request.POST.get('status', 'andamento'),
                client_position=request.POST.get('client_position', 'autor'),
                value=request.POST.get('value') or 0,
                description=request.POST.get('description', ''),
                court=request.POST.get('court', ''),
                opposing_party=request.POST.get('opposing_party', ''),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            lawyer_id = request.POST.get('lawyer')
            if lawyer_id:
                p.lawyer_id = lawyer_id
            p.save()
            messages.success(request, 'Processo cadastrado com sucesso!')
            return redirect('processes:list')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'processes/form.html', {
        'title': 'Novo Processo', 'clients': clients, 'lawyers': lawyers,
        'type_choices': Process.TYPE_CHOICES, 'status_choices': Process.STATUS_CHOICES,
        'position_choices': Process.POSITION_CHOICES,
    })


@login_required
def process_edit(request, pk):
    branch = get_branch(request)
    process = get_object_or_404(Process, pk=pk, branch=branch)
    clients = Client.objects.filter(branch=branch, is_active=True)
    lawyers = Lawyer.objects.filter(branch=branch, is_active=True)
    if request.method == 'POST':
        try:
            process_type, custom_type = get_process_type_data(request)
            process.client_id = request.POST.get('client')
            process.number = request.POST.get('number', '')
            process.type = process_type
            process.custom_type = custom_type
            process.status = request.POST.get('status', 'andamento')
            process.client_position = request.POST.get('client_position', 'autor')
            process.value = request.POST.get('value') or 0
            process.description = request.POST.get('description', '')
            process.court = request.POST.get('court', '')
            process.opposing_party = request.POST.get('opposing_party', '')
            process.notes = request.POST.get('notes', '')
            lawyer_id = request.POST.get('lawyer')
            process.lawyer_id = lawyer_id if lawyer_id else None
            process.save()
            messages.success(request, 'Processo atualizado!')
            return redirect('processes:list')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'processes/form.html', {
        'title': 'Editar Processo', 'process': process, 'clients': clients, 'lawyers': lawyers,
        'type_choices': Process.TYPE_CHOICES, 'status_choices': Process.STATUS_CHOICES,
        'position_choices': Process.POSITION_CHOICES,
    })


@login_required
def process_delete(request, pk):
    branch = get_branch(request)
    process = get_object_or_404(Process, pk=pk, branch=branch)
    process.is_active = False
    process.save_without_historical_record()
    messages.success(request, 'Processo removido.')
    return redirect('processes:list')


@login_required
def process_detail(request, pk):
    branch = get_branch(request)
    process = get_object_or_404(Process, pk=pk, branch=branch)
    updates = process.updates.all()
    if request.method == 'POST':
        title = request.POST.get('update_title', '')
        desc = request.POST.get('update_description', '')
        date_str = request.POST.get('update_date', '')
        if title and desc and date_str:
            ProcessUpdate.objects.create(process=process, title=title, description=desc,
                                         date=date_str, created_by=request.user)
            messages.success(request, 'Andamento adicionado!')
            return redirect('processes:detail', pk=pk)
    return render(request, 'processes/detail.html', {'process': process, 'updates': updates})


@login_required
def generate_number(request):
    """Generate a process number."""
    import datetime
    year = datetime.date.today().year
    num = ''.join(random.choices(string.digits, k=7))
    number = f"{num}-{random.randint(10,99)}.{year}.8.26.{random.randint(1000,9999)}"
    return HttpResponse(number)


@login_required
def export_pdf(request):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    branch = get_branch(request)
    processes = Process.objects.filter(branch=branch, is_active=True).select_related('client')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.rect(0, h - 60, w, 60, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont('Helvetica-Bold', 14)
    p.drawString(40, h - 38, 'GB & N.Comin Advocacia - Processos')
    y = h - 90
    p.setFillColor(colors.HexColor('#e8650a'))
    p.setFont('Helvetica-Bold', 9)
    for txt, x in [('Processo', 40), ('Cliente', 160), ('Tipo', 290), ('Status', 370), ('Valor', 450)]:
        p.drawString(x, y, txt)
    y -= 20
    p.setFillColor(colors.black)
    p.setFont('Helvetica', 8)
    for proc in processes:
        if y < 60:
            p.showPage()
            y = h - 60
        p.drawString(40, y, (proc.number or 'S/N')[:20])
        p.drawString(160, y, proc.client.name[:18])
        p.drawString(290, y, proc.type_label[:12])
        p.drawString(370, y, proc.get_status_display())
        p.drawString(450, y, f'R$ {proc.value:,.2f}')
        y -= 16
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="processos.pdf"'
    return response
