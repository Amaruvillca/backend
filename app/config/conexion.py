from mysql.connector import pooling
from mysql.connector import Error

class Conexion:
    #DATABASE = 'tienda'
    DATABASE = 'tienda2'
    USERNAME = 'root'
    PASSWORD = 'root'
    DB_PORT = '3306'
    HOST = 'localhost'
    POOL_SIZE =30
    POOL_NAME = 'tienda_online'
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
    

    
