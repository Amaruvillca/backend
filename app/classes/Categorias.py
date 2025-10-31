from app.classes.Activerecord import Activerecord


class Categorias(Activerecord):
    TABLA = 'categoria'
    nombre_id = 'id_categoria'
    columnas_db = [
        'id_categoria', 'nombre', 'descripcion', 'imagen', 'estado'
    ]
    errores = [] 
    def __init__(self, id_categoria=None, nombre=None, descripcion=None,
                 imagen=None, estado=None):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.estado = estado

  