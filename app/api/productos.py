import json
import shutil
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path  
import os
import os
import shutil
import uuid

from app.classes.Productos import Producto
BASE_DIR = Path(__file__).resolve().parent.parent

# Ruta a la carpeta de imágenes
RUTA_BANNER = BASE_DIR / "img" / "baner_producto"
RUTA_PRODUCTO = BASE_DIR / "img" / "productos"
RUTA_PRODUCTO_V = BASE_DIR / "img" / "producto_v"
CACHE_FILE = BASE_DIR / "image_features_cache.pkl"

router = APIRouter()


@router.get('/')
async def mostrarProductos():
    producto = Producto()
    resultado = producto.all()
    return  {
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
    banner: UploadFile = File(None),
):
    try:
        datos_dict = json.loads(datos) 
    except Exception as e:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Guardar imágenes
    
    def guardar(imagen):
        if imagen:
            ext = os.path.splitext(imagen.filename)[1]  # Extrae extensión
            nombre_unico = f"{uuid.uuid4().hex}{ext}"  # Genera nombre único con la misma extensión
            path = os.path.join(RUTA_PRODUCTO, nombre_unico)
            os.makedirs(RUTA_PRODUCTO, exist_ok=True)
            with open(path, "wb") as f:
                shutil.copyfileobj(imagen.file, f)
            return nombre_unico
        return None

    def guardarB(imagen):
        if imagen:
            ext = os.path.splitext(imagen.filename)[1]
            nombre_unico = f"{uuid.uuid4().hex}{ext}"
            path = os.path.join(RUTA_BANNER, nombre_unico)
            os.makedirs(RUTA_BANNER, exist_ok=True)
            with open(path, "wb") as f:
                shutil.copyfileobj(imagen.file, f)
            return nombre_unico
        return None

    datos_dict["imagen"] = guardar(imagen)
    datos_dict["banner_producto"] = guardarB(banner)
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

@router.get("/recientes")
def obtener_productos_recientes():
    productos = Producto.productos_recientes()

    return {
        "message": "Datos recuperados exitosamente",
        "data": [producto.__dict__ for producto in productos]
    }
    
@router.get("/buscar")
def buscar_productos(busqueda: str):
    productos = Producto.buscar_productos(busqueda)
    return {
        "message": "Datos recuperados exitosamente",
        "data": [producto.__dict__ for producto in productos],
        "total": len(productos) 
    }

@router.get("/banner")
def obtener_banners(cantidad: int = 3):
    banners = Producto.obtener_banners_aleatorios(cantidad)
    
    # Formatear respuesta
    data = [{
        "id": b[0],
        "nombre": b[1],
        "precio": float(b[2]),
        "banner_url": b[3]  # Este es el campo importante
    } for b in banners]
    
    return {
        "message": "Banners recuperados exitosamente",
        "data": data
    }


@router.get("/recientes")
def obtener_productos_recientes():
    productos = Producto.productos_recientes()

    return {
        "message": "Datos recuperados exitosamente",
        "data": [producto.__dict__ for producto in productos]
    }

@router.get("/mejorescalificados")
def obtener_productos_mejor_calificados():
    productos = Producto.mejores_calificados()
    
    return {
        "message": "Datos recuperados exitosamente",
        "data": [producto.__dict__ for producto in productos]
    }
@router.get("/mejorescalificados/{pagina}")
def obtener_productos_mejor_calificados(pagina: int):
    productos = Producto.mejores_calificados_paginados(pagina)
    
    return {
        "message": "Datos recuperados exitosamente",
        "data": [producto.__dict__ for producto in productos]
    }

    
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
@router.get("/{id_producto}/similares")
def obtener_similares(id_producto: int):
    productos = Producto.obtener_similares(id_producto=id_producto)

    return {
        "message": "Productos similares encontrados",
        "data": [p.__dict__ for p in productos]
    }

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

@router.post('/guardar_imagen_producto/')
async def guardar_imagen_producto(imagen: UploadFile = File(...)):
    """Guarda una imagen en la carpeta de productos y la añade al caché de características"""
    try:
        # Verificar que la carpeta exista
        os.makedirs(RUTA_PRODUCTO, exist_ok=True)
        
        # ✅ MANTENER EL NOMBRE ORIGINAL del archivo
        nombre_archivo = imagen.filename
        ruta_imagen = RUTA_PRODUCTO / nombre_archivo
        
        # Guardar la imagen
        with open(ruta_imagen, "wb") as f:
            contenido = await imagen.read()
            f.write(contenido)
        
        print(f"✅ Imagen guardada en: {ruta_imagen}")
        
        # ✅ ACTUALIZAR EL CACHÉ usando la función de main.py
        import sys
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from main import add_image_to_cache
        
        # Añadir imagen a la caché de características
        cache_exitosa = add_image_to_cache(str(ruta_imagen), nombre_archivo)
        
        return {
            "message": "Imagen guardada exitosamente",
            "filename": nombre_archivo,  # ✅ Nombre original
            "path": str(ruta_imagen),
            "cache_updated": cache_exitosa
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")
    
@router.post('/guardar_imagen_producto_variante/')
async def guardar_imagen_producto_variante(imagen: UploadFile = File(...)):
    """Guarda una imagen en la carpeta de productos y la añade al caché de características"""
    try:
        # Verificar que la carpeta exista
        os.makedirs(RUTA_PRODUCTO, exist_ok=True)
        
        # ✅ MANTENER EL NOMBRE ORIGINAL del archivo
        nombre_archivo = imagen.filename
        ruta_imagen = RUTA_PRODUCTO_V / nombre_archivo
        
        # Guardar la imagen
        with open(ruta_imagen, "wb") as f:
            contenido = await imagen.read()
            f.write(contenido)
        
        print(f"✅ Imagen guardada en: {ruta_imagen}")
        
        
        
        return {
            "message": "Imagen guardada exitosamente",
            "filename": nombre_archivo,  # ✅ Nombre original
            "path": str(ruta_imagen),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")