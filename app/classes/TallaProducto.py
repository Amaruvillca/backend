from app.classes.Activerecord import Activerecord


class TallaProducto(Activerecord):
    TABLA = 'talla_producto'
    nombre_id = 'id_talla_producto'
    columnas_db = [
        'id_talla_producto', 'talla', 'stock', 'descripcion', 'id_color_producto'
    ]
    errores = []

    def __init__(self, id_talla_producto = None, talla = None, stock = None, descripcion = None, id_color_producto = None):
        self.id_talla_producto = id_talla_producto
        self.talla = talla
        self.stock = stock
        self.descripcion = descripcion
        self.id_color_producto = id_color_producto