from app.classes import Activerecord


class ProductoVenta(Activerecord):
    TABLA = 'producto_venta'
    CAMPOS = [
        'id_producto_venta',
        'fecha_añadido',
        'cantidad',
        'talla',
        'precio_unitario',
        'precio_total',
        'id_venta',
        'id_color_producto'
    ]
    errores = []

    def __init__(
        self,
        id_producto_venta=None,
        fecha_añadido=None,
        cantidad=None,
        talla=None,
        precio_unitario=None,
        precio_total=None,
        id_venta=None,
        id_color_producto=None
    ):
        self.id_producto_venta = id_producto_venta
        self.fecha_añadido = fecha_añadido
        self.cantidad = cantidad
        self.talla = talla
        self.precio_unitario = precio_unitario
        self.precio_total = precio_total
        self.id_venta = id_venta
        self.id_color_producto = id_color_producto
