from app.classes import Activerecord


class Personal(Activerecord):
    TABLA = 'personal'
    CAMPOS = ['id_personal', 'nombres', 'ap_paterno', 'ap_materno', 'ci', 'email', 'password',
              'direccion', 'celular', 'tipo_personal', 'imagen_personal', 'estado', 'id_sucursal']
    errores = [] 
    def __init__(self, id_personal=None, nombres=None, ap_paterno=None, ap_materno=None, ci=None,
                 email=None, password=None, direccion=None, celular=None, tipo_personal=None, imagen_personal=None,
                 estado=None, id_sucursal=None):
        self.id_personal = id_personal
        self.nombres = nombres
        self.ap_paterno = ap_paterno
        self.ap_materno = ap_materno
        self.ci = ci
        self.email = email
        self.password = password
        self.celular = celular
        self.direccion = direccion
        self.tipo_personal = tipo_personal
        self.imagen_personal = imagen_personal
        self.estado = estado
        self.id_sucursal = id_sucursal