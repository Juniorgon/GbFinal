from apps.branches.models import Branch
from django.conf import settings


def branch_context(request):
    if not request.user.is_authenticated:
        return {}

    # Branches the current user can switch to
    if request.user.is_super_admin:
        all_branches = Branch.objects.filter(is_active=True)
    elif hasattr(request.user, 'lawyer_profile') and request.user.lawyer_profile:
        lp = request.user.lawyer_profile
        branch_ids = [lp.branch_id]
        branch_ids.extend(lp.accessible_branches.filter(is_active=True).values_list('id', flat=True))
        all_branches = Branch.objects.filter(id__in=branch_ids, is_active=True)
    else:
        all_branches = Branch.objects.filter(id=request.user.branch_id, is_active=True)

    return {
        'current_branch': getattr(request, 'current_branch', None),
        'all_branches': all_branches,
        'branch_count': all_branches.count(),
        'user_is_admin': request.user.is_admin,
        'user_is_super_admin': request.user.is_super_admin,
        'system_version': getattr(settings, 'SYSTEM_VERSION', ''),
        'system_env': getattr(settings, 'SYSTEM_ENV', 'development'),
    }
