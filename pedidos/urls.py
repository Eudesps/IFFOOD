from django.urls import path
from .views import LoginView, LogoutView, ProductListView, OrderCreateView, AdminPanelOrderView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('produtos/', ProductListView.as_view(), name='produto-list'),
    path('pedidos/criar/', OrderCreateView.as_view(), name='pedido-create'),
    path('admin/pedidos/', AdminPanelOrderView.as_view(), name='admin-panel-orders'),
]