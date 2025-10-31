
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

from app.classes.Carrito import Carrito

router = APIRouter()

@router.get('/')
def mostrarSucursales():
    carrito = Carrito()
    resultado = carrito.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }
    
@router.post('/')
async def crearCarrito(request: Request):
    
    data = await request.json()
    carrito=Carrito()
    carrito.sincronizar(data)
    
    if not carrito.guardar():
        raise HTTPException(status_code=400, detail="Error al crear el carrito"+carrito.atributos())
    
    return JSONResponse(status_code=200, content={"message": "Carrito creado exitosamente", "data": carrito.atributos()})