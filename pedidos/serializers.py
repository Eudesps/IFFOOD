# serializers.py
from rest_framework import serializers
from .models import Produto, Pedido, ProdutoNoPedido
from django.contrib.auth import get_user_model

User = get_user_model()

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco', 'categoria', 'imagem']

class ProdutoNoPedidoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer() # nested serializer para incluir os dados do produto

    class Meta:
        model = ProdutoNoPedido
        fields = ['produto', 'quantidade']

class PedidoSerializer(serializers.ModelSerializer):
    itens = ProdutoNoPedidoSerializer(many=True, read_only=True)
    cliente = serializers.CharField(source='cliente.username', read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'status', 'total', 'criado_em', 'itens']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)