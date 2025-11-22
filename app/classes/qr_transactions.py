
import datetime
from app.classes.Activerecord import Activerecord
from psycopg2.extras import DictCursor

from app.config.gmail_client import GmailClient
from app.classes.cod_proceso_pago import CodProcesoPago
class QrTransactions(Activerecord):
    
    TABLA = 'qr_transactions'  
    nombre_id = 'id_qr_transaction'
    columnas_db = [
        'id_qr_transaction', 'nro_ach', 'fecha_transaccion', 'hora_transaccion', 'tipo_operacion',
        'nro_cuenta_origen', 'nombre_del_origen', 'banco_origen', 'nro_cuenta_destino', 'nombre_beneficiario','banco_destino',
        'monto', 'moneda', 'nro_orden_ach', 'glosa', 'monto_faltante', 'id_carrito'
    ]
    errores = [] 
    def __init__(self,id_qr_transaction=None, nro_ach=None, fecha_transaccion=None, hora_transaccion=None, tipo_operacion=None,
                 nro_cuenta_origen=None, nombre_del_origen=None, banco_origen=None, nro_cuenta_destino=None, nombre_beneficiario=None, banco_destino=None,
                 monto=None, moneda=None, nro_orden_ach=None, glosa=None, monto_faltante=None, id_carrito=None):
        self.id_qr_transaction = id_qr_transaction
        self.nro_ach = nro_ach
        self.fecha_transaccion = fecha_transaccion
        self.hora_transaccion = hora_transaccion
        self.tipo_operacion = tipo_operacion
        self.nro_cuenta_origen = nro_cuenta_origen
        self.nombre_del_origen = nombre_del_origen
        self.banco_origen = banco_origen
        self.nro_cuenta_destino = nro_cuenta_destino
        self.nombre_beneficiario = nombre_beneficiario
        self.banco_destino = banco_destino
        self.monto = monto
        self.moneda = moneda
        self.nro_orden_ach = nro_orden_ach
        self.glosa = glosa
        self.monto_faltante = monto_faltante
        self.id_carrito = id_carrito
        
    @classmethod
    def crear_desde_dict(cls, data_dict):
        return cls(
            id_qr_transaction=data_dict.get('id_qr_transaction'),
            nro_ach=data_dict.get('nro_ach'),
            fecha_transaccion=data_dict.get('fecha_transaccion'),
            hora_transaccion=data_dict.get('hora_transaccion'),
            tipo_operacion=data_dict.get('tipo_operacion'),
            nro_cuenta_origen=data_dict.get('nro_cuenta_origen'),
            nombre_del_origen=data_dict.get('nombre_del_origen'),
            banco_origen=data_dict.get('banco_origen'),
            nro_cuenta_destino=data_dict.get('nro_cuenta_destino'),
            nombre_beneficiario=data_dict.get('nombre_beneficiario'),
            banco_destino=data_dict.get('banco_destino'),
            monto=data_dict.get('monto'),
            moneda=data_dict.get('moneda'),
            nro_orden_ach=data_dict.get('nro_orden_ach'),
            glosa=data_dict.get('glosa'),
            monto_faltante=data_dict.get('monto_faltante'),
            id_carrito=data_dict.get('id_carrito')
        )
        
    

    @classmethod
    def procesar_qr_transaction(cls, id_carrito: int, uid: str,glosa: str):
        
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                #verificar que el carrito pertenezca al uid y esté en estado pendiente o procesopago
                query = f"""
                    SELECT c.id_carrito,u.id_cliente  
                    FROM carrito c
                    JOIN cliente u ON c.id_cliente = u.id_cliente
                    WHERE c.id_carrito = %s AND u.uid = %s AND (c.estado = 'pendiente' OR c.estado = 'procesopago')
                    LIMIT 1
                """
                cursor.execute(query, (id_carrito, uid))
                resultado = cursor.fetchone()
                if not resultado:
                    print(f"No se encontró el carrito {id_carrito} para el UID {uid}")
                    return
                #verificar monto total a pagar 
                id_carrito = resultado['id_carrito']
                id_cliente = resultado['id_cliente']
                query = f"""
                    SELECT pc.id_carrito,u.fcm_token, SUM(pc.precio_total) AS MONTO_TOTAL
                    FROM productos_carrito pc
                    JOIN carrito c ON pc.id_carrito = c.id_carrito
                    JOIN cliente u ON c.id_cliente = u.id_cliente
                    WHERE pc.id_carrito = %s
                    GROUP BY pc.id_carrito, u.fcm_token
                """
                cursor.execute(query, (id_carrito,))
                resultado = cursor.fetchone()
                if not resultado:
                    print(f"No se encontraron transacciones QR para el carrito {id_carrito}")
                    return
                monto_total = resultado['monto_total']
                fcm_token = resultado['fcm_token']
                fecha_hora_actual = datetime.now()
                #guardar glosa
                proceso_pago = CodGlosa()
                proceso_pago.codigo = proceso_pago
                if not proceso_pago.guardar():
                    print(f"error al guardar glosa para el carrito {id_carrito}")
                    return
                
                #buscar qr transaction
                gmail = GmailClient()
                gmail.test_connection()
                
                emails = gmail.list_emails(max_results=5)
                for e in emails:
                    print(f"📬 {e['from']} - {e['subject']} ({e['date']})")
                    
                #ACH7@bancounion.com.bo
                # Buscar emails de un remitente específico
                emails = gmail.list_emails(query='from:ACH7@bancounion.com.bo')
                

                print(f"Procesando transacción QR para carrito {id_carrito} y UID {uid}")
        except Exception as e:
            print(f"Error en procesar_qr_transaction: {e}")
            
        finally:
            cls.liberar_conexion(conexion)
    

    
    
