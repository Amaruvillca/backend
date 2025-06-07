from app.classes.Activerecord import Activerecord


class ColorProducto(Activerecord):
    TABLA = 'color_producto'
    nombre_id = 'id_color_producto'
    columnas_db = [
        'id_color_producto', 'colores', 'cod_producto', 'descripcion', 'imagen', 'id_producto'
    ]
    errores = [] 
    def __init__(self, id_color_producto = None, colores = None, cod_producto = None, descripcion = None, imagen = None, id_producto = None):
        self.id_color_producto = id_color_producto
        self.colores = colores
        self.cod_producto = cod_producto
        self.descripcion = descripcion
        self.imagen = imagen
        self.id_producto = id_producto