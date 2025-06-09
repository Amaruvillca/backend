from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path  
import os

from app.classes.Productos import Producto
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
@router.get('/productos/{id_categoria}/{pagina}')
def obtener_productos_por_categoria(id_categoria: int, pagina: int):
    productos = Producto.mostrar_productos_categoria(id_categoria, pagina)
    return {
        "message": "Datos recuperados exitosamente",
        "data": [p.__dict__ for p in productos]
    }

