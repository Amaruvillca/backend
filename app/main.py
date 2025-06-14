from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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
from app.api import categorias, productos, sucursal, colorProducto, tallaProducto

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Include API routers
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(sucursal.router, prefix="/sucursales", tags=["sucursal"])
app.include_router(categorias.router, prefix="/categorias", tags=["categorias"])
app.include_router(colorProducto.router, prefix="/colorProducto", tags=["colorProducto"])
app.include_router(tallaProducto.router, prefix="/tallaProducto", tags=["tallaProducto"])

# Root endpoint
@app.get("/")
def read_root():
    return "Welcome to LookMarket"

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
    threshold: float = Form(0.5)
):
    """Endpoint for image comparison"""
    try:
        image = Image.open(file.file).convert("RGB")
        uploaded_features = extract_features(image)
        similar_images = compare_images(uploaded_features, threshold)

        return JSONResponse(content={
            "resultados": [
                {"imagen": name, "similitud": round(score, 4)}
                for name, score in similar_images
            ],
            "total_resultados": len(similar_images)
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")