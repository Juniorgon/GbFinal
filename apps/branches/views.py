from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.permissions import super_admin_required

from .models import Branch


@login_required
def switch_branch(request):
    referer = request.META.get("HTTP_REFERER", "/")
    if request.method != "POST":
        return redirect(referer)

    branch_id = request.POST.get("branch_id")
    branch = Branch.objects.filter(id=branch_id, is_active=True).first()

    if not branch:
        messages.error(request, "Filial invalida.")
        return redirect(referer)

    user = request.user
    if user.is_super_admin:
        request.session["current_branch_id"] = branch.id
        messages.success(request, f"Filial alterada para {branch.name}.")
        return redirect(referer)

    if user.is_admin:
        if user.branch_id == branch.id:
            request.session["current_branch_id"] = branch.id
            messages.success(request, f"Filial alterada para {branch.name}.")
        else:
            messages.error(request, "Voce nao tem permissao para acessar essa filial.")
        return redirect(referer)

    lawyer_profile = getattr(user, "lawyer_profile", None)
    has_access = False
    if lawyer_profile:
        has_access = (
            lawyer_profile.branch_id == branch.id
            or lawyer_profile.accessible_branches.filter(id=branch.id).exists()
        )
    if has_access:
        request.session["current_branch_id"] = branch.id
        messages.success(request, f"Filial alterada para {branch.name}.")
    else:
        messages.error(request, "Voce nao tem permissao para acessar essa filial.")
    return redirect(referer)


@super_admin_required
def branch_list(request):
    branches = Branch.objects.all().order_by('name')
    return render(request, 'branches/list.html', {'branches': branches})
