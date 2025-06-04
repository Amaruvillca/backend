from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import categorias, productos, sucursal, colorProducto, tallaProducto


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(productos.router, prefix="/productos", tags=["productos"])
app.include_router(sucursal.router, prefix="/sucursales", tags=["sucursal"])
app.include_router(categorias.router, prefix="/categorias", tags=["categorias"])
app.include_router(colorProducto.router, prefix="/colorProducto", tags=["colorProducto"])
app.include_router(tallaProducto.router, prefix="/tallaProducto", tags=["tallaProducto"])



@app.get("/")
def read_root():
    return "bien venido"