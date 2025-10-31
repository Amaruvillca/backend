
from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path  
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

import shutil
import json
import os

from app.classes.ProductoCarrito import ProductoCarrito
from app.classes.Carrito import Carrito
from app.classes.Cliente import Cliente
from datetime import datetime

router = APIRouter()

@router.get('/')
def mostrarSucursales():
    productocarrirto = ProductoCarrito()
    resultado = productocarrirto.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }
    
@router.delete('/{id}')
def eliminarProductoCarrito(id: int):
    productoCarrito = ProductoCarrito()
    if productoCarrito.borrar(id):
        return {
            "message": "ProductoCarrito eliminado exitosamente"
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el producto")
    
@router.post('/{uid}')
async def crearProductoCarrito(uid: str, request: Request):
    data = await request.json()

    cliente = Cliente.find_by_uid(uid)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    id_cliente = cliente.id_cliente

    # Verificar si hay un carrito pendiente
    estado = Carrito.obtener_estado_por_cliente(id_cliente)

    if estado == "pendiente":
        id_carrito = Carrito.obtener_ultimo_id_carrito_por_cliente(id_cliente)
    else:
        # Crear un nuevo carrito si no hay uno pendiente
        nuevo_carrito = Carrito(
            fecha_creacion=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            estado="pendiente",
            id_cliente=id_cliente
        )
        if not nuevo_carrito.guardar():
            raise HTTPException(status_code=400, detail="Error al crear nuevo carrito")

        id_carrito = Carrito.obtener_ultimo_id_carrito_por_cliente(id_cliente)

    # Sincronizar producto
    productocarrito = ProductoCarrito()
    productocarrito.sincronizar(data)
    productocarrito.id_carrito = id_carrito

    # Extraer datos necesarios
    id_color_producto = productocarrito.id_color_producto
    cantidad = productocarrito.cantidad
    talla = productocarrito.talla

    # Si ya existe, sumar cantidad
    actualizado = ProductoCarrito.actualizar_o_sumar_cantidad(
        id_carrito=id_carrito,
        id_color_producto=id_color_producto,
        cantidad_a_sumar=cantidad,
        talla=talla
    )

    if actualizado:
        return JSONResponse(
            status_code=200,
            content={"message": "Cantidad actualizada exitosamente en el carrito"}
        )

    # Si no existía el producto en el carrito, lo guardamos como nuevo
    if not productocarrito.guardar():
        raise HTTPException(status_code=400, detail="Error al crear el producto en el carrito: " + str(productocarrito.atributos()))

    return JSONResponse(
        status_code=200,
        content={
            "message": "Producto en carrito creado exitosamente",
            "data": productocarrito.atributos()
        }
    )


@router.get('/{uid}/productoscarrito')
async def obtenerProductosCarrito(uid: str):
    cliente = Cliente.find_by_uid(uid)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    id_cliente = cliente.id_cliente

    productos = ProductoCarrito.obtener_productos_ultimo_carrito_pendiente(id_cliente)

    productos_dicts = [p.to_dict() for p in productos]

    return JSONResponse(
        status_code=200,
        content={
            "message": "Productos del carrito obtenidos exitosamente",
            "data": productos_dicts
        }
    )


