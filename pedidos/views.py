# pedidos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Produto, Pedido, ProdutoNoPedido
from .forms import ProdutoForm

# Função para verificar se o usuário é um restaurante
def is_restaurante(user):
    return user.user_type == 'restaurante'

# Função para verificar se o usuário é um cliente
def is_cliente(user):
    return user.user_type == 'cliente'


# View de Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type_form = request.POST.get('user_type')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.user_type == user_type_form:
                login(request, user)
                return redirect('home')
            else:
                error = "Credenciais inválidas para este tipo de acesso."
        else:
            error = "Credenciais inválidas."
        
        return render(request, 'login/login.html', {'error': error})
    
    return render(request, 'login/login.html')

# View de Home (página inicial)
@login_required
def home_view(request):
    if is_restaurante(request.user):
        produtos = Produto.objects.all()
        # Pedidos do mais novo para o mais antigo
        pedidos = Pedido.objects.all().order_by('-criado_em')
        
        context = {
            'produtos': produtos,
            'pedidos': pedidos
        }
        return render(request, 'restaurante/restaurante_home.html', context)
    
    elif is_cliente(request.user):
        produtos = Produto.objects.all()
        # Futuramente, vamos buscar os pedidos do cliente logado aqui
        context = {
            'produtos': produtos,
            'pedidos': [] # Lista vazia por enquanto
        }
        return render(request, 'cliente/cliente_home.html', context)
    
    # Caso o user_type seja inválido ou não definido
    return redirect('login')


# View de Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# --------------------------------------------------------------------------
# Vistas para Gerenciamento de Produtos
# --------------------------------------------------------------------------

@login_required
@user_passes_test(is_restaurante)
def add_produto_view(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProdutoForm()
    
    context = {'form': form}
    return render(request, 'restaurante/add_produto.html', context)

@login_required
@user_passes_test(is_restaurante)
def edit_produto_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProdutoForm(instance=produto)
    
    context = {'form': form, 'produto': produto}
    return render(request, 'restaurante/edit_produto.html', context)

@login_required
@user_passes_test(is_restaurante)
def delete_produto_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        produto.delete()
        return redirect('home')
    
    return render(request, 'restaurante/delete_produto.html', {'produto': produto})


# --------------------------------------------------------------------------
# Vistas para Gerenciamento de Pedidos
# --------------------------------------------------------------------------

@login_required
@user_passes_test(is_restaurante)
def update_status_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['pedido', 'em_preparo', 'saiu_para_entrega']:
            pedido.status = status
            pedido.save()
    return redirect('home')

@login_required
@user_passes_test(is_restaurante)
def detalhes_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens_pedido = pedido.itens.all() # assuming 'itens' is the related_name
    context = {
        'pedido': pedido,
        'itens_pedido': itens_pedido
    }
    return render(request, 'restaurante/detalhes_pedido.html', context)