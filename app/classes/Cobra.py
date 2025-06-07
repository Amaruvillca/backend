from app.classes import Activerecord


class Cobra(Activerecord):
    TABLA = 'cobra'
    CAMPOS = [
        'id_cobra',
        'monto_total',
        'monto_pagado',
        'cambio',
        'fecha_pago',
        'tipo_pago',
        'id_cliente',
        'nombreC',
        'ci',
        'id_personal',
        'id_venta'
    ]
    errores = []

    def __init__(
        self,
        id_cobra=None,
        monto_total=None,
        monto_pagado=None,
        cambio=None,
        fecha_pago=None,
        tipo_pago=None,
        id_cliente=None,
        nombreC=None,
        ci=None,
        id_personal=None,
        id_venta=None
    ):
        self.id_cobra = id_cobra
        self.monto_total = monto_total
        self.monto_pagado = monto_pagado
        self.cambio = cambio
        self.fecha_pago = fecha_pago
        self.tipo_pago = tipo_pago
        self.id_cliente = id_cliente
        self.nombreC = nombreC
        self.ci = ci
        self.id_personal = id_personal
        self.id_venta = id_venta
