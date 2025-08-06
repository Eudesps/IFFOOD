# pedidos/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo de Usuário Personalizado
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

# Modelo de Produtos
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

# Modelo de Pedidos
class Pedido(models.Model):
    STATUS_CHOICES = (
        ("pedido", "Pedido"),
        ("em_preparo", "Em preparo"),
        ("saiu_para_entrega", "Saiu para entrega"),
    )
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pedido"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} de {self.cliente.username}"

# Modelo de Produto no Pedido
class ProdutoNoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} em Pedido #{self.pedido.id}"