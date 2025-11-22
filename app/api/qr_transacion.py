
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

from app.classes.qr_transactions import QrTransactions


router = APIRouter()

@router.get('/')
def mostrarSucursales():
    return{
        "message": "Endpoint de QR Transactions activo"
    }

@router.post('/')
async def procesar_qr_transaction(id_carrito: int, uid: str,glosa: str):
    pass