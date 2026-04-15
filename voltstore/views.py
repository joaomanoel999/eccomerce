from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Produto, Categoria, Pedido, ItemPedido
from .forms import LoginForm, CadastroForm, CheckoutForm



# PÁGINAS PRINCIPAIS

def pagina_inicial(request):
    """Página inicial com produtos em destaque."""
    produtos_destaque = Produto.objects.filter(destaque=True)[:8]
    categorias = Categoria.objects.all()
    return render(request, 'voltstore/pagina_inicial.html', {
        'produtos': produtos_destaque,
        'categorias': categorias,
    })


def lista_produtos(request):
    """Lista todos os produtos com filtro por categoria e busca."""
    produtos = Produto.objects.filter(estoque__gt=0)
    categorias = Categoria.objects.all()

    # Filtro por categoria
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)

    # Busca por nome
    busca = request.GET.get('busca', '')
    if busca:
        produtos = produtos.filter(nome__icontains=busca)

    return render(request, 'voltstore/produtos.html', {
        'produtos': produtos,
        'categorias': categorias,
        'busca': busca,
        'categoria_selecionada': categoria_id,
    })


def detalhe_produto(request, pk):
    """Página de detalhe de um produto."""
    produto = get_object_or_404(Produto, pk=pk)
    relacionados = Produto.objects.filter(categoria=produto.categoria).exclude(pk=pk)[:4]
    return render(request, 'voltstore/detalhe_produto.html', {
        'produto': produto,
        'relacionados': relacionados,
    })



# AUTENTICAÇÃO

def login_view(request):
    """Login do usuário."""
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email    = form.cleaned_data['email']
        senha    = form.cleaned_data['senha']
        # Busca por email
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            username = email  # tenta como username direto

        usuario = authenticate(request, username=username, password=senha)
        if usuario:
            login(request, usuario)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'E-mail ou senha incorretos.')

    return render(request, 'voltstore/login.html', {'form': form})


def logout_view(request):
    """Logout do usuário."""
    logout(request)
    return redirect('home')


def cadastro_view(request):
    """Cadastro de novo usuário."""
    if request.user.is_authenticated:
        return redirect('home')

    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['senha'])
        user.email = form.cleaned_data['email']
        user.save()
        login(request, user)
        messages.success(request, f'Bem-vindo, {user.first_name}!')
        return redirect('home')

    return render(request, 'voltstore/cadastro.html', {'form': form})



# CARRINHO (usando sessão)

def _get_carrinho(request):
    """Retorna o carrinho da sessão (dict: produto_id -> quantidade)."""
    return request.session.get('carrinho', {})


def _save_carrinho(request, carrinho):
    request.session['carrinho'] = carrinho
    request.session.modified = True


def carrinho_view(request):
    """Exibe o carrinho de compras."""
    carrinho = _get_carrinho(request)
    itens = []
    total = 0

    for produto_id, quantidade in carrinho.items():
        try:
            produto = Produto.objects.get(pk=produto_id)
            subtotal = produto.preco * quantidade
            total += subtotal
            itens.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})
        except Produto.DoesNotExist:
            pass

    return render(request, 'voltstore/carrinho.html', {
        'itens': itens,
        'total': total,
    })


def adicionar_carrinho(request, pk):
    """Adiciona produto ao carrinho."""
    produto = get_object_or_404(Produto, pk=pk)
    carrinho = _get_carrinho(request)
    chave = str(pk)

    carrinho[chave] = carrinho.get(chave, 0) + 1
    _save_carrinho(request, carrinho)

    messages.success(request, f'"{produto.nome}" adicionado ao carrinho!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def remover_carrinho(request, pk):
    """Remove produto do carrinho."""
    carrinho = _get_carrinho(request)
    carrinho.pop(str(pk), None)
    _save_carrinho(request, carrinho)
    return redirect('carrinho')


def atualizar_carrinho(request, pk):
    """Atualiza quantidade de um item no carrinho."""
    if request.method == 'POST':
        carrinho = _get_carrinho(request)
        quantidade = int(request.POST.get('quantidade', 1))
        if quantidade > 0:
            carrinho[str(pk)] = quantidade
        else:
            carrinho.pop(str(pk), None)
        _save_carrinho(request, carrinho)
    return redirect('carrinho')



# CHECKOUT E PEDIDO

@login_required
def checkout_view(request):
    """Tela de checkout com endereço e resumo."""
    carrinho = _get_carrinho(request)
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('carrinho')

    itens = []
    total = 0
    for produto_id, quantidade in carrinho.items():
        try:
            produto = Produto.objects.get(pk=produto_id)
            subtotal = produto.preco * quantidade
            total += subtotal
            itens.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})
        except Produto.DoesNotExist:
            pass

    form = CheckoutForm(request.POST or None)
    return render(request, 'voltstore/checkout.html', {
        'form': form,
        'itens': itens,
        'total': total,
    })


@login_required
def confirmar_pedido(request):
    """Cria o pedido no banco de dados."""
    if request.method != 'POST':
        return redirect('checkout')

    carrinho = _get_carrinho(request)
    if not carrinho:
        return redirect('carrinho')

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Verifique os dados de entrega.')
        return redirect('checkout')

    # Cria o pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        endereco=form.cleaned_data['endereco'],
    )

    for produto_id, quantidade in carrinho.items():
        try:
            produto = Produto.objects.get(pk=produto_id)
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unit=produto.preco,
            )
        except Produto.DoesNotExist:
            pass

    pedido.calcular_total()

    # Limpa o carrinho
    request.session['carrinho'] = {}
    request.session.modified = True

    return redirect('pedido_sucesso', pk=pedido.pk)


@login_required
def pedido_sucesso(request, pk):
    """Tela de confirmação após o pedido."""
    pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    return render(request, 'voltstore/pedido_sucesso.html', {'pedido': pedido})


# ÁREA DO USUÁRIO


@login_required
def minha_conta(request):
    """Perfil do usuário."""
    return render(request, 'voltstore/minha_conta.html', {'usuario': request.user})


@login_required
def meus_pedidos(request):
    """Lista os pedidos do usuário."""
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, 'voltstore/meus_pedidos.html', {'pedidos': pedidos})


@login_required
def detalhe_pedido(request, pk):
    """Detalhe de um pedido específico."""
    pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    return render(request, 'voltstore/detalhe_pedido.html', {'pedido': pedido})
