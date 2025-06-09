from app.classes.Activerecord import Activerecord


class ComentarioProducto(Activerecord):
    TABLA = 'comentario_producto'
    nombre_id = 'id_comentario'
    columnas_db = [
        'id_comentario', 'comentario', 'fecha', 'id_cliente', 'id_producto'
    ]
    errores = [] 

    def __init__(self, id_comentario=None, comentario=None, fecha=None, id_cliente=None, id_producto=None):
        self.id_comentario = id_comentario
        self.comentario = comentario
        self.fecha = fecha
        self.id_cliente = id_cliente
        self.id_producto = id_producto

    