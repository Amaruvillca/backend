from app.classes.Activerecord import Activerecord


class Carrito(Activerecord):
    
    TABLA = 'carrito'
    nombre_id = 'id_carrito'
    columnas_db = [
        'id_carrito',
        'fecha_creacion',
        'estado',
        'id_cliente',
    ]
    errores = []

    def __init__(self, id_carrito=None, fecha_creacion=None, estado=None, id_cliente=None):
        self.id_carrito = id_carrito
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        self.id_cliente = id_cliente

    @classmethod
    def obtener_estado_por_id(cls, id_carrito: int) -> str:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                query = f"SELECT estado FROM {cls.TABLA} WHERE {cls.nombre_id} = %s"
                cursor.execute(query, (id_carrito,))
                resultado = cursor.fetchone()
                return resultado['estado'] if resultado else "No encontrado"
        except Exception as e:
            print(f"Error al obtener el estado: {e}")
            return "Error"
        finally:
            cls.liberar_conexion(conexion)
            
    @classmethod
    def obtener_estado_por_cliente(cls, id_cliente: int) -> str:
        """
        Obtiene el estado del último carrito asociado a un cliente.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            str: Estado del carrito si se encuentra, "No encontrado" o "Error" si ocurre un problema.
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                query = f"""
                    SELECT estado FROM {cls.TABLA}
                    WHERE id_cliente = %s
                    ORDER BY id_carrito DESC
                    LIMIT 1
                """
                cursor.execute(query, (id_cliente,))
                resultado = cursor.fetchone()
                return resultado['estado'] if resultado else "No encontrado"
        except Exception as e:
            print(f"Error al obtener el estado por cliente: {e}")
            return "Error"
        finally:
            cls.liberar_conexion(conexion)


    @classmethod
    def obtener_ultimo_id_carrito_por_cliente(cls, id_cliente: int) -> int:
        """
        Devuelve el ID del último carrito creado por el cliente.
    
        Args:
            id_cliente (int): ID del cliente.
    
        Returns:
            int: El último ID de carrito encontrado, o 0 si no se encuentra o hay error.
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                query = f"""
                    SELECT id_carrito FROM {cls.TABLA}
                    WHERE id_cliente = %s
                    ORDER BY id_carrito DESC
                    LIMIT 1
                """
                cursor.execute(query, (id_cliente,))
                resultado = cursor.fetchone()
                return resultado['id_carrito'] if resultado else 0
        except Exception as e:
            print(f"Error al obtener el último ID de carrito: {e}")
            return 0
        finally:
            cls.liberar_conexion(conexion)
    