from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.branches.models import Branch

User = get_user_model()


class Command(BaseCommand):
    help = "Create initial branches and users for GB & N.Comin Advocacia"

    def handle(self, *args, **options):
        branch_caxias, _ = Branch.objects.get_or_create(
            name="Caxias do Sul",
            defaults={
                "address": "R. Ver. Mario Pezzi, 564 - Exposicao",
                "phone": "(54) 9710-2525",
                "email": "caxias@gbadvocacia.com.br",
                "city": "Caxias do Sul",
                "state": "RS",
                "admin_name": "Admin Caxias",
                "is_active": True,
                "is_headquarters": False,
            },
        )
        branch_np, _ = Branch.objects.get_or_create(
            name="Nova Prata",
            defaults={
                "address": "Av. Presidente Vargas, 1860 - Sao Cristovao",
                "phone": "(54) 9710-2525",
                "email": "novaprata@gbadvocacia.com.br",
                "city": "Nova Prata",
                "state": "RS",
                "admin_name": "Admin Nova Prata",
                "is_active": True,
                "is_headquarters": True,
            },
        )

        if not branch_np.is_headquarters:
            branch_np.is_headquarters = True
            branch_np.save(update_fields=["is_headquarters"])
        Branch.objects.exclude(pk=branch_np.pk).filter(is_headquarters=True).update(is_headquarters=False)
        self.stdout.write(self.style.SUCCESS("Filiais verificadas"))

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@gbadvocacia.com.br",
                password="Admin@123",
                first_name="Super",
                last_name="Administrador",
                role="super_admin",
                branch=branch_np,
            )
            self.stdout.write(self.style.SUCCESS("Super Admin: admin / Admin@123"))
        else:
            self.stdout.write("Super Admin ja existe.")

        if not User.objects.filter(username="admin_caxias").exists():
            User.objects.create_user(
                username="admin_caxias",
                email="admincaxias@gbadvocacia.com.br",
                password="Admin@123",
                first_name="Admin",
                last_name="Caxias",
                role="admin",
                branch=branch_caxias,
            )
            self.stdout.write(self.style.SUCCESS("Admin Caxias: admin_caxias / Admin@123"))

        if not User.objects.filter(username="admin_np").exists():
            User.objects.create_user(
                username="admin_np",
                email="adminnp@gbadvocacia.com.br",
                password="Admin@123",
                first_name="Admin",
                last_name="Nova Prata",
                role="admin",
                branch=branch_np,
            )
            self.stdout.write(self.style.SUCCESS("Admin Nova Prata: admin_np / Admin@123"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Sistema pronto! Acesse: http://localhost/"))
        self.stdout.write(self.style.WARNING("Troque as senhas em producao e ative o 2FA!"))
