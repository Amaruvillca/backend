ki# 🧠 API REST de Reconocimiento Facial y Gestión Empresarial con FastAPI

Este proyecto es una API REST construida con **FastAPI** que permite:

- Reconocimiento facial usando un modelo **ResNet50 preentrenado**.
- Gestión de sucursales, productos, categorías y usuarios.
- Carga y almacenamiento de imágenes asociadas a productos y sucursales.
- Arquitectura extensible y lista para producción.

---

## 🚀 Características

- 📷 Carga de imágenes para detección facial y productos.
- 🧠 Extracción de características faciales usando ResNet50.
- 🔍 Comparación de rostros (verificación de identidad).
- 🏪 Gestión CRUD de sucursales, productos, categorías y usuarios.
- 🌐 API REST lista para producción.
- 🔧 Docker-ready y extensible para múltiples modelos y entidades.

---

## 📦 Librerías principales utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework principal para la API.
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI para desarrollo y producción.
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM para la gestión de base de datos.
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validación de datos y modelos.
- **[python-multipart](https://andrew-d.github.io/python-multipart/)** - Manejo de formularios y archivos.
- **[Pillow](https://python-pillow.org/)** - Procesamiento de imágenes.
- **[TensorFlow](https://www.tensorflow.org/)** y/o **[Keras](https://keras.io/)** - Para el modelo ResNet50.
- **[PyTorch](https://pytorch.org/)** - Alternativa para modelos de deep learning y procesamiento de imágenes.
- **[NumPy](https://numpy.org/)** - Operaciones numéricas y manejo de arrays.
- **[Shutil, OS, JSON, Pathlib]** - Librerías estándar para manejo de archivos y utilidades.

---

## 🛠️ Requisitos

- Python 3.8+
- pip

> Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## 📁 Estructura del Proyecto

```
backend/
│
├── app/
│   ├── api/           # Endpoints FastAPI (sucursales, productos, categorías, usuarios)
│   ├── classes/       # Modelos ORM (Sucursal, Producto, Categoria, Usuario, Activerecord)
│   ├── config/        # Configuración de la base de datos
│   └── ...            # Otros módulos
│
├── frontend/          # Archivos HTML y JS para la interfaz web
│
├── img/               # Imágenes subidas (productos, sucursales)
│
├── requirements.txt   # Dependencias del proyecto
└── README.md
```

---

## 🛣️ Endpoints Principales

- `/api/sucursales/`   → CRUD de sucursales
- `/api/productos/`    → CRUD de productos
- `/api/categorias/`   → CRUD de categorías
- `/api/usuarios/`     → CRUD de usuarios
- `/api/face/`         → Reconocimiento facial (subida y comparación de imágenes)

---

## ⚡ Ejecución

1. Clona el repositorio y entra al directorio `backend`.
2. Instala las dependencias.
3. Inicia el servidor:

```bash
uvicorn app.main:app --reload
```

4. Accede a la documentación interactiva en:  
   [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📝 Notas

- Las imágenes subidas se almacenan en la carpeta `img/`.
- Puedes probar los endpoints desde la documentación Swagger.

---

## 🧑‍💻 Autor

- Proyecto Loyola

---
