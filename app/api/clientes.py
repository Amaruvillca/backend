from datetime import date
import logging
import shutil
import uuid
import cv2
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
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
        UMBRAL_ENFOQUE =30  # Ajusta este valor según tus necesidades
        
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
        has_glasses = bool(detect_glasses_selfie(face_image, face_landmarks[0]))
        has_hat = bool(detect_headwear_improved(face_image, face_landmarks[0]))
        
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

import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

import cv2
import numpy as np
import mediapipe as mp
import base64

mp_face_mesh = mp.solutions.face_mesh

def detect_glasses_selfie(image_input, debug=False):
    """
    Detección de lentes optimizada para selfies frontales.
    Recibe:
      - np.ndarray (imagen ya cargada, RGB o BGR)
      - bytes
      - base64 string (data:image/jpeg;base64,...)
    No acepta rutas de archivo.
    """

    # === 1. Cargar correctamente la imagen según su tipo ===
    if isinstance(image_input, np.ndarray):
        img = image_input
    elif isinstance(image_input, bytes):
        img = cv2.imdecode(np.frombuffer(image_input, np.uint8), cv2.IMREAD_COLOR)
    elif isinstance(image_input, str) and image_input.startswith("data:image"):
        header, encoded = image_input.split(",", 1)
        img_data = base64.b64decode(encoded)
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    else:
        raise ValueError("Formato de imagen no válido. Debe ser ndarray, bytes o base64 string.")

    if img is None:
        raise ValueError("❌ No se pudo decodificar la imagen correctamente.")

    # Convertir a RGB (MediaPipe trabaja en RGB)
    if img.shape[2] == 3:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        rgb = img.copy()

    # === 2. Detección facial con MediaPipe FaceMesh ===
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                               refine_landmarks=True, min_detection_confidence=0.6) as face_mesh:
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        if debug:
            print("⚠️ No se detectó rostro.")
        return False

    face_landmarks = results.multi_face_landmarks[0]
    h, w, _ = rgb.shape
    pts = [(int(p.x * w), int(p.y * h)) for p in face_landmarks.landmark]

    # Índices aproximados de ojos y cejas
    left_eye_idx = [33, 133, 159, 145, 153]
    right_eye_idx = [362, 263, 386, 374, 380]
    left_brow_idx = [55, 65, 52, 53, 46]
    right_brow_idx = [285, 295, 282, 283, 276]

    def get_region(idx_list):
        pts_region = np.array([pts[i] for i in idx_list])
        x1, y1 = np.min(pts_region, axis=0)
        x2, y2 = np.max(pts_region, axis=0)
        return [max(0, x1-5), max(0, y1-5), min(w, x2+5), min(h, y2+5)]

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    score = 0

    # === 3. CONTRASTE OJOS / ROSTRO ===
    for idx_list in [left_eye_idx, right_eye_idx]:
        x1, y1, x2, y2 = get_region(idx_list)
        eye = gray[y1:y2, x1:x2]
        if eye.size == 0:
            continue
        expand = 20
        x1s, y1s = max(0, x1-expand), max(0, y1-expand)
        x2s, y2s = min(w, x2+expand), min(h, y2+expand)
        surround = gray[y1s:y2s, x1s:x2s]

        eye_mean = np.mean(eye)
        surround_mean = np.mean(surround)
        ratio = eye_mean / (surround_mean + 1)
        if ratio < 0.7:
            score += 20
        elif ratio < 0.85:
            score += 10

    # === 4. LÍNEAS DE MONTURA ===
    x1b, y1b, x2b, y2b = get_region(left_brow_idx + right_brow_idx)
    frame_zone = gray[y1b:y2b, x1b:x2b]
    frame_zone = cv2.equalizeHist(frame_zone)  # ecualiza el histograma y mejora contraste

    if frame_zone.size > 0:
        edges = cv2.Canny(frame_zone, 70, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30,
                                minLineLength=(x2b-x1b)//3, maxLineGap=6)
        if lines is not None:
            horizontal = sum(
                1 for l in lines
                if abs(np.arctan2(l[0][3]-l[0][1], l[0][2]-l[0][0])*180/np.pi) < 12
            )
            if horizontal >= 2:
                score += 30
            elif horizontal == 1:
                score += 15

    # === 5. REFLEXIONES ===
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    reflections = np.sum((hsv[:, :, 1] < 70) & (hsv[:, :, 2] > 210))
    reflection_ratio = reflections / (hsv.shape[0] * hsv.shape[1])
    if reflection_ratio > 0.05:
        score += 20
    elif reflection_ratio > 0.03:
        score += 10

    # === 6. DECISIÓN FINAL ===
    if debug:
        print(f"👓 Score total: {score} (Umbral: 45)")
    return score >= 45



def get_landmarks(image):
    """
    Detecta landmarks faciales usando Mediapipe FaceMesh
    """
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(image)
        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = image.shape

        # Índices aproximados de ojos y cejas
        left_eye_idx = [33, 133, 160, 159, 158, 157, 173]
        right_eye_idx = [362, 263, 387, 386, 385, 384, 398]
        left_brow_idx = [70, 63, 105, 66, 107]
        right_brow_idx = [336, 296, 334, 293, 300]

        def to_np(idx_list):
            return np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in idx_list])

        return {
            'left_eye': to_np(left_eye_idx),
            'right_eye': to_np(right_eye_idx),
            'left_eyebrow': to_np(left_brow_idx),
            'right_eyebrow': to_np(right_brow_idx)
        }


def detect_from_image(path):
    """
    Carga una imagen, detecta rostro y determina si tiene lentes
    """
    image_bgr = cv2.imread(path)
    if image_bgr is None:
        raise ValueError("No se pudo leer la imagen")

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    landmarks = get_landmarks(image_rgb)
    if not landmarks:
        print("No se detectó rostro.")
        return False

    has_glasses = detect_glasses_selfie(image_rgb, landmarks, debug=True)
    print("👓 Tiene lentes:", has_glasses)
    return has_glasses


if __name__ == "__main__":
    # Ejemplo de uso con una imagen local
    detect_from_image("rostro.jpg")


def detect_headwear_improved(face_rgb, landmarks, debug=False):
    """
    Detección mejorada de gorras/sombreros para selfies
    """
    if 'forehead' not in landmarks or 'chin' not in landmarks:
        return False

    gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
    
    # Mejorar contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    forehead_y = landmarks['forehead'][0][1]
    chin_y = landmarks['chin'][-1][1]
    face_height = chin_y - forehead_y

    # Definir regiones de análisis
    top_region_height = int(face_height * 0.4)  # 40% superior
    top_y1 = max(0, forehead_y - top_region_height)
    top_roi = gray[top_y1:forehead_y, :]
    
    face_region_height = int(face_height * 0.3)  # 30% de la cara
    face_roi = gray[forehead_y:forehead_y + face_region_height, :]

    if top_roi.size == 0 or face_roi.size == 0:
        return False

    score = 0
    
    # 1. ANÁLISIS DE INTENSIDAD (principal)
    top_intensity = np.mean(top_roi)
    face_intensity = np.mean(face_roi)
    intensity_diff = abs(top_intensity - face_intensity)
    
    # Diferencia significativa de intensidad
    if intensity_diff > 30:
        score += 35
    elif intensity_diff > 20:
        score += 20
    
    # 2. ANÁLISIS DE TEXTURA
    top_texture = np.var(top_roi)
    face_texture = np.var(face_roi)
    
    # Gorras suelen tener textura diferente
    if top_texture > face_texture * 2.0:
        score += 25
    elif top_texture < face_texture * 0.5:
        score += 20
    
    # 3. DETECCIÓN DE BORDES (visera de gorra)
    top_edges = cv2.Canny(top_roi, 50, 150)
    face_edges = cv2.Canny(face_roi, 50, 150)
    
    # Buscar bordes horizontales en la parte superior
    horizontal_kernel = np.ones((1, 15), np.uint8)
    horizontal_edges = cv2.morphologyEx(top_edges, cv2.MORPH_OPEN, horizontal_kernel)
    
    horizontal_edge_ratio = np.sum(horizontal_edges > 0) / top_roi.size
    
    if horizontal_edge_ratio > 0.05:  # 5% de bordes horizontales
        score += 20
    
    # 4. ANÁLISIS DE COLOR (gorras de colores)
    hsv = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2HSV)
    top_hsv = hsv[top_y1:forehead_y, :]
    face_hsv = hsv[forehead_y:forehead_y + face_region_height, :]
    
    # Diferencia de color
    hue_diff = abs(np.mean(top_hsv[:,:,0]) - np.mean(face_hsv[:,:,0]))
    sat_diff = abs(np.mean(top_hsv[:,:,1]) - np.mean(face_hsv[:,:,1]))
    
    if hue_diff > 20 or sat_diff > 40:
        score += 15
    
    # 5. FORMA DE LA CABEZA
    # Calcular el ancho en diferentes alturas
    if 'chin' in landmarks and 'forehead' in landmarks:
        chin_width = landmarks['chin'][-1][0] - landmarks['chin'][0][0]
        forehead_width = landmarks['forehead'][-1][0] - landmarks['forehead'][0][0]
        
        # Con gorra, la parte superior suele ser más ancha
        if forehead_width > chin_width * 1.2:
            score += 15
    
    # Debug
    if debug:
        print(f"Headwear detection score: {score}")
        debug_img = face_rgb.copy()
        
        # Dibujar regiones
        cv2.rectangle(debug_img, (0, top_y1), (gray.shape[1], forehead_y), (255, 0, 0), 2)
        cv2.rectangle(debug_img, (0, forehead_y), (gray.shape[1], forehead_y + face_region_height), (0, 255, 0), 2)
        
        cv2.putText(debug_img, f"Score: {score}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Headwear Debug", debug_img)
        cv2.waitKey(0)
    
    return score >= 50

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

def calcular_nivel_enfoque(imagen, umbral=30):
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

@router.put("/actualizarfscm/")
async def actualizar_fscm(uid: str, fcm: str):
    try:
        # Lógica para actualizar el FSCM del cliente
        cliente = Cliente.actualizar_fscm(uid, fcm)
        if cliente:
            return JSONResponse(status_code=200, content={              
                "success": True,
                "message": "FCM actualizado exitosamente"
            })
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "message": "Cliente no encontrado para actualizar FCM"
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Error al actualizar FCM",
                "error": str(e)
            }
        )