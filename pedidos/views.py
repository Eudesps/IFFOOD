# pedidos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Produto, Pedido, ProdutoNoPedido
from .forms import ProdutoForm
from django.db import transaction
from django.http import JsonResponse

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
        
        # BUSCA OS PEDIDOS DO CLIENTE LOGADO
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-criado_em')
        
        cart = request.session.get('cart', {})
        cart_item_count = sum(item['quantidade'] for item in cart.values())
        
        context = {
            'produtos': produtos,
            'pedidos': pedidos,
            'cart_item_count': cart_item_count
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
            
    # Redireciona de volta para a home com um parâmetro de aba
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
        
        # Retorna uma resposta JSON com o novo contador de itens
        cart_item_count = sum(item['quantidade'] for item in cart.values())
        return JsonResponse({'cart_item_count': cart_item_count, 'success': True})
    
    # Se não for POST, redireciona ou retorna um erro
    return JsonResponse({'success': False, 'error': 'Método de requisição inválido'}, status=405)

@login_required
@user_passes_test(is_cliente)
def cart_view(request):
    cart = request.session.get('cart', {})
    
    cart_items = []
    total = 0
    # Calcula a contagem de itens
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
        'cart_item_count': cart_item_count, # Passa a contagem para o template
    }
    
    return render(request, 'cliente/cart.html', context)


@login_required
@user_passes_test(is_cliente)
def checkout_view(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('home')  # Redireciona se o carrinho estiver vazio

        try:
            with transaction.atomic():
                # 1. Cria o objeto Pedido
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    total=0,  # O total será calculado abaixo
                    status='pedido' # Define o status inicial
                )

                total_final = 0
                
                # 2. Itera sobre os itens do carrinho e cria os objetos ProdutoNoPedido
                for produto_id_str, item_data in cart.items():
                    produto = Produto.objects.get(id=int(produto_id_str))
                    quantidade = item_data['quantidade']
                    
                    # Cria a relação ProdutoNoPedido
                    ProdutoNoPedido.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=quantidade
                    )
                    
                    # Calcula o total do pedido
                    total_final += produto.preco * quantidade
                
                # 3. Atualiza o total no objeto Pedido
                pedido.total = total_final
                pedido.save()
                
                # 4. Limpa o carrinho da sessão
                del request.session['cart']
                
                # Mensagem de sucesso (opcional, pode ser adicionada no futuro)
                # messages.success(request, 'Seu pedido foi finalizado com sucesso!')
                
                # Redireciona para uma página de confirmação ou para a home
                return redirect('home')

        except Produto.DoesNotExist:
            return render(request, 'pedidos/error.html', {'message': 'Um dos produtos não foi encontrado.'})
        except Exception as e:
            # Lida com outros erros, como problemas de banco de dados
            return render(request, 'pedidos/error.html', {'message': f'Ocorreu um erro ao finalizar o pedido: {e}'})

    # Se a requisição não for POST, redireciona para o carrinho
    return redirect('cart')

@login_required
@user_passes_test(is_cliente)
def order_detail_view(request, pedido_id):
    # Busca o pedido, garantindo que ele pertença ao cliente logado
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    # Busca todos os itens (produtos) associados a este pedido
    itens_pedido = pedido.produtonopedido_set.all()

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