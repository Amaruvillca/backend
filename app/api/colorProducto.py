from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path  
import os

from app.classes.ColorProducto import ColorProducto



router = APIRouter()

@router.get('/')
def hola():
    color_producto = ColorProducto()
    resultado = color_producto.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }