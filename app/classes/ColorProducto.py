from app.classes.Activerecord import Activerecord

from psycopg2.extras import DictCursor
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
        
    @classmethod
    def buscar_descripcion_e_imagen(cls, id_color_producto: int) -> list[str]:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                consulta = f"""
                    SELECT descripcion, imagen 
                    FROM {cls.TABLA} 
                    WHERE {cls.nombre_id} = %s 
                    LIMIT 1
                """
                cursor.execute(consulta, (id_color_producto,))
                resultado = cursor.fetchone()
    
                if resultado:
                    descripcion = resultado.get('descripcion', '')
                    imagen = resultado.get('imagen', '')
                    return [descripcion, imagen]
                else:
                    return []
        except Exception as e:
            print(f"Error en buscar_descripcion_e_imagen: {e}")
            return []
        finally:
            cls.liberar_conexion(conexion)
    
