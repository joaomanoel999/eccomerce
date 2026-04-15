from django.contrib import admin
from .models import Produto, Categoria, Pedido, ItemPedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display  = ['nome', 'marca', 'preco', 'estoque', 'destaque', 'categoria']
    list_filter   = ['categoria', 'destaque']
    search_fields = ['nome', 'marca']
    list_editable = ['preco', 'estoque', 'destaque']


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['preco_unit', 'subtotal']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'status', 'total', 'criado_em']
    list_filter  = ['status']
    inlines      = [ItemPedidoInline]
