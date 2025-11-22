
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

from app.classes.Paga import Paga

router = APIRouter()

@router.get('/')
def mostrarSucursales():
    paga = Paga()
    resultado = paga.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }
@router.get('/History/{uid}')
def mostrarHistorialPagos(uid: str):
    paga = Paga()
    resultado = paga.obtener_pagos_por_uid(uid)
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }

@router.post('/{id_carrito}')
async def crearPaga(id_carrito: int, request: Request):
    data = await request.json()
    paga = Paga()
    nuevo_pago = paga.crear(data)
    if nuevo_pago:
        return {
            "message": "Pago creado exitosamente",
            "data": nuevo_pago
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo crear el pago")
