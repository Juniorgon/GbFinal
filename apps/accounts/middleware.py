"""
apps/accounts/middleware.py
---------------------------
BranchMiddleware: define request.current_branch a cada request
e valida que o usuário tem permissão real para acessar aquela filial.
"""

from apps.branches.models import Branch


class BranchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.current_branch = self._resolve_branch(request)
        else:
            request.current_branch = None
        return self.get_response(request)

    def _resolve_branch(self, request):
        user = request.user
        branch_id = request.session.get('current_branch_id')
        lawyer_profile = getattr(user, 'lawyer_profile', None)

        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id, is_active=True)
                if user.is_super_admin:
                    return branch
                if user.is_admin:
                    if user.branch_id == branch.id:
                        return branch
                    request.session['current_branch_id'] = user.branch_id
                    return user.branch
                if lawyer_profile:
                    if (
                        lawyer_profile.branch_id == branch.id
                        or lawyer_profile.accessible_branches.filter(id=branch.id).exists()
                    ):
                        return branch
                    request.session['current_branch_id'] = lawyer_profile.branch_id
                    return lawyer_profile.branch
                request.session['current_branch_id'] = user.branch_id
                return user.branch
            except Branch.DoesNotExist:
                pass

        if lawyer_profile and lawyer_profile.branch and lawyer_profile.branch.is_active:
            request.session['current_branch_id'] = lawyer_profile.branch_id
            return lawyer_profile.branch

        if user.branch and user.branch.is_active:
            request.session['current_branch_id'] = user.branch_id
            return user.branch

        if user.is_super_admin:
            first = Branch.get_default_branch()
            if first:
                request.session['current_branch_id'] = first.id
                return first

        return None
