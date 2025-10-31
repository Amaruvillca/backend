import logging
import shutil
import uuid
import cv2
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path  
import os
from fastapi import HTTPException
import pickle

import face_recognition
import numpy as np
from fastapi import Body

#from app.classes.Cliente import Cliente
from app.classes.Cliente   import Cliente
from app.config.jwt_manager import jwt_manager

BASE_DIR = Path(__file__).resolve().parent.parent

# Ruta a la carpeta de imágenes
RUTA_IMG_CLIENTES = BASE_DIR / "img" / "clientes"/"imagenes_clientes.pkl"

router = APIRouter()

@router.get('/')
async def clientes():
    clientes = Cliente()
    resultado = clientes.all()
    return  {
        "message": "Datos recuperados exitosamente",
        "data": resultado
    }
@router.get('/{uid}')
async def clientes(
    uid: str
):
    estado = False
   
    if Cliente().has_imagen(uid):
        estado = True
        return  {
            "estado": estado
        }
    else:
        
        return  {
            "estado": estado
        }
        


@router.post("/")
async def registrar_cliente(
    request: dict = Body(...)
):
    try:
        # Crear instancia del cliente
        cliente = Cliente()
        cliente.sincronizar(request)
        
        # Validar los datos
        if not cliente.validar():
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Error de validación",
                    "errors": cliente.errores
                }
            )
        
        # Intentar guardar
        if cliente.guardar():
            access_token = jwt_manager.create_access_token({
                "sub": cliente.id_cliente,
                "email": cliente.email,
                "uid": cliente.uid,
                "rol": "cliente"
            })
            return {
                "success": True,
                "message": "Cliente registrado exitosamente",
                "id_cliente": cliente.id_cliente,
                "email": cliente.email,
                "access_token": access_token
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Error al guardar en base de datos",
                    "db_error": getattr(cliente, 'db_error', 'Error desconocido')
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.get("/verificar-biometria/{uid}")
async def verificar_biometria(
    uid: str
):
    """
    Verifica si un cliente tiene biometría registrada.
    
    Args:
        uid (str): UID del cliente a verificar
        
    Returns:
        dict: Diccionario con el estado de la biometría
    """
    try:
        if Cliente().has_imagen(uid):
            return {
                
                "message": "Biometría encontrada",
                "biometria_registrada": True
            }
        else:
            return {
                
                "message": "Biometría no encontrada",
                "biometria_registrada": False
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )       

@router.post("/verificar-imagen/{uid}")
async def verificar_imagen(
    uid:str,
    imagen: UploadFile = File(...),
    imagen2: UploadFile = File(...)
):
    
    def guardar(imagen):
        try:
            import pickle

            if imagen:
                ext = os.path.splitext(imagen.filename)[1]  # Extrae extensión (.png, .jpg)
                nombre_unico = f"{uuid.uuid4().hex}{ext}"   # Genera nombre único como antes

                imagen_bytes = imagen.file.read()
                nparr = np.frombuffer(imagen_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is None:
                    return None

                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_img)

                if len(face_locations) != 1:
                    return None

                encodings = face_recognition.face_encodings(rgb_img, face_locations)
                if not encodings:
                    return None

                embedding = encodings[0]

                # Cargar el archivo .pkl si existe
                if RUTA_IMG_CLIENTES.exists():
                    with open(RUTA_IMG_CLIENTES, "rb") as f:
                        datos = pickle.load(f)
                else:
                    datos = {}

                # Guardar embedding usando el nombre del archivo como clave
                datos[nombre_unico] = embedding

                # Escribir de nuevo el archivo
                with open(RUTA_IMG_CLIENTES, "wb") as f:
                    pickle.dump(datos, f)

                return nombre_unico  # 🔁 Esto mantiene tu lógica original de retorno
            return None
        except Exception as e:
            logging.error(f"Error al guardar embedding con nombre único: {e}")
            return None

    try:
        # Leer la imagen
        contents = await imagen.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Imagen no válida")
        
        # Convertir a RGB (face_recognition usa RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detectar rostros
        face_locations = face_recognition.face_locations(rgb_img)
        
        if not face_locations:
            return {
                "valido": False,
                "mensaje": "No se detectó ningún rostro en la imagen",
                "detalles": {
                    "rostro_detectado": False,
                    "accesorios": None
                }
            }
# Verificar enfoque
        nivel_enfoque = calcular_nivel_enfoque(img)
        UMBRAL_ENFOQUE = 100  # Ajusta este valor según tus necesidades
        
        if nivel_enfoque < UMBRAL_ENFOQUE:
            return {
                "valido": False,
                "mensaje": "Imagen borrosa o fuera de foco",
                "detalles": {
                    "rostro_detectado": False,
                    "enfoque": float(nivel_enfoque),
                    "umbral_enfoque": UMBRAL_ENFOQUE,
                    "accesorios": None
                }
            }
        
        if len(face_locations) > 1:
            return {
                "valido": False,
                "mensaje": "Se detectó más de un rostro en la imagen",
                "detalles": {
                    "rostro_detectado": True,
                    "multiples_rostros": True,
                    "accesorios": None
                }
            }
        
        # Analizar el primer rostro detectado
        top, right, bottom, left = face_locations[0]
        face_image = rgb_img[top:bottom, left:right]
        face_landmarks = face_recognition.face_landmarks(face_image)
        
        if not face_landmarks:
            return {
                "valido": False,
                "mensaje": "No se pudieron detectar características faciales",
                "detalles": {
                    "rostro_detectado": True,
                    "multiples_rostros": False,
                    "accesorios": None
                }
            }
        
        #Detección mejorada de accesorios
        has_glasses = bool(detect_glasses_improved(face_image, face_landmarks[0]))
        has_hat = bool(detect_headwear_fast(face_image, face_landmarks[0]))
        
        if has_glasses or has_hat:
            return {
                "valido": False,
                "mensaje": "Rostro con accesorios detectados",
                "detalles": {
                    "rostro_detectado": True,
                    "multiples_rostros": False,
                    "accesorios": {
                        "lentes": has_glasses,
                        "gorra_sombrero": has_hat
                    }
                }
            }
        if Cliente().update_imagen_by_uid(uid, guardar(imagen2)):
        
            return {
                "valido": True,
                "mensaje": "Rostro válido detectado",
                "detalles": {
                    "rostro_detectado": True,
                    "multiples_rostros": False,
                    "accesorios": {
                        "lentes": False,
                        "gorra_sombrero": False
                    }
                }
            }
        else:
            return{
                "valido": False,
                "mensaje": "No se pudo guardar la imagen",
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar imagen: {str(e)}")
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar la imagen"
        )

def detect_glasses_improved(face_image, landmarks, debug=False):
    """
    Detección optimizada para Flutter con:
    - Cámara frontal (selfies)
    - ResolutionPreset.high
    - Formato YUV420
    - Mejor adaptación a condiciones variables de luz
    """
    if 'left_eye' not in landmarks or 'right_eye' not in landmarks:
        return False

    # 1. Preprocesamiento específico para YUV420 de móvil
    if len(face_image.shape) == 3:
        gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
        # Corrección de contraste para selfies
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
    else:
        gray = face_image
    
    # 2. Ajustar región ocular para selfies frontales
    left_eye = np.array(landmarks['left_eye'])
    right_eye = np.array(landmarks['right_eye'])
    
    # Área más amplia para compensar calidad móvil
    eye_region_width = int(face_image.shape[1] * 0.4)
    eye_region_height = int(face_image.shape[0] * 0.25)
    
    # Calcular ROI centrada en ojos
    eyes_center_x = int((left_eye[:, 0].mean() + right_eye[:, 0].mean()) / 2)
    eyes_center_y = int((left_eye[:, 1].mean() + right_eye[:, 1].mean()) / 2)
    
    x1 = max(0, eyes_center_x - eye_region_width // 2)
    x2 = min(face_image.shape[1], eyes_center_x + eye_region_width // 2)
    y1 = max(0, eyes_center_y - eye_region_height // 3)
    y2 = min(face_image.shape[0], eyes_center_y + eye_region_height // 3)
    
    eye_roi = gray[y1:y2, x1:x2]
    
    # 3. Detección mejorada para móviles
    ## a. Detección de marcos con parámetros adaptativos
    edges = cv2.Canny(eye_roi, 30, 100, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 
                          threshold=15,  # Más bajo para calidad móvil
                          minLineLength=10, 
                          maxLineGap=5)
    
    ## b. Análisis de reflectividad en ROI
    hsv = cv2.cvtColor(face_image[y1:y2, x1:x2], cv2.COLOR_RGB2HSV) if len(face_image.shape) == 3 \
          else cv2.cvtColor(cv2.cvtColor(face_image[y1:y2, x1:x2], cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2HSV)
    
    brightness = np.mean(hsv[:,:,2])
    saturation = np.mean(hsv[:,:,1])
    
    ## c. Detección de lentes oscuros con umbral dinámico
    avg_brightness = np.mean(gray)
    dark_threshold = max(30, avg_brightness * 0.3)  # Umbral más bajo para móviles
    
    # 4. Sistema de puntuación mejorado
    score = 0
    
    # Marcos de lentes (líneas detectadas)
    if lines is not None:
        horizontal_lines = sum(1 for line in lines 
                             if abs(line[0][1] - line[0][3]) < 5)  # Líneas horizontales
        if horizontal_lines >= 2:
            score += 40
    
    # Reflectividad (lentes con brillo)
    if brightness > 130 and saturation < 70:  # Umbrales más flexibles
        score += 30
    
    # Lentes oscuros (poca luz en ojos)
    eye_left = gray[left_eye[:,1].min():left_eye[:,1].max(), 
                   left_eye[:,0].min():left_eye[:,0].max()]
    eye_right = gray[right_eye[:,1].min():right_eye[:,1].max(), 
                    right_eye[:,0].min():right_eye[:,0].max()]
    
    if (np.mean(eye_left) < dark_threshold and 
        np.mean(eye_right) < dark_threshold):
        score += 30

    # Debug visual
    if debug:
        debug_img = face_image.copy() if len(face_image.shape) == 3 \
                   else cv2.cvtColor(face_image, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(debug_img, f"Score: {score}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Glasses Detection", debug_img)
        cv2.waitKey(0)

    return score >= 60  # Umbral más bajo para móviles
def detect_headwear_fast(face_rgb, landmarks, k_int=25, k_var=200):
    """
    Detección ligera de gorra/capucha optimizada para velocidad.
    Combina diferencia de intensidad y textura.
    """
    if 'forehead' not in landmarks or 'chin' not in landmarks:
        return False

    gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)

    forehead_y = landmarks['forehead'][0][1]
    chin_y     = landmarks['chin'][-1][1]
    face_h     = chin_y - forehead_y

    # --- 1. ROI superior más grande (40 % de la cara) ----------
    top_h  = int(face_h * 0.40)
    top_y1 = max(0, forehead_y - top_h)
    top_roi  = gray[top_y1:forehead_y, :]

    # --- 2. ROI de referencia en la frente ----------------------
    ref_h  = int(face_h * 0.15)
    face_roi = gray[forehead_y:forehead_y + ref_h, :]

    if top_roi.size == 0 or face_roi.size == 0:
        return False

    # --- 3. Métricas -------------------------------------------
    diff_intensity = abs(np.mean(top_roi) - np.mean(face_roi))
    diff_texture   = abs(np.var(top_roi)  - np.var(face_roi))

    # Umbrales adaptativos: bajamos si la imagen es muy oscura
    exposure = np.mean(gray)
    adapt_int = k_int * (0.6 if exposure < 80 else 1.0)

    return (diff_intensity > adapt_int) or (diff_texture > k_var)


@router.get("/buscar-por-uid/{uid}")
async def buscar_cliente_por_uid(uid: str):
    """
    Busca un cliente por su UID único y devuelve sus datos si existe.
    
    Args:
        uid (str): El UID único del cliente a buscar
        
    Returns:
        dict: Diccionario con los datos del cliente si se encuentra, o mensaje de error
    """
    try:
        cliente = Cliente.find_by_uid(uid)
        
        if cliente:
            return {
                "success": True,
                "message": "Cliente encontrado",
                "data": {
                    "id_cliente": cliente.id_cliente,
                    "uid": cliente.uid,
                    "nombres": cliente.nombres,
                    "ap_paterno": cliente.ap_paterno,
                    "ap_materno": cliente.ap_materno,
                    "ci": cliente.ci,
                    "fcm_token": cliente.fcm_token,
                    "email": cliente.email,
                    "password": cliente.password,
                    "celular": cliente.celular,
                    "direccion": cliente.direccion,
                    "fecha_registro": cliente.fecha_registro,
                    "preferencias": cliente.preferencias,
                    "latitud": cliente.latitud,
                    "longitud": cliente.longitud,
                    "imagen_cliente": cliente.imagen_cliente                  
                }
            }
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "message": "Cliente no encontrado",
                    "error": f"No existe un cliente con el UID: {uid}"
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Error al buscar cliente",
                "error": str(e)
            }
        )


# Cargar embeddings del archivo .pkl
def cargar_embeddings():
    if RUTA_IMG_CLIENTES.exists():
        with open(RUTA_IMG_CLIENTES, "rb") as f:
            return pickle.load(f)
    return {}

# Guardar embeddings al archivo .pkl
def guardar_embeddings(embeddings):
    with open(RUTA_IMG_CLIENTES, "wb") as f:
        pickle.dump(embeddings, f)

# Extraer el embedding y guardarlo
def procesar_y_guardar_embedding(uid, imagen_file):
    try:
        imagen_bytes = imagen_file.file.read()
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return False

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img)

        if len(face_locations) != 1:
            return False  # No rostro o más de uno

        encodings = face_recognition.face_encodings(rgb_img, face_locations)

        if not encodings:
            return False

        encoding = encodings[0]  # Embedding de 128 dimensiones

        embeddings = cargar_embeddings()
        embeddings[uid] = encoding  # Guardamos por UID
        guardar_embeddings(embeddings)

        return True
    except Exception as e:
        logging.error(f"Error al guardar embedding: {e}")
        return False

def calcular_nivel_enfoque(imagen, umbral=100):
    """Calcula el nivel de enfoque usando la varianza de Laplace"""
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return laplacian.var()

@router.post("/comparar-imagen/{uid}")
async def comparar_imagen(
    uid: str,
    imagen: UploadFile = File(...)
):
    import pickle
    import numpy as np
    import cv2
    from fastapi import HTTPException

    try:
        # Leer imagen
        contenido = await imagen.read()
        nparr = np.frombuffer(contenido, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Imagen no válida")

        # Convertir a RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Reescalar si la imagen es muy grande
        max_dimension = 800
        height, width = rgb_img.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / float(max(height, width))
            rgb_img = cv2.resize(rgb_img, (int(width * scale), int(height * scale)))

        # Mejorar iluminación y contraste
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
        gray = cv2.equalizeHist(gray)
        rgb_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

        # Detectar rostro con modelo "hog" (puedes cambiar a "cnn" si tienes GPU)
        face_locations = face_recognition.face_locations(rgb_img, model="hog")

        if  not face_locations:
            return {
                "match": False,
                "distancia": 0,
                "mensaje": "No se detectó ningún rostro en la imagen. Asegúrate de que esté bien iluminada, centrada y sin obstrucciones."
            }
        elif len(face_locations) > 1:
            return {
                "match": False,
                "distancia": None,
                "mensaje": "Se detectaron múltiples rostros en la imagen. Por favor, asegúrate de que solo una persona esté frente a la cámara."
            }

        # Verificar landmarks (estructura facial)
        face_landmarks_list = face_recognition.face_landmarks(rgb_img, face_locations)
        if not face_landmarks_list or not face_landmarks_list[0]:
            return {
                "match": False,
                "distancia": None,
                "mensaje": "No se detectaron características faciales suficientes (landmarks)."
            }

        # Obtener embedding de la imagen recibida
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        if not face_encodings:
            raise HTTPException(status_code=400, detail="No se pudo extraer embedding facial")
        nuevo_embedding = face_encodings[0]

        # Verificar si existen los embeddings guardados
        if not RUTA_IMG_CLIENTES.exists():
            raise HTTPException(status_code=404, detail="No hay embeddings guardados")

        with open(RUTA_IMG_CLIENTES, "rb") as f:
            embeddings_guardados = pickle.load(f)

        # Obtener datos del cliente
        cliente = Cliente.find_by_uid(uid)
        print(cliente.imagen_cliente)
        if not cliente or not cliente.imagen_cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado o sin embedding asociado")

        embedding_guardado = embeddings_guardados.get(cliente.imagen_cliente)
        if embedding_guardado is None:
            raise HTTPException(status_code=404, detail="Embedding facial no encontrado para este cliente")

        # Comparar embeddings
        distancia = np.linalg.norm(embedding_guardado - nuevo_embedding)
        umbral = 0.6  # Ajustable
        es_mismo = distancia < umbral

        return {
            "match": bool(es_mismo),
            "distancia": float(distancia),
            "mensaje": "Rostros coinciden" if es_mismo else "Rostros diferentes"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al comparar imágenes: {str(e)}")
