from app.classes import Activerecord


class ProductoCarrito(Activerecord):
    TABLA = 'producto_carrito'
    CAMPOS = [
        'id_producto_carrito',
        'fecha_añadido',
        'cantidad',
        'talla',
        'precio_unitario',
        'precio_total',
        'id_carrito',
        'id_color_producto'
    ]
    errores = []

    def __init__(
        self,
        id_producto_carrito=None,
        fecha_añadido=None,
        cantidad=None,
        talla=None,
        precio_unitario=None,
        precio_total=None,
        id_carrito=None,
        id_color_producto=None
    ):
        self.id_producto_carrito = id_producto_carrito
        self.fecha_añadido = fecha_añadido
        self.cantidad = cantidad
        self.talla = talla
        self.precio_unitario = precio_unitario
        self.precio_total = precio_total
        self.id_carrito = id_carrito
        self.id_color_producto = id_color_producto
