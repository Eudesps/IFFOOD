from django.shortcuts import render

# Create your views here.

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .models import Produto, Pedido, ProdutoNoPedido
from .serializers import ProdutoSerializer, PedidoSerializer, UserLoginSerializer

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({
                    'message': 'Login bem-sucedido!',
                    'user_type': user.user_type
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'message': 'Logout bem-sucedido.'}, status=status.HTTP_200_OK)

class ProductListView(generics.ListAPIView):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderCreateView(generics.CreateAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # A lógica para criar um pedido será inserida aqui
        pass

class AdminPanelOrderView(generics.ListAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAdminUser]

# Você precisará criar os serializers correspondentes em um arquivo serializers.py
# para que estas views funcionem.