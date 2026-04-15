def carrinho_contador(request):
   
    carrinho = request.session.get('carrinho', {})
    total = sum(carrinho.values())
    return {'carrinho_total': total}
