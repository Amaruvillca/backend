
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