import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
load_dotenv()

class Conexion:
    
    DATABASE = os.getenv('DB_NAME', 'tienda_online')
    USERNAME = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_PORT = int(os.getenv('DB_PORT', '5430'))
    HOST = os.getenv('DB_HOST', 'localhost')
    POOL_SIZE = int(os.getenv('POOL_SIZE', '3'))
    POOL_NAME = 'tienda_online_pool'
    pool = None

    @classmethod
    def obtener_pool(cls):
        if cls.pool is None:  
            try:
                cls.pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=cls.POOL_SIZE,
                    host=cls.HOST,
                    port=cls.DB_PORT,
                    database=cls.DATABASE,
                    user=cls.USERNAME,
                    password=cls.PASSWORD
                )
                print("✅ Pool de conexiones PostgreSQL creado exitosamente")
                return cls.pool
            except Exception as e:
                print(f'❌ Ocurrió un error al obtener pool de PostgreSQL: {e}')
                raise
        return cls.pool
    
    @classmethod
    def obtener_conexion(cls):
        
        try:
            pool = cls.obtener_pool()
            conexion = pool.getconn()
            return conexion
        except Exception as e:
            print(f'❌ Error al obtener conexión del pool: {e}')
            raise
    
    @classmethod
    def liberar_conexion(cls, conexion):
        try:
            pool = cls.obtener_pool()
            pool.putconn(conexion)
            print(f'✅ Conexión liberada al pool')
            
        except Exception as e:
            print(f'❌ Error al liberar conexión: {e}')
            # Cerrar la conexión si no se puede regresar al pool
            conexion.close()

    @classmethod
    def cerrar_pool(cls):
        if cls.pool:
            cls.pool.closeall()
            print("✅ Pool de conexiones cerrado")