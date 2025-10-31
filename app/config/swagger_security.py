# app/dependencies/swagger_headers.py
from fastapi import Header, Depends
from typing import Optional

async def swagger_headers(
    x_api_name: Optional[str] = Header("Facelook", description="Nombre de la API"),
    x_api_version: Optional[str] = Header("1.0", description="Versión de la API"),
    x_developed_by: Optional[str] = Header("Kurve", description="Desarrollado por"),
    x_code: Optional[str] = Header(None, description="Código de operación")
):
    """
    Dependency para mostrar headers en Swagger UI
    """
    return {
        "X-API-Name": x_api_name,
        "X-API-Version": x_api_version,
        "X-Developed-By": x_developed_by,
        "X-Code": x_code
    }