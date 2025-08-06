# pedidos/forms.py
from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco', 'categoria', 'imagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Hambúrguer Clássico'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 25.90'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Lanches, Pizzas'}),
            'imagem': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL da imagem'}),
        }
        labels = {
            'nome': 'Nome do Produto',
            'preco': 'Preço',
            'categoria': 'Categoria',
            'imagem': 'URL da Imagem',
        }