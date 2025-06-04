from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path  
import os

from app.classes.TallaProducto import TallaProducto



router = APIRouter()

@router.get('/')
def hola():
    talla_producto = TallaProducto()
    resultado = talla_producto.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }