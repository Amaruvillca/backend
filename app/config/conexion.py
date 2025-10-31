from mysql.connector import pooling
import os
from dotenv import load_dotenv
from mysql.connector import pooling
from mysql.connector import Error
load_dotenv()

print("🔍 DEBUG - Variables de entorno cargadas:")
print(f"DB_HOST: '{os.getenv('DB_HOST')}'")
print(f"DB_PORT: '{os.getenv('DB_PORT')}'") 
print(f"DB_USER: '{os.getenv('DB_USER')}'")
print(f"DB_NAME: '{os.getenv('DB_NAME')}'")

class Conexion:
    #DATABASE = 'tienda'
    DATABASE = os.getenv('DB_NAME', 'tienda2')  # Valor por defecto 'tienda2'
    USERNAME = os.getenv('DB_USER', 'root')     # Valor por defecto 'root'
    PASSWORD = os.getenv('DB_PASSWORD', 'root') # Valor por defecto 'root'
    DB_PORT = int(os.getenv('DB_PORT', '3306')) # Convertir a entero
    HOST = os.getenv('DB_HOST', 'localhost')    # Valor por defecto 'localhost'
    POOL_SIZE = int(os.getenv('POOL_SIZE', '30')) # Tamaño del pool
    POOL_NAME = os.getenv('POOL_NAME', 'tienda_online') # Nombre del pool
    pool = None

    @classmethod
    def obtener_pool(cls):
        if cls.pool is None:  
            try:
                cls.pool = pooling.MySQLConnectionPool(
                    pool_name=cls.POOL_NAME,
                    pool_size=cls.POOL_SIZE,
                    host=cls.HOST,
                    port=cls.DB_PORT,
                    database=cls.DATABASE,
                    user=cls.USERNAME,
                    password=cls.PASSWORD
                )
                return cls.pool
            except Error as e:
                print(f'Ocurrio un error al obtener pool: {e}')
                raise
        return cls.pool
    
    @classmethod
    def obtener_conexion(cls):
        pool = cls.obtener_pool()
        return pool.get_connection()
    
    @classmethod
    def liberar_conexion(cls,conexion):
        conexion.close()
    

    
