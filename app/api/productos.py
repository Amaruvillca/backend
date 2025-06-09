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

@router.get('/{id}/colores')
def mostrarColoresProducto(id: int):
    producto = Producto()
    resultado = producto.colores(id)
    return {
        "message": "Colores del producto recuperados exitosamente",
        "data": resultado
    }

@router.get('/{id}/colores/{id_color_producto}/tallas')
def mostrarTallasProducto(id: int,id_color_producto: int):
    producto = Producto()
    resultado = producto.tallas(id_color_producto)
    
    return {
        "message": "Tallas del producto recuperadas exitosamente",
        "data": resultado
    }
    
@router.get('/todo/{id}')
def mostrarProducto(id: int):
    producto = Producto()
    resultado = producto.productos_colores_y_tallas(id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    } 
    
@router.get("/{pagina}/paginacion")
def obtener_productos_paginados(pagina: int):
    productos = Producto.productos_paginados(pagina)
    
    return {
        "message": "Datos recuperados exitosamente",
        "data": [producto.__dict__ for producto in productos]
    }
