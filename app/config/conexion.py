import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
load_dotenv()

print("🔍 DEBUG - Variables de entorno cargadas:")
print(f"DB_HOST: '{os.getenv('DB_HOST')}'")
print(f"DB_PORT: '{os.getenv('DB_PORT')}'") 
print(f"DB_USER: '{os.getenv('DB_USER')}'")
print(f"DB_NAME: '{os.getenv('DB_NAME')}'")

class Conexion:
   # DATABASE = os.getenv('DB_NAME', 'tienda2')  # Valor por defecto 'tienda2'
    #USERNAME = os.getenv('DB_USER', 'postgres') # Valor por defecto 'postgres'
    #PASSWORD = os.getenv('DB_PASSWORD', 'root') # Valor por defecto 'root'
    #DB_PORT = int(os.getenv('DB_PORT', '5432')) # PostgreSQL usa puerto 5432 por defecto
    #HOST = os.getenv('DB_HOST', 'localhost')    # Valor por defecto 'localhost'
    #POOL_SIZE = int(os.getenv('POOL_SIZE', '30')) # Tamaño del pool
    #POOL_NAME = 'tienda_online_pool' # Nombre del pool (psycopg2 no usa nombre)
    #pool = None
    
    DATABASE = 'tienda2'  # Valor por defecto 'tienda2'
    USERNAME = 'root' # Valor por defecto 'postgres'
    PASSWORD = 'root' # Valor por defecto 'root'
    DB_PORT = 5432 # PostgreSQL usa puerto 5432 por defecto
    HOST = 'localhost'    # Valor por defecto 'localhost'
    POOL_SIZE = 30 # Tamaño del pool
    POOL_NAME = 'tienda_online_pool' # Nombre del pool (psycopg2 no usa nombre)
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