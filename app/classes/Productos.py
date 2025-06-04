from app.classes.Activerecord import Activerecord

class Producto(Activerecord):
    TABLA = 'producto'  
    nombre_id = 'id_producto'
    columnas_db = [
        'id_producto', 'nombre', 'descripcion', 'imagen', 'fecha_creacion',
        'genero', 'precio', 'para', 'id_sucursal', 'id_categoria'
    ]
    errores = [] 

    def __init__(self, id_producto=None, nombre=None, descripcion=None, imagen=None,
                 fecha_creacion=None, genero=None, precio=None, para=None,
                 id_sucursal=None, id_categoria=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.fecha_creacion = fecha_creacion
        self.genero = genero
        self.precio = precio
        self.para = para
        self.id_sucursal = id_sucursal
        self.id_categoria = id_categoria

    def validar(self) -> bool:
        self.errores = []
        if not self.nombre:
            self.errores.append("El nombre es obligatorio.")
        if not self.precio or self.precio <= 0:
            self.errores.append("El precio debe ser un número positivo.")
        if not self.id_sucursal:
            self.errores.append("La sucursal es obligatoria.")
        if not self.id_categoria:
            self.errores.append("La categoría es obligatoria.")
        if not self.genero:
            self.errores.append("El género es obligatorio.")
        if not self.descripcion:
            self.errores.append("La descripción es obligatoria.")
        if not self.imagen:
            self.errores.append("La imagen es obligatoria.")
        if not self.fecha_creacion:
            self.errores.append("La fecha de creación es obligatoria.")
        if not self.para:
            self.errores.append("El campo 'para' es obligatorio.")
        if self.errores:
            print(f"Errores de validación: {self.errores}")
            return False
        return len(self.errores) == 0
    