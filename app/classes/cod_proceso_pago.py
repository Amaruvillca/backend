from app.classes.Activerecord import Activerecord
class CodProcesoPago(Activerecord):   
    TABLA = 'cod_proceso_pago'
    nombre_id = 'id_cod_proceso_pago'
    columnas_db = [
        'id_cod_proceso_pago', 'codigo', 'monto_total','monto_pago_transaccion','monto_faltante',
        'monto_extra','monto_pagado','mensaje','logs', 'fecha_creacion', 'fecha_actualizacion',
        'estado', 'id_carrito'
            ]
    errores = []
    def __init__(self,id_cod_proceso_pago=None, codigo=None, monto_total=None, monto_pago_transaccion=None, monto_faltante=None,
                 monto_extra=None, monto_pagado=None, mensaje=None, logs=None, fecha_creacion=None, fecha_actualizacion=None,
                 estado=None, id_carrito=None):
        self.id_cod_proceso_pago = id_cod_proceso_pago
        self.codigo = codigo
        self.monto_total = monto_total
        self.monto_pago_transaccion = monto_pago_transaccion
        self.monto_faltante = monto_faltante
        self.monto_extra = monto_extra
        self.monto_pagado = monto_pagado
        self.mensaje = mensaje
        self.logs = logs
        self.fecha_creacion = fecha_creacion
        self.fecha_actualizacion = fecha_actualizacion
        self.estado = estado
        self.id_carrito = id_carrito

