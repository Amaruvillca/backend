from app.classes.Activerecord import Activerecord
from psycopg2.extras import DictCursor

class Paga(Activerecord):
    TABLA = 'paga'
    nombre_id = 'id_paga'
    columnas_db = [
        'id_paga',
        'monto_total',
        'monto_pagado',
        'fecha_pago',
        'id_cliente',
        'id_carrito'
    ]
    errores = []

    def __init__(
        self,
        id_paga=None,
        monto_total=None,
        monto_pagado=None,
        fecha_pago=None,
        id_cliente=None,
        id_carrito=None
    ):
        self.id_paga = id_paga
        self.monto_total = monto_total
        self.monto_pagado = monto_pagado
        self.fecha_pago = fecha_pago
        self.id_cliente = id_cliente
        self.id_carrito = id_carrito

    @classmethod
    def obtener_pagos_por_uid(cls, uid: str):
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                query = f"""SELECT p.* FROM {cls.TABLA} p
                INNER JOIN carrito c ON p.id_carrito = c.id_carrito
                INNER JOIN cliente cl ON c.id_cliente = cl.id_cliente
                WHERE cl.uid = %s
                AND c.estado = 'pagado'
                ORDER BY p.fecha_pago DESC
                """
                cursor.execute(query, (uid,))
                resultados = cursor.fetchall()
                return [cls(**fila) for fila in resultados]
        except Exception as e:
            print(f"Error al obtener pagos por UID: {e}")
            return []
        finally:
            cls.liberar_conexion(conexion)