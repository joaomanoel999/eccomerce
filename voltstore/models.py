from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    icone = models.CharField(max_length=10, default='📦')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome        = models.CharField(max_length=200)
    marca       = models.CharField(max_length=100)
    descricao   = models.TextField()
    preco       = models.DecimalField(max_digits=10, decimal_places=2)
    preco_antigo= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagem      = models.ImageField(upload_to='produtos/', blank=True, null=True)
    categoria   = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    estoque     = models.IntegerField(default=0)
    destaque    = models.BooleanField(default=False)
    criado_em   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome

    def desconto_percentual(self):
        if self.preco_antigo and self.preco_antigo > self.preco:
            return int(((self.preco_antigo - self.preco) / self.preco_antigo) * 100)
        return 0


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente',    'Pendente'),
        ('pago',        'Pago'),
        ('enviado',     'Enviado'),
        ('entregue',    'Entregue'),
        ('cancelado',   'Cancelado'),
    ]

    usuario     = models.ForeignKey(User, on_delete=models.CASCADE)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    total       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    endereco    = models.CharField(max_length=300, blank=True)
    criado_em   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.id} — {self.usuario.username}'

    def calcular_total(self):
        total = sum(item.subtotal() for item in self.itens.all())
        self.total = total
        self.save()
        return total


class ItemPedido(models.Model):
    pedido      = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto     = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade  = models.IntegerField(default=1)
    preco_unit  = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
     if self.preco_unit is None:
        return 0
     return self.preco_unit * self.quantidade

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'
