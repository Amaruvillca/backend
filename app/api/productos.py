import json
import shutil
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path  
import os

from app.classes.Productos import Producto

router = APIRouter()

@router.get('/')
def mostrarProductos():
    producto = Producto()
    resultado = producto.all()
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }


@router.post("/")
async def crear_producto(
    datos: str = Form(...),  
    imagen: UploadFile = File(None),
    
):
    try:
        datos_dict = json.loads(datos) 
    except Exception as e:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Guardar imágenes
    def guardar(imagen):
        if imagen:
            path = f"img/productos/{imagen.filename}"
            os.makedirs("img/productos", exist_ok=True)
            with open(path, "wb") as f:
                shutil.copyfileobj(imagen.file, f)
            return imagen.filename
        return None

    datos_dict["imagen"] = guardar(imagen)
    # Crear el producto
    producto = Producto()
    producto.sincronizar(datos_dict)
    if(producto.validar() == False):
        raise HTTPException(status_code=400, detail=producto.errores)


    if producto.guardar():
        return {
            "mensaje": "Producto creado exitosamente",
            "id_producto": producto.id_producto
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo guardar el producto")
@router.put("/")
async def actualizar_producto(
    
    datos: str = Form(...),
    imagen: UploadFile = File(None),
):
    try:
        datos_dict = json.loads(datos) 
    except Exception as e:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Guardar imágenes
    def guardar(imagen):
        if imagen:
            path = f"img/productos/{imagen.filename}"
            os.makedirs("img/productos", exist_ok=True)
            with open(path, "wb") as f:
                shutil.copyfileobj(imagen.file, f)
            return imagen.filename
        return None

    datos_dict["imagen"] = guardar(imagen)
    # Crear el producto
    producto = Producto()
    producto.sincronizar(datos_dict)
    if(producto.validar() == False):
        raise HTTPException(status_code=400, detail=producto.errores)


    if producto.guardar():
        return {
            "mensaje": "Producto actualizado exitosamente",
            "id_producto": producto.id_producto
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo guardar el producto")



@router.get('/{id}')
def mostrarProducto(id: int):
    producto = Producto()
    resultado = producto.find(id)
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }    
@router.delete('/{id}')
def eliminarProducto(id: int):
    producto = Producto()
    if producto.borrar(id):
        return {
            "message": "Producto eliminado exitosamente"
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el producto")

IMAGENES_DIR = "./img/productos/"

@router.get("/imagenes/{nombre_imagen}")
async def servir_imagen(nombre_imagen: str):
   
    os.makedirs(IMAGENES_DIR, exist_ok=True)
    
    ruta_imagen = Path(IMAGENES_DIR) / nombre_imagen
    
    if not ruta_imagen.is_file():
        return {"error": "Imagen no encontrada"}, 404
    
    return FileResponse(ruta_imagen)