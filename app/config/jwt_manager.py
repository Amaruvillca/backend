# app/auth/jwt_manager.py
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

class JWTManager:
    def __init__(self):
        # Configuración (en producción usa variables de entorno)
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-clave-super-secreta-aqui")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 43200
        
        # Contexto para hashing de passwords
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT con los datos proporcionados
        
        Args:
            data: Diccionario con los datos a incluir en el token
            expires_delta: Tiempo de expiración personalizado
            
        Returns:
            str: Token JWT codificado
        """
        # Crear una copia de los datos para no modificar el original
        to_encode = data.copy()
        
        # Calcular tiempo de expiración
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Agregar timestamp de expiración
        to_encode.update({"exp": expire})
        
        # Codificar el token JWT
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Dict con los datos del token si es válido, None si es inválido
        """
        try:
            # Decodificar el token
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            # Token inválido o expirado
            return None
    
    def hash_password(self, password: str) -> str:
        """
        Hashea una contraseña usando bcrypt
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Contraseña hasheada
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Contraseña hasheada
            
        Returns:
            bool: True si coinciden, False si no
        """
        return self.pwd_context.verify(plain_password, hashed_password)

# Instancia global para usar en toda la aplicación
jwt_manager = JWTManager()