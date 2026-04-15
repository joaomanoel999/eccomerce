from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('',                    views.pagina_inicial,   name='home'),
    path('produtos/',           views.lista_produtos,   name='produtos'),
    path('produto/<int:pk>/',   views.detalhe_produto,  name='detalhe_produto'),

    # Autenticação
    path('login/',              views.login_view,       name='login'),
    path('logout/',             views.logout_view,      name='logout'),
    path('cadastro/',           views.cadastro_view,    name='cadastro'),

    # Carrinho (sessão)
    path('carrinho/',           views.carrinho_view,    name='carrinho'),
    path('carrinho/adicionar/<int:pk>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('carrinho/remover/<int:pk>/',   views.remover_carrinho,   name='remover_carrinho'),
    path('carrinho/atualizar/<int:pk>/', views.atualizar_carrinho, name='atualizar_carrinho'),

    # Checkout e Pedido
    path('checkout/',           views.checkout_view,    name='checkout'),
    path('pedido/confirmar/',   views.confirmar_pedido, name='confirmar_pedido'),
    path('pedido/sucesso/<int:pk>/', views.pedido_sucesso, name='pedido_sucesso'),

    # Área do usuário
    path('minha-conta/',        views.minha_conta,      name='minha_conta'),
    path('meus-pedidos/',       views.meus_pedidos,     name='meus_pedidos'),
    path('meus-pedidos/<int:pk>/', views.detalhe_pedido, name='detalhe_pedido'),
]
