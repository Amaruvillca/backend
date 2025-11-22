# app/classes/activerecord.py
from abc import ABC, abstractmethod
import logging
from app.config.conexion import Conexion
from typing import List, Dict, Union, Optional
import jwt
from datetime import datetime, timedelta
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Activerecord(ABC):
    SECRET_KEY = "faceapp2025"
    ALGORITHM = "HS256"
    DURACION_TOKEN_MINUTOS = 60
    TABLA = '' 
    nombre_id = 'id' 
    columnas_db = []  
    errores = []  

    @classmethod
    def obtener_conexion(cls):
        return Conexion.obtener_conexion()
    
    @classmethod
    def liberar_conexion(cls, conexion):
        if conexion:
            # Para PostgreSQL con pool, usar putconn en lugar de close
            #if hasattr(cls, 'pool') and cls.pool:
                Conexion.liberar_conexion(conexion)
            #else:
                #conexion.putconn(conexion)

    @classmethod
    def all(cls) -> List:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f'SELECT * FROM {cls.TABLA} ORDER BY {cls.nombre_id} DESC'
                cursor.execute(query)
                resultados = cursor.fetchall()
                # Convertir a lista de diccionarios
                column_names = [desc[0] for desc in cursor.description]
                dict_resultados = [dict(zip(column_names, row)) for row in resultados]
                return [cls.crear_objeto(fila) for fila in dict_resultados]
        except Exception as e:
            print(f'Error in all(): {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def consultar_sql(cls, query: str) -> List[Dict]:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(query)
                resultados = cursor.fetchall()
                # Convertir a lista de diccionarios
                column_names = [desc[0] for desc in cursor.description]
                return [dict(zip(column_names, row)) for row in resultados]
        except Exception as e:
            print(f'Error in consultar_sql(): {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def crear_objeto(cls, registro: Dict):
        obj = cls()
        for key, value in registro.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

    def guardar(self) -> bool:
        if getattr(self, self.nombre_id, None) is None:
            return self._insertar()
        else:
            return self._actualizar()

    def _insertar(self) -> bool:
        atributos = self.sanitizar_atributos()
        if not atributos:
            return False

        conexion = self.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                columns = ', '.join(atributos.keys())
                placeholders = ', '.join(['%s'] * len(atributos))
                # PostgreSQL usa RETURNING para obtener el ID insertado
                query = f"INSERT INTO {self.TABLA} ({columns}) VALUES ({placeholders}) RETURNING {self.nombre_id}"
                logger.debug("Query SQL: %s", query)
                logger.debug("Valores: %s", list(atributos.values()))
                cursor.execute(query, list(atributos.values()))
                # Obtener el ID generado
                nuevo_id = cursor.fetchone()[0]
                conexion.commit()
                
                # Asignar el ID al objeto
                setattr(self, self.nombre_id, nuevo_id)
                return True
        except Exception as e:
            print(f'Error in _insertar(): {e}')
            logger.debug(f'Error in _insertar(): {e}')
            conexion.rollback()
            return False
        finally:
            self.liberar_conexion(conexion)

    def _actualizar(self) -> bool:
        id_val = getattr(self, self.nombre_id)
        if not id_val:
            return False

        atributos = self.sanitizar_atributos()
        if not atributos:
            return False

        conexion = self.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                set_clause = ', '.join([f"{key} = %s" for key in atributos.keys()])
                values = list(atributos.values())
                values.append(id_val)
                
                # PostgreSQL no usa LIMIT en UPDATE
                query = f"UPDATE {self.TABLA} SET {set_clause} WHERE {self.nombre_id} = %s"
                cursor.execute(query, values)
                conexion.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f'Error in _actualizar(): {e}')
            conexion.rollback()
            return False
        finally:
            self.liberar_conexion(conexion)

    @classmethod
    def borrar(cls, id: Union[int, str]) -> bool:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"DELETE FROM {cls.TABLA} WHERE {cls.nombre_id} = %s"
                cursor.execute(query, (id,))
                conexion.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f'Error in borrar(): {e}')
            conexion.rollback()
            return False
        finally:
            cls.liberar_conexion(conexion)

    def atributos(self) -> Dict:
        attrs = {}
        for columna in self.columnas_db:
            if columna == self.nombre_id:
                continue
            if hasattr(self, columna):
                attrs[columna] = getattr(self, columna)
        return attrs

    def sanitizar_atributos(self) -> Dict:
        return self.atributos()

    @classmethod
    def get_errores(cls) -> List:
        return cls.errores

    def validar(self) -> bool:
        self.errores = []
        return len(self.errores) == 0

    @classmethod
    def buscar_claves(cls, obtener: str, tabla: str, entidad: str, parametro: str) -> str:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"SELECT {obtener} FROM {tabla} WHERE {entidad} = %s"
                cursor.execute(query, (parametro,))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else ''
        except Exception as e:
            print(f'Error in buscar_claves(): {e}')
            return ''
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def mostrar_datos(cls, id: Union[int, str]) -> Dict:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE {cls.nombre_id} = %s"
                cursor.execute(query, (id,))
                resultado = cursor.fetchone()
                if resultado:
                    column_names = [desc[0] for desc in cursor.description]
                    return dict(zip(column_names, resultado))
                return {}
        except Exception as e:
            print(f'Error in mostrar_datos(): {e}')
            return {}
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def find(cls, id: Union[int, str]):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE {cls.nombre_id} = %s"
                cursor.execute(query, (id,))
                registro = cursor.fetchone()
                if registro:
                    column_names = [desc[0] for desc in cursor.description]
                    registro_dict = dict(zip(column_names, registro))
                    return cls.crear_objeto(registro_dict)
                return None
        except Exception as e:
            print(f'Error in find(): {e}')
            return None
        finally:
            cls.liberar_conexion(conexion)

    def sincronizar(self, args: Dict = {}):
        for key, value in args.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

    @classmethod
    def contar_datos(cls) -> int:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"SELECT COUNT(*) FROM {cls.TABLA}"
                cursor.execute(query)
                return cursor.fetchone()[0]
        except Exception as e:
            print(f'Error in contar_datos(): {e}')
            return 0
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def asociados_cuenta(cls, id_cuenta: Union[int, str]) -> List[Dict]:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE id_cuenta = %s ORDER BY {cls.nombre_id} DESC"
                cursor.execute(query, (id_cuenta,))
                resultados = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return [dict(zip(column_names, row)) for row in resultados]
        except Exception as e:
            print(f'Error in asociados_cuenta(): {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

    @classmethod   
    def crear_token(cls, data: dict) -> str:
        datos_a_codificar = data.copy()
        expiracion = datetime.utcnow() + timedelta(minutes=cls.DURACION_TOKEN_MINUTOS)
        datos_a_codificar.update({"exp": expiracion})
        token_jwt = jwt.encode(datos_a_codificar, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token_jwt
    
    @classmethod
    def verificar_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expirado")
        except jwt.InvalidTokenError:
            raise Exception("Token inválido")
    
    @classmethod
    def enviar_notificacion(cls, token: str, titulo: str, cuerpo: str,image: str = None) -> bool:
        try:
            from app.config.firebase_config import FirebaseConfig
            FirebaseConfig.initialize_firebase()
            messaging = FirebaseConfig.get_messaging()
            
            message = messaging.Message(
                notification=messaging.Notification(
                   image=image,
                    title=titulo,
                    body=cuerpo,
                    
                ),
                token=token
            )
            
            response = messaging.send(message)
            logger.info(f"Notificación enviada: {response}")
            return True
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return False
    
    
        