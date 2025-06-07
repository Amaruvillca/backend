from app.classes import Activerecord


class Cliente(Activerecord):
    TABLA = 'cliente'
    CAMPOS = ['id_cliente', 'Uid', 'nombres', 'ap_paterno', 'ap_materno', 'ci', 'fcm_token',
              'email', 'password', 'celular', 'direccion', 'fecha_registro', 'preferencias',
              'latitud', 'longitud', 'imagen_cliente']
    errores = [] 
    
    def __init__(self, id_cliente=None, Uid=None, nombres=None, ap_paterno=None, ap_materno=None,
                 ci=None, fcm_token=None, email=None, password=None, celular=None, direccion=None,
                 fecha_registro=None, preferencias=None, latitud=None, longitud=None, imagen_cliente=None):
        self.id_cliente = id_cliente
        self.Uid = Uid
        self.nombres = nombres
        self.ap_paterno = ap_paterno
        self.ap_materno = ap_materno
        self.ci = ci
        self.fcm_token = fcm_token
        self.email = email
        self.password = password
        self.celular = celular
        self.direccion = direccion
        self.fecha_registro = fecha_registro
        self.preferencias = preferencias
        self.latitud = latitud
        self.longitud = longitud
        self.imagen_cliente = imagen_cliente
