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
            conexion.close()

    @classmethod
    def all(cls) -> List:
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                query = f'SELECT * FROM {cls.TABLA} ORDER BY {cls.nombre_id} DESC'
                cursor.execute(query)
                resultados = cursor.fetchall()
                return [cls.crear_objeto(fila) for fila in resultados]
        except Exception as e:
            print(f'Error in all(): {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)

            
            
    @classmethod
    def consultar_sql(cls, query: str) -> List[Dict]:

        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
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
                query = f"INSERT INTO {self.TABLA} ({columns}) VALUES ({placeholders})"
                logger.debug("Query SQL: %s", query)
                logger.debug("Valores: %s", list(atributos.values()))
                cursor.execute(query, list(atributos.values()))
                conexion.commit()
                
              
                setattr(self, self.nombre_id, cursor.lastrowid)
                return True
        except Exception as e:
            print(f'Error in _insertar(): {e}')
            logger.debug(f'Error in _insertar(): {e}')
            
            
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
                
                query = f"UPDATE {self.TABLA} SET {set_clause} WHERE {self.nombre_id} = %s LIMIT 1"
                cursor.execute(query, values)
                conexion.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f'Error in _actualizar(): {e}')
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
            with conexion.cursor(dictionary=True) as cursor:
                query = f"SELECT {obtener} FROM {tabla} WHERE {entidad} = %s"
                cursor.execute(query, (parametro,))
                resultado = cursor.fetchone()
                return resultado.get(obtener, '') if resultado else ''
        except Exception as e:
            print(f'Error in buscar_claves(): {e}')
            return ''
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def mostrar_datos(cls, id: Union[int, str]) -> Dict:
        
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE {cls.nombre_id} = %s"
                cursor.execute(query, (id,))
                return cursor.fetchone() or {}
        except Exception as e:
            print(f'Error in mostrar_datos(): {e}')
            return {}
        finally:
            cls.liberar_conexion(conexion)

    @classmethod
    def find(cls, id: Union[int, str]):
        
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(dictionary=True) as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE {cls.nombre_id} = %s"
                cursor.execute(query, (id,))
                registro = cursor.fetchone()
                return cls.crear_objeto(registro) if registro else None
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
            with conexion.cursor(dictionary=True) as cursor:
                query = f"SELECT * FROM {cls.TABLA} WHERE id_cuenta = %s ORDER BY {cls.nombre_id} DESC"
                cursor.execute(query, (id_cuenta,))
                return cursor.fetchall()
        except Exception as e:
            print(f'Error in asociados_cuenta(): {e}')
            return []
        finally:
            cls.liberar_conexion(conexion)
    @classmethod   
    def crear_token(cls,data: dict) -> str:
        datos_a_codificar = data.copy()
        expiracion = datetime.utcnow() + timedelta(minutes=cls.DURACION_TOKEN_MINUTOS)
        datos_a_codificar.update({"exp": expiracion})
        token_jwt = jwt.encode(datos_a_codificar, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token_jwt
    
    @classmethod
    def verificar_token(cls,token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expirado")
        except jwt.InvalidTokenError:
            raise Exception("Token inválido")