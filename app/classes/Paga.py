from app.classes import Activerecord


class Paga(Activerecord):
    TABLA = 'paga'
    CAMPOS = [
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
