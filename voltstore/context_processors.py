def carrinho_contador(request):
    """Disponibiliza o total de itens do carrinho em todos os templates."""
    carrinho = request.session.get('carrinho', {})
    total = sum(carrinho.values())
    return {'carrinho_total': total}
