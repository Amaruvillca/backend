from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from torchvision import models, transforms
from torch.nn.functional import cosine_similarity
from PIL import Image
import torch
import os
from pathlib import Path

from app.api import categorias, productos, sucursal, colorProducto, tallaProducto


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

def montar_directorio(ruta_relativa: str, url_mount: str, nombre: str):
    path = BASE_DIR / ruta_relativa
    if path.exists():
        app.mount(url_mount, StaticFiles(directory=path), name=nombre)
    else:
        print(f"[AVISO] No se encontró la carpeta {path}, no se montará '{url_mount}'.")

# Montar imágenes
montar_directorio("img/productos", "/img/productos", "img_productos")
montar_directorio("img/producto_v", "/img/producto_v", "img_producto_variantes")
montar_directorio("img/sucursales", "/img/sucursales", "img_sucursales")
montar_directorio("img/clientes", "/img/clientes", "img_clientes")
montar_directorio("img/personal", "/img/personal", "img_personal")
montar_directorio("img/categorias", "/img/categorias", "img_categorias")

# Rutas de API
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(sucursal.router, prefix="/sucursales", tags=["sucursal"])
app.include_router(categorias.router, prefix="/categorias", tags=["categorias"])
app.include_router(colorProducto.router, prefix="/colorProducto", tags=["colorProducto"])
app.include_router(tallaProducto.router, prefix="/tallaProducto", tags=["tallaProducto"])

@app.get("/")
def read_root():
    return "Bienvenido a LookMarket"

# -----------------------------------------------
# FUNCIONALIDAD DE COMPARACIÓN DE IMÁGENES CON IA
# -----------------------------------------------

# Carpeta con imágenes base
IMAGE_DIR = BASE_DIR / "img/productos"

# Transforms para ResNet50
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Modelo ResNet50 sin la última capa (solo extracción de features)
resnet = models.resnet50(pretrained=True)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])
resnet.eval()
device = torch.device("cpu")
resnet.to(device)

# Función para extraer características de imagen
def extract_features(image: Image.Image):
    tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = resnet(tensor)
    return features.view(-1)

# Comparar imagen con las de la carpeta
def compare_with_folder(uploaded_image: Image.Image, threshold: float = 0.8):
    uploaded_features = extract_features(uploaded_image)
    results = []

    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(IMAGE_DIR, filename)
            try:
                image = Image.open(path).convert("RGB")
                features = extract_features(image)
                similarity = cosine_similarity(uploaded_features.unsqueeze(0), features.unsqueeze(0))
                sim_score = similarity.item()
                if sim_score >= threshold:
                    results.append((filename, sim_score))
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

    results.sort(key=lambda x: x[1], reverse=True)
    return results

# Ruta de comparación
@app.post("/comparar-imagenes")
async def comparar_imagen(
    file: UploadFile = File(...),
    threshold: float = Form(0.8)
):
    try:
        image = Image.open(file.file).convert("RGB")
        similares = compare_with_folder(image, threshold)

        return JSONResponse(content={
            "resultados": [
                {"imagen": nombre, "similitud": round(score, 4)}
                for nombre, score in similares
            ],
            "total_resultados": len(similares)
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar la imagen: {str(e)}")



