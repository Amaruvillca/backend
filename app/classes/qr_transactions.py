import datetime
import threading
import time
import re
import uuid
from decimal import Decimal
from app.classes.Activerecord import Activerecord
from psycopg2.extras import DictCursor
from app.config.gmail_client import GmailClient
from app.classes.cod_proceso_pago import CodProcesoPago

class QrTransactions(Activerecord):
    
    TABLA = 'qr_transactions'  
    # ✅ CORREGIDO: Usar el nombre correcto de la columna ID
    nombre_id = 'id_qr_transactions'  # Cambiado de 'id_qr_transaction' a 'id_qr_transactions'
    columnas_db = [
        'id_qr_transactions', 'nro_ach', 'fecha_transaccion', 'hora_transaccion', 'tipo_operacion',
        'nro_cuenta_origen', 'nombre_del_origen', 'banco_origen', 'nro_cuenta_destino', 'nombre_beneficiario','banco_destino',
        'monto', 'moneda', 'nro_orden_ach', 'glosa', 'monto_faltante', 'id_carrito'
    ]
    errores = [] 
    
    def __init__(self, id_qr_transactions=None, nro_ach=None, fecha_transaccion=None, hora_transaccion=None, tipo_operacion=None,
                 nro_cuenta_origen=None, nombre_del_origen=None, banco_origen=None, nro_cuenta_destino=None, 
                 nombre_beneficiario=None, banco_destino=None, monto=None, moneda=None, nro_orden_ach=None, 
                 glosa=None, monto_faltante=None, id_carrito=None):
        # ✅ CORREGIDO: Usar el nombre correcto del ID
        self.id_qr_transactions = id_qr_transactions
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
            id_qr_transactions=data_dict.get('id_qr_transactions'),  # ✅ CORREGIDO
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
    def _buscar_y_procesar_transaccion(cls, codigo: str, id_carrito: int, fcm_token: str, monto_total):
        """
        Método que se ejecuta en el hilo para buscar y procesar transacciones
        """
        print(f"🧵 Hilo iniciado - Carrito: {id_carrito}, Monto: {monto_total}")
        
        try:
            gmail = GmailClient()
            
            # Test de conexión mejorado
            try:
                profile = gmail.service.users().getProfile(userId='me').execute()
                print(f"✅ Conectado a Gmail como: {profile.get('emailAddress', 'Unknown')}")
            except Exception as e:
                print(f"❌ No se pudo conectar a Gmail: {e}")
                cls._actualizar_estado_error(id_carrito, codigo, f"Error de conexión a Gmail: {str(e)}")
                return

            # Buscar por 5 minutos máximo
            tiempo_inicio = datetime.datetime.now()
            tiempo_fin = tiempo_inicio + datetime.timedelta(minutes=5)
            intentos = 0
            transaccion_encontrada = False
            
            while datetime.datetime.now() < tiempo_fin and not transaccion_encontrada:
                intentos += 1
                print(f"🔄 Intento {intentos} - Buscando transacción para carrito {id_carrito}, monto: {monto_total}")
                
                try:
                    # Buscar correos del banco
                    emails = gmail.search_emails(query='from:ACH7@bancounion.com.bo', max_results=30)
                    print(f"📧 Encontrados {len(emails)} correos en intento {intentos}")
                    
                    for i, email in enumerate(emails):
                        # Si ya encontramos transacción, salir inmediatamente
                        if transaccion_encontrada:
                            break
                            
                        # Obtener el cuerpo del email de manera segura
                        cuerpo = email.get('body', '')
                        if not cuerpo:
                            # Intentar obtener el cuerpo de otra manera
                            cuerpo = email.get('snippet', '') or email.get('plain_body', '') or ''
                        
                        print(f"📄 Procesando correo {i+1} - Tamaño cuerpo: {len(cuerpo)} caracteres")
                        
                        # Buscar si el correo contiene una transacción con el monto correcto
                        if cls._es_transaccion_valida(cuerpo, monto_total):
                            print(f"✅ ¡Transacción encontrada para carrito {id_carrito}!")
                            
                            # Extraer datos de la transacción
                            datos_transaccion = cls._extraer_datos_transaccion(cuerpo)
                            
                            # Guardar transacción en la base de datos
                            if cls._guardar_transaccion_encontrada(id_carrito, datos_transaccion, monto_total, codigo):
                                print(f"💰 Transacción guardada exitosamente para carrito {id_carrito}")
                                transaccion_encontrada = True
                                break  # Salir del bucle de correos
                            else:
                                print(f"❌ Error al guardar transacción, continuando búsqueda...")
                                # Continuar buscando en el siguiente correo
                    
                    # Si encontramos transacción, salir del bucle principal inmediatamente
                    if transaccion_encontrada:
                        print(f"🎯 Proceso completado - Hilo finalizado para carrito {id_carrito}")
                        break
                    
                    # Solo esperar si no encontramos transacción y aún hay tiempo
                    tiempo_restante = (tiempo_fin - datetime.datetime.now()).total_seconds()
                    if tiempo_restante > 0 and not transaccion_encontrada:
                        print(f"⏳ Esperando 30s... (Tiempo restante: {int(tiempo_restante/60)}m {int(tiempo_restante%60)}s)")
                        time.sleep(30)
                    else:
                        break
                        
                except Exception as e:
                    print(f"❌ Error en intento {intentos}: {e}")
                    # Solo esperar si no encontramos transacción y aún hay tiempo
                    if not transaccion_encontrada:
                        time.sleep(30)
            
            if not transaccion_encontrada:
                print(f"⏰ Tiempo agotado - No se encontró transacción para carrito {id_carrito} después de {intentos} intentos")
                cls._actualizar_estado_timeout(id_carrito, codigo)
            else:
                print(f"✅ Proceso finalizado exitosamente para carrito {id_carrito}")
            
        except Exception as e:
            print(f"❌ Error en hilo de búsqueda para carrito {id_carrito}: {e}")
            cls._actualizar_estado_error(id_carrito, codigo, f"Error en búsqueda: {str(e)}")
        finally:
            print(f"🔚 Hilo finalizado para carrito {id_carrito}")
    
    @classmethod
    def _es_transaccion_valida(cls, cuerpo_email: str, monto_total) -> bool:
        """
        Verifica si el correo contiene una transacción con el monto correcto
        """
        try:
            # Convertir monto_total a float si es Decimal
            if isinstance(monto_total, Decimal):
                monto_total_float = float(monto_total)
            else:
                monto_total_float = float(monto_total)
                
            print(f"🔍 Buscando transacción con monto: {monto_total_float}")
            
            # Buscar el monto en el correo - patrón específico para esta estructura HTML
            patron_monto = r'<span style="font-size: 13px; color: #1f497d;white-space: nowrap;"><b>Monto:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>'
            match_monto = re.search(patron_monto, cuerpo_email, re.IGNORECASE | re.DOTALL)
            
            if not match_monto:
                # Intentar con un patrón más simple por si falla el específico
                patron_monto_simple = r'Monto:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>'
                match_monto = re.search(patron_monto_simple, cuerpo_email, re.IGNORECASE | re.DOTALL)
                
            if not match_monto:
                # Último intento: buscar cualquier texto que contenga "Monto:"
                patron_monto_fallback = r'Monto[^:]*:\s*([^\n<]+)'
                match_monto = re.search(patron_monto_fallback, cuerpo_email, re.IGNORECASE)
                
            if not match_monto:
                print(f"❌ No se pudo encontrar el monto en el correo")
                return False
                
            monto_str = match_monto.group(1).strip()
            print(f"🔍 Monto encontrado en correo: '{monto_str}'")
            print(f"🔍 Monto esperado: {monto_total_float}")
            
            # Extraer solo el número del monto (eliminar "Bs", "Bolivianos", etc.)
            monto_match = re.search(r'(\d+\.?\d*)', monto_str)
            if not monto_match:
                print(f"❌ No se pudo extraer el valor numérico del monto")
                return False
                
            monto_transaccion = float(monto_match.group(1))
            print(f"🔍 Monto numérico extraído: {monto_transaccion}")
            
            # Verificar que los montos coincidan (con tolerancia pequeña por decimales)
            montos_coinciden = abs(monto_transaccion - monto_total_float) < 0.01
            
            if montos_coinciden:
                print(f"✅ ¡Montos coinciden! Transacción VÁLIDA")
                return True
            else:
                print(f"❌ Montos NO coinciden: Transacción={monto_transaccion}, Esperado={monto_total_float}")
                return False
                
        except Exception as e:
            print(f"❌ Error validando transacción: {e}")
            return False
    
    @classmethod
    def _convertir_fecha_formato_db(cls, fecha_str: str) -> str:
        """
        Convierte fecha de formato DD/MM/YYYY a YYYY-MM-DD para PostgreSQL
        """
        try:
            if not fecha_str:
                return None
                
            # Verificar si ya está en formato correcto
            if re.match(r'\d{4}-\d{2}-\d{2}', fecha_str):
                return fecha_str
                
            # Convertir de DD/MM/YYYY a YYYY-MM-DD
            partes = fecha_str.split('/')
            if len(partes) == 3:
                dia, mes, anio = partes
                # Si el año tiene solo 2 dígitos, asumimos siglo 20/21
                if len(anio) == 2:
                    anio = f"20{anio}" if int(anio) <= 50 else f"19{anio}"
                return f"{anio}-{mes}-{dia}"
            
            return fecha_str
        except Exception as e:
            print(f"❌ Error convirtiendo fecha '{fecha_str}': {e}")
            return fecha_str
    
    @classmethod
    def _extraer_datos_transaccion(cls, cuerpo_email: str) -> dict:
        """
        Extrae los datos de la transacción del cuerpo del email HTML
        """
        datos = {}
        
        patrones = {
            'nro_orden_ach': [
                r'Número de Orden ACH:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Número de Orden ACH[^:]*:\s*([^\n<]+)'
            ],
            'glosa': [
                r'Glosa:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Glosa[^:]*:\s*([^\n<]+)'
            ],
            'monto': [
                r'Monto:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Monto[^:]*:\s*([^\n<]+)'
            ],
            'moneda': [
                r'Moneda:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Moneda[^:]*:\s*([^\n<]+)'
            ],
            'fecha_transaccion': [
                r'Fecha de transacción:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Fecha de transacción[^:]*:\s*([^\n<]+)'
            ],
            'hora_transaccion': [
                r'Hora de transacción:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Hora de transacción[^:]*:\s*([^\n<]+)'
            ],
            'tipo_operacion': [
                r'Tipo de Operación:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Tipo de Operación[^:]*:\s*([^\n<]+)'
            ],
            'nro_cuenta_origen': [
                r'N° Cuenta de Origen:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'N° Cuenta de Origen[^:]*:\s*([^\n<]+)'
            ],
            'nombre_del_origen': [
                r'Nombre del Originante:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Nombre del Originante[^:]*:\s*([^\n<]+)'
            ],
            'banco_origen': [
                r'Banco Origen:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Banco Origen[^:]*:\s*([^\n<]+)'
            ],
            'nro_cuenta_destino': [
                r'N° Cuenta de Destino:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'N° Cuenta de Destino[^:]*:\s*([^\n<]+)'
            ],
            'nombre_beneficiario': [
                r'Nombre del Beneficiario:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Nombre del Beneficiario[^:]*:\s*([^\n<]+)'
            ],
            'banco_destino': [
                r'Banco Destino:</b>\s*</span>\s*</td>\s*<td[^>]*>\s*<span[^>]*>([^<]+)</span>',
                r'Banco Destino[^:]*:\s*([^\n<]+)'
            ]
        }
        
        for campo, patron_list in patrones.items():
            for patron in patron_list:
                match = re.search(patron, cuerpo_email, re.IGNORECASE | re.DOTALL)
                if match:
                    datos[campo] = match.group(1).strip()
                    break
        
        # ✅ CORREGIDO: Convertir fecha al formato de PostgreSQL
        if 'fecha_transaccion' in datos:
            datos['fecha_transaccion'] = cls._convertir_fecha_formato_db(datos['fecha_transaccion'])
            print(f"📅 Fecha convertida: {datos['fecha_transaccion']}")
        
        return datos
    
    @classmethod
    def _guardar_transaccion_encontrada(cls, id_carrito: int, datos_transaccion: dict, monto_total, codigo_proceso: str) -> bool:
        """
        Guarda la transacción encontrada en la base de datos
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                # Convertir monto_total a float si es Decimal
                if isinstance(monto_total, Decimal):
                    monto_total_float = float(monto_total)
                else:
                    monto_total_float = float(monto_total)
                
                # Calcular monto faltante
                monto_str = datos_transaccion.get('monto', '0')
                monto_match = re.search(r'(\d+\.?\d*)', monto_str)
                if monto_match:
                    monto_transaccion = float(monto_match.group(1))
                else:
                    monto_transaccion = 0
                    
                monto_faltante = max(0, monto_total_float - monto_transaccion)
                
                # Crear y guardar la transacción QR
                qr_transaction = cls(
                    nro_ach=datos_transaccion.get('nro_orden_ach', ''),
                    fecha_transaccion=datos_transaccion.get('fecha_transaccion'),  # ✅ Ya convertida
                    hora_transaccion=datos_transaccion.get('hora_transaccion'),
                    tipo_operacion=datos_transaccion.get('tipo_operacion'),
                    nro_cuenta_origen=datos_transaccion.get('nro_cuenta_origen'),
                    nombre_del_origen=datos_transaccion.get('nombre_del_origen'),
                    banco_origen=datos_transaccion.get('banco_origen'),
                    nro_cuenta_destino=datos_transaccion.get('nro_cuenta_destino'),
                    nombre_beneficiario=datos_transaccion.get('nombre_beneficiario'),
                    banco_destino=datos_transaccion.get('banco_destino'),
                    monto=monto_transaccion,
                    moneda=datos_transaccion.get('moneda'),
                    nro_orden_ach=datos_transaccion.get('nro_orden_ach'),
                    glosa=datos_transaccion.get('glosa'),
                    monto_faltante=monto_faltante,
                    id_carrito=id_carrito
                )
                
                if qr_transaction.guardar():
                    print(f"✅ Transacción QR guardada para carrito {id_carrito}")
                    
                    # Actualizar estado del carrito
                    query = "UPDATE carrito SET estado = 'pagado' WHERE id_carrito = %s"
                    cursor.execute(query, (id_carrito,))
                    
                    # Actualizar proceso de pago a COMPLETADO
                    proceso_actualizado = CodProcesoPago.actualizar_where(
                        {
                            'estado': 'C',  # Completado
                            'monto_pago_transaccion': monto_transaccion,
                            'monto_pagado': monto_transaccion,
                            'monto_faltante': monto_faltante,
                            'fecha_actualizacion': datetime.datetime.now(),
                            'mensaje': 'Pago encontrado y procesado exitosamente'
                        },
                        f"id_carrito = {id_carrito} AND codigo = '{codigo_proceso}'"
                    )
                    
                    conexion.commit()
                    print(f"✅ Carrito {id_carrito} actualizado a estado 'pagado'")
                    return True
                else:
                    print(f"❌ Error al guardar transacción QR para carrito {id_carrito}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error al guardar transacción encontrada: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            cls.liberar_conexion(conexion)
    
    @classmethod
    def _actualizar_estado_timeout(cls, id_carrito: int, codigo: str):
        """
        Actualiza el estado del proceso cuando se agota el tiempo
        """
        try:
            proceso_actualizado = CodProcesoPago.actualizar_where(
                {
                    'estado': 'T',  # Timeout
                    'fecha_actualizacion': datetime.datetime.now(),
                    'mensaje': 'Tiempo agotado - No se encontró pago'
                },
                f"id_carrito = {id_carrito} AND codigo = '{codigo}'"
            )
            print(f"⏰ Estado actualizado a TIMEOUT para carrito {id_carrito}")
        except Exception as e:
            print(f"❌ Error actualizando estado timeout: {e}")
    
    @classmethod
    def _actualizar_estado_error(cls, id_carrito: int, codigo: str, mensaje_error: str):
        """
        Actualiza el estado del proceso cuando hay error
        """
        try:
            proceso_actualizado = CodProcesoPago.actualizar_where(
                {
                    'estado': 'E',  # Error
                    'fecha_actualizacion': datetime.datetime.now(),
                    'mensaje': mensaje_error
                },
                f"id_carrito = {id_carrito} AND codigo = '{codigo}'"
            )
            print(f"❌ Estado actualizado a ERROR para carrito {id_carrito}")
        except Exception as e:
            print(f"❌ Error actualizando estado error: {e}")
    
    @classmethod
    def procesar_qr_transaction(cls, id_carrito: int, uid: str):
        """
        Procesa una transacción QR - versión principal
        """
        conexion = cls.obtener_conexion()
        try:
            with conexion.cursor(cursor_factory=DictCursor) as cursor:
                # Verificar que el carrito pertenezca al uid y esté en estado pendiente o procesopago
                query = """
                    SELECT c.id_carrito, u.id_cliente  
                    FROM carrito c
                    JOIN cliente u ON c.id_cliente = u.id_cliente
                    WHERE c.id_carrito = %s AND u.uid = %s AND (c.estado = 'pendiente' OR c.estado = 'procesopago')
                    LIMIT 1
                """
                cursor.execute(query, (id_carrito, uid))
                resultado = cursor.fetchone()
                if not resultado:
                    print(f"❌ No se encontró el carrito {id_carrito} para el UID {uid}")
                    return None
                
                # Verificar monto total a pagar 
                id_carrito = resultado['id_carrito']
                id_cliente = resultado['id_cliente']
                
                # CORREGIDO: Usar 'producto_carrito' (nombre correcto de la tabla)
                query = """
                    SELECT pc.id_carrito, u.fcm_token, SUM(pc.precio_total) AS MONTO_TOTAL
                    FROM producto_carrito pc
                    JOIN carrito c ON pc.id_carrito = c.id_carrito
                    JOIN cliente u ON c.id_cliente = u.id_cliente
                    WHERE pc.id_carrito = %s
                    GROUP BY pc.id_carrito, u.fcm_token
                """
                cursor.execute(query, (id_carrito,))
                resultado = cursor.fetchone()
                if not resultado:
                    print(f"❌ No se encontraron productos para el carrito {id_carrito}")
                    return None
                
                monto_total = resultado['monto_total']
                fcm_token = resultado['fcm_token']
                
                # Generar código de proceso pago
                codigo = f"PAY{id_carrito}{uuid.uuid4().hex[:8]}"
                
                # Guardar proceso de pago
                proceso_pago = CodProcesoPago()
                proceso_pago.codigo = codigo
                proceso_pago.monto_total = monto_total
                proceso_pago.id_carrito = id_carrito
                proceso_pago.estado = 'A'  # Activo (buscando)
                proceso_pago.mensaje = 'Proceso de pago iniciado - Buscando transacción'
                
                if not proceso_pago.guardar():
                    print(f"❌ Error al guardar proceso de pago para el carrito {id_carrito}")
                    return None
                
                print(f"✅ Proceso de pago guardado: {codigo}")
                
                # Iniciar búsqueda de QR transaction en hilo separado
                thread = threading.Thread(
                    target=cls._buscar_y_procesar_transaccion,
                    args=(codigo, id_carrito, fcm_token, monto_total),
                    daemon=True
                )
                thread.start()
                
                print(f"🎯 Búsqueda iniciada en hilo separado para carrito {id_carrito}")
                return codigo

        except Exception as e:
            print(f"❌ Error en procesar_qr_transaction: {e}")
            return None
        finally:
            cls.liberar_conexion(conexion)