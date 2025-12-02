import logging
import PIL
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from torchvision import models, transforms
from torch.nn.functional import cosine_similarity
from PIL import Image
import pickle
from typing import Dict
import torch
import os
from pathlib import Path

# Import API routers
from app.api import categorias, productos, sucursal, colorProducto, tallaProducto, clientes, paga, carrito, productocarrito, qr_transacion
from app.classes.Productos import Producto

from app.config.gmail_client import GmailClient
from app.config.headers_middlware import HeadersMiddleware
from app.config.swagger_security import swagger_headers


# Initialize FastAPI app

from fastapi import FastAPI, Header, HTTPException

origins = [
    "http://localhost:3000",  # tu frontend
]



app = FastAPI(
    title="Facelook API",
    version="1.0",
    description="API con headers personalizados en Swagger UI",
    dependencies=[Depends(swagger_headers)],
    
)

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Name", "X-API-Version", "X-Developed-By", "X-Code"],
)

app.add_middleware(HeadersMiddleware)

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent

# Mount static directories function
def mount_directory(relative_path: str, url_mount: str, name: str):
    path = BASE_DIR / relative_path
    if path.exists():
        app.mount(url_mount, StaticFiles(directory=path), name=name)
    else:
        print(f"[WARNING] Directory {path} not found, '{url_mount}' won't be mounted.")

# Mount static directories
mount_directory("img/productos", "/img/productos", "img_productos")
mount_directory("img/producto_v", "/img/producto_v", "img_producto_variantes")
mount_directory("img/sucursales", "/img/sucursales", "img_sucursales")
mount_directory("img/clientes", "/img/clientes", "img_clientes")
mount_directory("img/personal", "/img/personal", "img_personal")
mount_directory("img/categorias", "/img/categorias", "img_categorias")
mount_directory("img/baner_producto", "/img/baner_producto", "img_baner_producto")
mount_directory("img/qr", "/img/qr", "qr")

# Include API routers
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(sucursal.router, prefix="/sucursales", tags=["sucursal"])
app.include_router(categorias.router, prefix="/categorias", tags=["categorias"])
app.include_router(colorProducto.router, prefix="/colorProducto", tags=["colorProducto"])
app.include_router(tallaProducto.router, prefix="/tallaProducto", tags=["tallaProducto"])
app.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
app.include_router(paga.router, prefix="/pagar", tags=["pagar"])
app.include_router(carrito.router, prefix="/carrito", tags=["carrito"])
app.include_router(productocarrito.router, prefix="/productocarrito", tags=["productoscarrito"])
app.include_router(qr_transacion.router, prefix="/qr_transactions", tags=["qr_transactions"])


# Root endpoint
@app.get("/")
def read_root():
    

# Crear cliente Gmail
    gmail = GmailClient()

# Probar conexión
    gmail.test_connection()

# Obtener los 5 correos más recientes
    emails = gmail.list_emails(max_results=5)
    for e in emails:
        print(f"📬 {e['from']} - {e['subject']} ({e['date']})")

    
    return {"message": "Welcome to FaceLoock API!"}

# -----------------------------------------------
# IMAGE COMPARISON FUNCTIONALITY
# -----------------------------------------------

# Configuration
IMAGE_DIR = BASE_DIR / "img/productos"
CACHE_FILE = BASE_DIR / "image_features_cache.pkl"
FEATURES_CACHE: Dict[str, torch.Tensor] = {}

# Image transformation pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

# Initialize model
device = torch.device("cpu")
resnet = models.resnet50(pretrained=True)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])
resnet.eval()
resnet.to(device)

def extract_features(image: Image.Image) -> torch.Tensor:
    """Extract features from an image using ResNet50"""
    tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = resnet(tensor)
    return features.view(-1)

def load_or_build_features_cache():
    """Load or build the features cache"""
    global FEATURES_CACHE
    
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "rb") as f:
            FEATURES_CACHE = pickle.load(f)
    else:
        FEATURES_CACHE = {}
        for filename in os.listdir(IMAGE_DIR):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                path = os.path.join(IMAGE_DIR, filename)
                try:
                    image = Image.open(path).convert("RGB")
                    features = extract_features(image)
                    FEATURES_CACHE[filename] = features.cpu().numpy()
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(FEATURES_CACHE, f)

# Initialize cache on startup
load_or_build_features_cache()
def add_image_to_cache(image_path: str, filename: str):
    """Add a new image to the features cache"""
    # global FEATURES_CACHE

    try:
        image = Image.open(image_path).convert("RGB")
        features = extract_features(image)
        FEATURES_CACHE[filename] = features.cpu().numpy()
        
        # Save updated cache
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(FEATURES_CACHE, f)
        
        print(f"✅ Imagen {filename} añadida a la caché de características")
        return True
    except Exception as e:
        print(f"❌ Error añadiendo imagen {filename} a la caché: {e}")
        return False

def get_features_cache():
    """Get the current features cache"""
    return FEATURES_CACHE

def update_features_cache():
    """Force cache update"""
    load_or_build_features_cache()

def compare_images(uploaded_features: torch.Tensor, threshold: float = 0.8) -> list:
    """Compare uploaded image features with cached features"""
    results = []
    
    for filename, features_np in FEATURES_CACHE.items():
        features = torch.from_numpy(features_np).to(device)
        similarity = cosine_similarity(uploaded_features.unsqueeze(0), features.unsqueeze(0))
        sim_score = similarity.item()
        
        if sim_score >= threshold:
            results.append((filename, sim_score))
    
    return sorted(results, key=lambda x: x[1], reverse=True)

@app.post("/comparar-imagenes")
async def compare_image(
    file: UploadFile = File(...),
    threshold: float = Form(0.7)
):
    """Endpoint que devuelve productos con imágenes similares ordenados por similitud"""
    try:
        # 1. Procesar imagen y obtener imágenes similares con sus scores
        image = Image.open(file.file).convert("RGB")
        similar_images = compare_images(extract_features(image), threshold)  # [(nombre_imagen, score), ...]
        
        if not similar_images:
            return {
                "message": "No se encontraron imágenes similares",
                "data": [],
                # "total_similares": 0
            }

        # 2. Ordenar por score de similitud (mayor primero)
        similar_images.sort(key=lambda x: x[1], reverse=True)
        
        # 3. Obtener nombres de imágenes ordenadas
        similar_image_names = [img[0] for img in similar_images]
        
        # 4. Obtener productos manteniendo el orden de similitud
        productos_similares = Producto.obtener_por_imagenes(similar_image_names)
        
        # 5. Crear mapeo de imagen a producto para preservar el orden
        producto_por_imagen = {p.imagen: p for p in productos_similares}
        
        # 6. Construir respuesta ordenada con scores
        respuesta_ordenada = []
        for img_name, score in similar_images:
            if img_name in producto_por_imagen:
                p = producto_por_imagen[img_name]
                respuesta_ordenada.append({
                    "id_producto": p.id_producto,
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "imagen": p.imagen,
                    "fecha": p.fecha_creacion,
                    "genero": p.genero,
                    "precio": float(p.precio),
                    "para": p.para,
                    "id_sucursal": p.id_sucursal,
                    "id_categoria": p.id_categoria,
                    "promedio_calificacion": float(getattr(p, 'promedio_calificacion', 0.0)),
                   # "similitud": float(score)  # Incluimos el score de similitud
                })

        return {
            "message": "Datos recuperados exitosamente",
            "data": respuesta_ordenada,
            # "total_similares": len(respuesta_ordenada)
        }

    except PIL.UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Archivo no es una imagen válida")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))