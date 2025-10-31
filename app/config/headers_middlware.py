from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

class HeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        
        # Valores válidos esperados para cada header
        self.valid_headers = {
            "X-API-Name": ["Facelook"],
            "X-API-Version": ["1.0"],
            "X-Developed-By": ["Kurve"],
            "X-Code": ["17145", "16956", "17061", "17411", "17158","17324"]
        }

        # Rutas exentas del control
        self.excluded_paths = [
            "/docs", "/redoc", "/openapi.json",
            "/img/", "/static/"
        ]

    def is_excluded_path(self, path: str) -> bool:
        """Verifica si la ruta debe quedar excluida del control de headers."""
        return any(path.startswith(prefix) for prefix in self.excluded_paths)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Excluir documentación e imágenes
        if self.is_excluded_path(path):
            return await call_next(request)

        headers = request.headers

        # Verificar existencia y validez de cada header
        for header_name, valid_values in self.valid_headers.items():
            if header_name not in headers:
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"Falta el header requerido: {header_name}"}
                )

            header_value = headers.get(header_name)
            if header_value not in valid_values:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": (
                            f"Valor inválido para '{header_name}'. "
                            f"Error al autenticar."
                        )
                    }
                )

        # Si pasa todas las validaciones → continuar
        response = await call_next(request)

        # Añadir los headers validados a la respuesta (opcional)
        for header_name, valid_values in self.valid_headers.items():
            response.headers[header_name] = headers.get(header_name)

        return response
