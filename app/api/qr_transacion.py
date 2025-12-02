from fastapi import APIRouter, HTTPException
from app.classes.qr_transactions import QrTransactions
from app.classes.cod_proceso_pago import CodProcesoPago
import datetime

router = APIRouter()

@router.get('/')
def mostrarSucursales():
    return {
        "message": "Endpoint de QR Transactions activo"
    }

@router.post('/iniciar_busqueda')
async def iniciar_busqueda(id_carrito: int, uid: str):
    """
    Inicia la búsqueda de transacciones QR para un carrito
    """
    try:
        print(f"🚀 Iniciando búsqueda para carrito {id_carrito}, UID: {uid}")
        
        # Llamar al método que procesa la transacción QR
        codigo_proceso = QrTransactions.procesar_qr_transaction(id_carrito, uid)
        
        if not codigo_proceso:
            raise HTTPException(
                status_code=400, 
                detail="No se pudo iniciar la búsqueda. Verifique que el carrito exista y esté en estado pendiente."
            )
        
        return {
            "success": True,
            "message": "Búsqueda de pago iniciada",
            "codigo_proceso": codigo_proceso,
            "id_carrito": id_carrito,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en iniciar_busqueda: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"No se pudo iniciar la búsqueda: {str(e)}"
        )

@router.get('/verificar_transaccion')
async def verificar_transaccion(id_carrito: int, codigo: str):
    """
    Verifica el estado del proceso de pago consultando cod_proceso_pago
    """
    try:
        print(f"🔍 Verificando transacción - Carrito: {id_carrito}, Código: {codigo}")
        
        # Buscar el proceso de pago específico
        proceso = CodProcesoPago.buscar_uno(
            f"id_carrito = {id_carrito} AND codigo = '{codigo}'"
        )
        
        if not proceso:
            raise HTTPException(
                status_code=404, 
                detail="No se encontró el proceso de pago especificado"
            )
        
        # Preparar respuesta según el estado
        respuesta = {
            "id_carrito": id_carrito,
            "codigo_proceso": codigo,
            "estado": proceso.estado,
            "mensaje": proceso.mensaje,
            "monto_total": float(proceso.monto_total) if proceso.monto_total else 0,
            "monto_pagado": float(proceso.monto_pagado) if proceso.monto_pagado else 0,
            "monto_faltante": float(proceso.monto_faltante) if proceso.monto_faltante else 0,
            "fecha_actualizacion": proceso.fecha_actualizacion.isoformat() if proceso.fecha_actualizacion else None,
            "existe_transaccion": False
        }
        
        # Interpretar los estados
        if proceso.estado == 'C':  # Completado
            respuesta["success"] = True
            respuesta["pago_completado"] = True
            respuesta["existe_transaccion"] = True
            respuesta["detalle"] = "Pago encontrado y procesado exitosamente"
            
        elif proceso.estado == 'A':  # Activo (buscando)
            respuesta["success"] = True
            respuesta["pago_completado"] = False
            respuesta["detalle"] = "Búsqueda de pago en progreso"
            
        elif proceso.estado == 'T':  # Timeout
            respuesta["success"] = False
            respuesta["pago_completado"] = False
            respuesta["detalle"] = "Tiempo agotado - No se encontró pago"
            
        elif proceso.estado == 'E':  # Error
            respuesta["success"] = False
            respuesta["pago_completado"] = False
            respuesta["detalle"] = f"Error en el proceso: {proceso.mensaje}"
            
        else:  # Otros estados
            respuesta["success"] = True
            respuesta["pago_completado"] = False
            respuesta["detalle"] = f"Estado del pago: {proceso.estado}"
        
        return respuesta
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en verificar_transaccion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get('/debug_gmail')
async def debug_gmail():
    """
    Endpoint para debug de Gmail - ver todos los correos recientes
    """
    try:
        from app.config.gmail_client import GmailClient
        gmail = GmailClient()
        
        # Buscar TODOS los correos recientes
        all_emails = gmail.search_emails(query='', max_results=10)
        
        emails_info = []
        for i, email in enumerate(all_emails):
            email_data = {
                'numero': i + 1,
                'id': email.get('id', ''),
                'snippet': email.get('snippet', '')[:200],
                'tiene_body': 'body' in email and bool(email.get('body')),
            }
            emails_info.append(email_data)
        
        return {
            "success": True,
            "total_emails": len(all_emails),
            "emails": emails_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get('/test_busquedas')
async def test_busquedas():
    """
    Probar diferentes queries de búsqueda
    """
    try:
        from app.config.gmail_client import GmailClient
        gmail = GmailClient()
        
        queries = [
            'from:ACH7@bancounion.com.bo',
            'from:@bancounion.com.bo', 
            'bancounion',
            'ACH',
            'transferencia',
            'pago',
            ''  # Todos los correos
        ]
        
        resultados = {}
        
        for query in queries:
            emails = gmail.search_emails(query=query, max_results=5)
            resultados[query] = {
                'count': len(emails),
                'emails': [{'snippet': e.get('snippet', '')[:100]} for e in emails[:2]]
            }
        
        return {
            "success": True,
            "resultados": resultados
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }