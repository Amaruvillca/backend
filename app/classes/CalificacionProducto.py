from app.classes.Activerecord import Activerecord


class CalificacionProducto(Activerecord):
    TABLA = 'calificacion_producto'
    nombre_id = 'id_calificacion'
    columnas_db = [
        'id_calificacion', 'puntuacion', 'fecha', 'id_cliente',
        'id_producto', 'comentario'
    ]
    errores = []
    def __init__(self, id_calificacion = None, puntuacion=None, fecha=None,
                 id_cliente=None, id_producto=None, comentario=None):
        self.id_calificacion = id_calificacion
        self.puntuacion = puntuacion
        self.fecha = fecha
        self.id_cliente = id_cliente
        self.id_producto = id_producto
        self.comentario = comentario

    