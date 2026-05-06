from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.branches.models import Branch

User = get_user_model()


class Command(BaseCommand):
    help = "Create initial branches and users for GB & N.Comin Advocacia"

    def ensure_user(self, *, username, email, password, first_name, last_name, role, branch, is_superuser=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "branch": branch,
                "is_staff": True,
                "is_superuser": is_superuser,
                "is_active": True,
            },
        )

        fields_to_update = []
        expected_values = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "branch": branch,
            "is_staff": True,
            "is_superuser": is_superuser,
            "is_active": True,
        }

        for field, value in expected_values.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                fields_to_update.append(field)

        user.set_password(password)
        fields_to_update.append("password")

        if fields_to_update:
            user.save(update_fields=fields_to_update)

        status = "criado" if created else "atualizado"
        self.stdout.write(self.style.SUCCESS(f"Usuario {status}: {username} / {password}"))
        return user

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

        self.ensure_user(
            username="admin",
            email="admin@gbadvocacia.com.br",
            password="Admin@123",
            first_name="Super",
            last_name="Administrador",
            role=User.ROLE_SUPER_ADMIN,
            branch=branch_caxias,
            is_superuser=True,
        )
        self.ensure_user(
            username="admin_caxias",
            email="admincaxias@gbadvocacia.com.br",
            password="Admin@123",
            first_name="Admin",
            last_name="Caxias",
            role=User.ROLE_ADMIN,
            branch=branch_caxias,
        )
        self.ensure_user(
            username="admin_np",
            email="adminnp@gbadvocacia.com.br",
            password="Admin@123",
            first_name="Admin",
            last_name="Nova Prata",
            role=User.ROLE_ADMIN,
            branch=branch_np,
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Sistema pronto! Acesse: http://localhost/"))
        self.stdout.write(self.style.WARNING("Troque as senhas em producao e ative o 2FA!"))
