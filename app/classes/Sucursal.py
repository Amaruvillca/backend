from app.classes.Activerecord import Activerecord


class Sucursal(Activerecord):
    TABLA = 'sucursal'
    nombre_id = 'id_sucursal'
    columnas_db = [
        'id_sucursal', 'nombre', 'imagen1', 'imagen2', 'imagen3',
        'telefono', 'fecha_apertura', 'direccion', 'ciudad',
        'latitud', 'longitud', 'estado'
    ]
    errores = [] 
    def __init__(self, id_sucursal=None, nombre=None,
                 imagen1=None, imagen2=None, imagen3=None,
                 telefono=None, fecha_apertura=None, direccion=None,
                 ciudad=None, latitud=None, longitud=None, estado=None):
        self.id_sucursal = id_sucursal
        self.nombre = nombre
        self.direccion = direccion
        self.imagen1 = imagen1
        self.imagen2 = imagen2
        self.imagen3 = imagen3
        self.telefono = telefono
        self.fecha_apertura = fecha_apertura
        self.ciudad = ciudad
        self.latitud = latitud
        self.longitud = longitud
        self.estado = estado