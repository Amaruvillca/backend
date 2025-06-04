from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path  
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.classes.Sucursal import Sucursal
import shutil
import json
import os

from app.classes.Sucursal import Sucursal

router = APIRouter()

@router.get('/')
def mostrarSucursales():
    sucursal = Sucursal()
    resultado = sucursal.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }


@router.post("/")
async def crear_sucursal(
    datos: str = Form(...),  
    imagen1: UploadFile = File(None),
    imagen2: UploadFile = File(None),
    imagen3: UploadFile = File(None)
):
    try:
        datos_dict = json.loads(datos) 
    except Exception as e:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Guardar imágenes
    def guardar(imagen):
        if imagen:
            path = f"img/sucursales/{imagen.filename}"
            os.makedirs("img/sucursales", exist_ok=True)
            with open(path, "wb") as f:
                shutil.copyfileobj(imagen.file, f)
            return imagen.filename
        return None

    datos_dict["imagen1"] = guardar(imagen1)
    datos_dict["imagen2"] = guardar(imagen2)
    datos_dict["imagen3"] = guardar(imagen3)

    # Crear la sucursal
    sucursal = Sucursal()
    sucursal.sincronizar(datos_dict)

    if sucursal.guardar():
        return {
            "mensaje": "Sucursal creada exitosamente",
            "id_sucursal": sucursal.id_sucursal
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo guardar la sucursal")