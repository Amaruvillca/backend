# 🧠 API REST de Reconocimiento Facial y Gestión Empresarial con FastAPI

Este proyecto es una API REST construida con **FastAPI** que permite:

- Reconocimiento facial usando un modelo **ResNet50 preentrenado**.
- Gestión de sucursales, productos, categorías y usuarios.
- Carga y almacenamiento de imágenes asociadas a productos y sucursales.
- Arquitectura extensible y lista para producción.

## 🚀 Características

- 📷 Carga de imágenes para detección facial y productos.
- 🧠 Extracción de características faciales usando ResNet50.
- 🔍 Comparación de rostros (verificación de identidad).
- 🏪 Gestión CRUD de sucursales, productos, categorías y usuarios.
- 🌐 API REST lista para producción.
- 🔧 Docker-ready y extensible para múltiples modelos y entidades.

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
- El frontend HTML se encuentra en la carpeta `frontend/`.

---

## 🧑‍💻 Autor

- Proyecto Loyola

---
