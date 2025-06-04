from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path  
import os

from app.classes.Categorias import Categorias



router = APIRouter()

@router.get('/')
def hola():
    categoria = Categorias()
    resultado = categoria.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }