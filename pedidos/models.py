# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("cliente", "Cliente"),
        ("restaurante", "Restaurante"),
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="cliente",
    )

    # Adicione estes campos para resolver o erro
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='pedidos_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='pedidos_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='pedidos_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='pedidos_user_permission',
    )

    def __str__(self):
        return self.username