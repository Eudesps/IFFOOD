# IFFOOD/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pedidos.urls')),  # Altera a rota principal para o app 'pedidos'
]