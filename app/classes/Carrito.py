from app.classes import Activerecord


class Carrito(Activerecord):
    
    TABLA = 'carrito'
    CAMPOS = [
        'id_carrito',
        'fecha_creacion',
        'estado',
        'id_cliente',
    ]
    errores = []

    def __init__(self, id_carrito=None, fecha_creacion=None, id_usuario=None, estado=None, id_cliente=None):
        self.id_carrito = id_carrito
        self.fecha_creacion = fecha_creacion
        self.id_usuario = id_usuario
        self.estado = estado
        self.id_cliente = id_cliente
