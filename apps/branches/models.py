from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    address = models.CharField(max_length=200, blank=True, verbose_name='Endereço')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='Email')
    city = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    state = models.CharField(max_length=2, blank=True, verbose_name='Estado')
    admin_name = models.CharField(max_length=100, blank=True, verbose_name='Admin')
    is_headquarters = models.BooleanField(default=False, verbose_name='Sede Principal')
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiais'
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_branch(cls):
        return cls.objects.filter(is_active=True).order_by('-is_headquarters', 'name').first()
