# IFFOOD

## Descrição do Projeto
Este projeto é uma plataforma completa de pedidos de comida, inspirada no conceito do iFood.    
Ele é responsável por toda a lógica do backend e também pela renderização do frontend através de templates HTML.

O objetivo é simular a experiência de um cliente fazendo um pedido e a de um restaurante gerenciando esses pedidos, tudo dentro de uma única aplicação Django.

## Funcionalidades
- **Autenticação de Usuário:** Suporte a login para dois tipos de usuários: **Cliente** e **Restaurante**.
- **Interface de Cliente:** Clientes podem navegar pelo cardápio, adicionar produtos ao carrinho e finalizar pedidos.
- **Interface de Restaurante (Admin):** Usuários com perfil de restaurante podem visualizar todos os pedidos recebidos e atualizar o status de cada um (por exemplo, de *Pedido* para *Em preparo*).
- **Renderização de Templates:** O Django renderiza todas as páginas (login, cardápio, painel de admin) usando seu sistema de templates.

## Tecnologias Utilizadas
- **Django:** Framework web Python para o desenvolvimento completo da aplicação.
- **Sistema de Templates do Django:** Utilizado para renderizar as interfaces de usuário (*HTML*, *CSS* e *JavaScript*).
- **Django Forms:** Para gerenciar os formulários de entrada de dados, como o login.
- **Banco de Dados:** Configurado com o banco de dados padrão do Django (*SQLite*).
