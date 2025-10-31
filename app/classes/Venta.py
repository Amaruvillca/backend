from app.classes import Activerecord


class Venta(Activerecord):
    TABLA = 'venta'
    CAMPOS = ['id_venta', 'fecha_creacion', 'estado', 'id_personal']
    errores = []
   
    def __init__(self, id_venta=None, fecha_creacion=None, estado=None, id_personal=None):
        super().__init__()
        self.id_venta = id_venta
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        self.id_personal = id_personal
