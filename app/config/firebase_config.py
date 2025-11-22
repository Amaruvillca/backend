import firebase_admin
from firebase_admin import credentials, messaging
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FirebaseConfig:
    _initialized = False
    _app = None
    
    @classmethod
    def initialize_firebase(cls):
        """Inicializar Firebase Admin SDK"""
        if cls._initialized:
            logger.debug("Firebase ya está inicializado")
            return True
            
        try:
            cred = cls._get_credentials()
            
            if cred is None:
                logger.error("No se pudieron cargar las credenciales de Firebase")
                return False
            
            # Inicializar solo si no está inicializado
            if not firebase_admin._apps:
                cls._app = firebase_admin.initialize_app(cred)
                cls._initialized = True
                logger.info("✅ Firebase Admin SDK inicializado correctamente")
                return True
            else:
                logger.info("Firebase ya estaba inicializado")
                cls._initialized = True
                return True
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error decodificando JSON de Firebase: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase: {e}")
            return False
    
    @classmethod
    def _get_credentials(cls):
        """Obtener credenciales desde diferentes fuentes"""
        # Opción 1: Desde variable de entorno (recomendado para producción)
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        if service_account_json:
            try:
                cred_dict = json.loads(service_account_json)
                logger.info("Firebase configurado desde variable de entorno")
                return credentials.Certificate(cred_dict)
            except json.JSONDecodeError as e:
                logger.error(f"Error en JSON de variable de entorno: {e}")
                return None
        
        # Opción 2: Desde archivo JSON
        possible_paths = [
            "service-account-key.json",
            "firebase-service-account.json",
            Path(__file__).parent / "service-account-key.json",
            Path(__file__).parent / "firebase-service-account.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Firebase configurado desde archivo: {path}")
                return credentials.Certificate(str(path))
        
        logger.error("No se encontró configuración de Firebase en ninguna ubicación")
        return None
    
    @classmethod
    def is_initialized(cls):
        """Verificar si Firebase está inicializado"""
        return cls._initialized and len(firebase_admin._apps) > 0
    
    @classmethod
    def get_messaging(cls):
        """Obtener instancia de messaging verificando inicialización"""
        if not cls.is_initialized():
            success = cls.initialize_firebase()
            if not success:
                raise RuntimeError("Firebase no pudo inicializarse. Verifique las credenciales.")
        
        return messaging
    
    @classmethod
    def get_app(cls):
        """Obtener la instancia de la app de Firebase"""
        if cls.is_initialized():
            return cls._app or firebase_admin.get_app()
        return None
    
    @classmethod
    def cleanup(cls):
        """Limpiar la inicialización de Firebase"""
        if cls._initialized and firebase_admin._apps:
            try:
                firebase_admin.delete_app(cls._app)
                logger.info("Firebase app eliminada correctamente")
            except Exception as e:
                logger.error(f"Error eliminando Firebase app: {e}")
            finally:
                cls._initialized = False
                cls._app = None