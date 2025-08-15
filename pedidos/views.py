# pedidos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Produto, Pedido, ProdutoNoPedido
from .forms import ProdutoForm
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages

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
        pedidos = Pedido.objects.all().order_by('-criado_em')
        
        context = {
            'produtos': produtos,
            'pedidos': pedidos
        }
        return render(request, 'restaurante/restaurante_home.html', context)
    
    elif is_cliente(request.user):
        produtos = Produto.objects.all()
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-criado_em')
        cart = request.session.get('cart', {})
        cart_item_count = sum(item['quantidade'] for item in cart.values())
        
        context = {
            'produtos': produtos,
            'pedidos': pedidos,
            'cart_item_count': cart_item_count,
        }
        return render(request, 'cliente/cliente_home.html', context)
    
    return redirect('login')

# View de Logout
def logout_view(request):
    logout(request)
    return redirect('login')

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


@login_required
@user_passes_test(is_restaurante)
def update_status_pedido_view(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        status = request.POST.get('status')
        
        # Verifique se o status recebido é válido
        valid_statuses = [choice[0] for choice in Pedido.STATUS_CHOICES]
        if status in valid_statuses:
            pedido.status = status
            pedido.save()
            
    return redirect(f"{reverse('home')}?tab=pedidos")

@login_required
@user_passes_test(is_restaurante)
def detalhes_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens_pedido = pedido.itens.all()
    context = {
        'pedido': pedido,
        'itens_pedido': itens_pedido
    }
    return render(request, 'restaurante/detalhes_pedido.html', context)


@login_required
@user_passes_test(is_cliente)
def add_to_cart_view(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)
        
        if 'cart' not in request.session:
            request.session['cart'] = {}
            
        cart = request.session['cart']
        produto_id_str = str(produto.id)
        
        if produto_id_str in cart:
            cart[produto_id_str]['quantidade'] += 1
        else:
            cart[produto_id_str] = {
                'quantidade': 1,
                'nome': produto.nome,
                'preco': str(produto.preco)
            }
        
        request.session.modified = True
        
        cart_item_count = sum(item['quantidade'] for item in cart.values())
        return JsonResponse({'cart_item_count': cart_item_count, 'success': True})
    
    return JsonResponse({'success': False, 'error': 'Método de requisição inválido'}, status=405)

@login_required
@user_passes_test(is_cliente)
def cart_view(request):
    cart = request.session.get('cart', {})
    
    cart_items = []
    total = 0
    cart_item_count = sum(item['quantidade'] for item in cart.values())

    for produto_id, item_data in cart.items():
        produto = get_object_or_404(Produto, id=int(produto_id))
        subtotal = produto.preco * item_data['quantidade']
        total += subtotal
        cart_items.append({
            'produto': produto,
            'quantidade': item_data['quantidade'],
            'subtotal': subtotal
        })

    context = {
        'cart_items': cart_items,
        'cart_total': total,
        'cart_item_count': cart_item_count,
    }
    
    return render(request, 'cliente/cart.html', context)


@login_required
@user_passes_test(is_cliente)
def checkout_view(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'O seu carrinho está vazio.')
            return redirect('cart')

        try:
            with transaction.atomic():
                total_final = 0
                itens_do_pedido = []

                for produto_id_str, item_data in cart.items():
                    produto = get_object_or_404(Produto, id=int(produto_id_str))
                    quantidade = item_data['quantidade']
                    subtotal = produto.preco * quantidade
                    total_final += subtotal
                    itens_do_pedido.append({
                        'produto': produto,
                        'quantidade': quantidade
                    })

                pedido = Pedido.objects.create(
                    cliente=request.user,
                    total=total_final,
                    status='pedido'
                )

                for item in itens_do_pedido:
                    ProdutoNoPedido.objects.create(
                        pedido=pedido,
                        produto=item['produto'],
                        quantidade=item['quantidade']
                    )

                del request.session['cart']
                request.session.modified = True

                messages.success(request, 'Pedido finalizado com sucesso! Você pode acompanhar o status na seção "Meus Pedidos".')
                return redirect('home')

        except Produto.DoesNotExist:
            messages.error(request, 'Um dos produtos não foi encontrado. Por favor, verifique seu carrinho.')
            return redirect('cart')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao finalizar o pedido: {e}')
            return redirect('cart')

    return redirect('cart')


@login_required
@user_passes_test(is_cliente)
def order_detail_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    itens_pedido = pedido.itens.all()

    context = {
        'pedido': pedido,
        'itens_pedido': itens_pedido,
    }
    
    return render(request, 'cliente/order_detail.html', context)

@login_required
@user_passes_test(is_cliente)
def remove_from_cart_view(request, produto_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        produto_id_str = str(produto_id)
        
        if produto_id_str in cart:
            del cart[produto_id_str]
            request.session.modified = True
            
    return redirect('cart')

def search_products_view(request):
    query = request.GET.get('q', '')
    if query:
        produtos = Produto.objects.filter(
            Q(nome__icontains=query) | Q(categoria__icontains=query)
        )
    else:
        produtos = Produto.objects.all()

    results = [
        {
            'id': produto.id,
            'nome': produto.nome,
            'preco': str(produto.preco),
            'categoria': produto.categoria,
        }
        for produto in produtos
    ]
    
    return JsonResponse(results, safe=False)