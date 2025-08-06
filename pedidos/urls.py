# pedidos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs de autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),

    # URLs de gerenciamento de produtos (para restaurante)
    path('produtos/adicionar/', views.add_produto_view, name='add-produto'),
    path('produtos/editar/<int:produto_id>/', views.edit_produto_view, name='edit-produto'),
    path('produtos/excluir/<int:produto_id>/', views.delete_produto_view, name='delete-produto'),
    
    # URLs de gerenciamento de pedidos (para restaurante)
    path('pedidos/atualizar-status/<int:pedido_id>/', views.update_status_pedido_view, name='update-status-pedido'),
    path('pedidos/detalhes/<int:pedido_id>/', views.detalhes_pedido_view, name='detalhes-pedido'),
]