from app.classes.Activerecord import Activerecord
import datetime
import psycopg2
from psycopg2.extras import DictCursor

class Cliente(Activerecord):
    nombre_id = 'id_cliente'
    TABLA = 'cliente'
    columnas_db = ['id_cliente', 'uid', 'nombres', 'ap_paterno', 'ap_materno', 'ci', 'fcm_token',
              'email', 'password', 'celular', 'direccion', 'fecha_registro', 'preferencias',
              'latitud', 'longitud', 'imagen_cliente']
    errores = [] 
    
    def __init__(self, id_cliente=None, uid=" ", nombres=" ", ap_paterno=" ", ap_materno=" ",
                 ci=0, fcm_token=" ", email=" ", password=" ", celular="00", direccion=" ",
                 fecha_registro=None, preferencias=" ", latitud=0.0, longitud=0.0, imagen_cliente=" "):
        self.id_cliente = id_cliente
        self.uid = uid
        self.nombres = nombres
        self.ap_paterno = ap_paterno
        self.ap_materno = ap_materno
        self.ci = ci
        self.fcm_token = fcm_token
        self.email = email
        self.password = password
        self.celular = celular
        self.direccion = direccion
        # Si no se proporciona fecha_registro, usar la fecha actual como string
        if fecha_registro is None:
            self.fecha_registro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.fecha_registro = fecha_registro
        self.preferencias = preferencias
        self.latitud = latitud
        self.longitud = longitud
        self.imagen_cliente = imagen_cliente

    def validar(self) -> bool:
           """Valida los datos antes de guardar"""
           self.errores = []

           

           return len(self.errores) == 0
       
    @classmethod
    def find_by_uid(cls, uid: str):
        """
        Busca un cliente por su uid y devuelve una instancia de Cliente si lo encuentra.
        Similar al método find() pero buscando por el campo uid en lugar de id_cliente.
        
        Args:
            uid (str): El uid del cliente a buscar
            
        Returns:
            Cliente: Una instancia de Cliente si se encuentra, None si no se encuentra
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE uid = %s"
                cursor.execute(query, (uid,))
                registro = cursor.fetchone()
                return cls.crear_objeto(registro) if registro else None
        except Exception as e:
            print(f'Error en find_by_uid(): {e}')
            return None
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def update_imagen_by_uid(cls, uid: str, nueva_imagen: str) -> bool:
        """
        Actualiza el atributo imagen_cliente del registro identificado por uid.

        Args:
            uid (str): UID del cliente cuyo avatar se modificará.
            nueva_imagen (str): Ruta o URL de la nueva imagen.

        Returns:
            bool: True si se actualizó algún registro, False en caso contrario.
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"UPDATE {cls.TABLA} SET imagen_cliente = %s WHERE uid = %s"
                cursor.execute(query, (nueva_imagen, uid))
                conexion.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en update_imagen_by_uid(): {e}")
            return False
        finally:
            cls.liberar_conexion(conexion)
            


    @classmethod
    def has_imagen(cls, uid: str) -> bool:
        conexion = cls.obtener_conexion()
        try:
            # Usar DictCursor explícitamente para PostgreSQL
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                query = f"SELECT imagen_cliente FROM {cls.TABLA} WHERE uid = %s"
                cursor.execute(query, (uid,))
                fila = cursor.fetchone()
    
                if not fila:
                    return False
    
                valor = fila["imagen_cliente"]
                
                if not valor:
                    return False
                    
                if isinstance(valor, str) and not valor.strip():
                    return False
                    
                return True
                    
        except Exception as e:
            print(f"💥 Error en has_imagen(): {e}")
            return False
        finally:
            if conexion:
                cls.liberar_conexion(conexion)

    @classmethod
    def find_id_by_uid(cls, uid: str) -> int:
        """
        Busca el id_cliente de un cliente a partir de su UID.

        Args:
            uid (str): El UID del cliente.

        Returns:
            str: El ID del cliente si se encuentra, cadena vacía si no se encuentra o hay error.
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                query = f"SELECT id_cliente FROM {cls.TABLA} WHERE uid = %s LIMIT 1"
                cursor.execute(query, (uid,))
                resultado = cursor.fetchone()
                return resultado["id_cliente"] if resultado else 0
        except Exception as e:
            print(f"Error en find_id_by_uid(): {e}")
            return ""
        finally:
            cls.liberar_conexion(conexion)
    
    @classmethod
    def actualizar_fscm(cls, uid: str, fcm_token: str) -> bool:
        """
        Actualiza el token FCM de un cliente identificado por su UID.

        Args:
            uid (str): El UID del cliente.
            fcm_token (str): El nuevo token FCM.

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario.
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"UPDATE {cls.TABLA} SET fcm_token = %s WHERE uid = %s"
                cursor.execute(query, (fcm_token, uid))
                conexion.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en actualizar_fscm(): {e}")
            return False
        finally:
            cls.liberar_conexion(conexion)

