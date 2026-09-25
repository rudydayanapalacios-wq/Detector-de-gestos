# GestureKiosk 🖐️

Sistema de **interacción sin contacto mediante gestos de la mano**, desarrollado con Django, FastAPI y MediaPipe.

El proyecto utiliza la cámara web para capturar la mano del usuario, detectar sus puntos de referencia (*landmarks*) y reconocer diferentes gestos para interactuar con un kiosco digital.

## 🚀 Tecnologías

- **Frontend:** Django, HTML, CSS y JavaScript
- **Backend:** FastAPI y Python
- **Reconocimiento:** MediaPipe Hand Landmarker + OpenCV
- **Autenticación:** JWT, Passlib y Bcrypt
- **Despliegue:** Docker

## 📁 Estructura

```text
Detector-de-gestos/
├── backend/
│   ├── app/
│   ├── hand_landmarker.task
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── kiosco/
│   ├── manage.py
│   └── requirements.txt
│
└── README.md
```

## 🧠 Funcionamiento

```text
Cámara web
    ↓
JavaScript
    ↓
Frontend Django
    ↓
API FastAPI
    ↓
MediaPipe
    ↓
Reconocimiento del gesto
    ↓
Respuesta al frontend
```

MediaPipe detecta los puntos de referencia de la mano y el backend utiliza esta información para identificar el gesto realizado.

## 🔐 Autenticación

El sistema cuenta con **registro e inicio de sesión**.  
Después de iniciar sesión, FastAPI genera un **JWT**, que se utiliza para acceder a los endpoints protegidos del detector.

## ⚙️ Instalación

### Backend

```bash
cd backend
python -m venv venv
```

Activar el entorno virtual y ejecutar:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API:

```text
http://localhost:8000
```

Documentación:

```text
http://localhost:8000/docs
```

### Frontend

En otra terminal:

```bash
cd frontend
pip install -r requirements.txt
python manage.py runserver
```

## 🐳 Docker

El backend incluye un `Dockerfile` preparado para ejecutar FastAPI junto con MediaPipe y OpenCV.

```bash
cd backend
docker build -t gesturekiosk-backend .
docker run -p 10000:10000 gesturekiosk-backend
```

## 🎯 Objetivo

Crear un kiosco digital que permita al usuario interactuar mediante **gestos de la mano**, reduciendo la necesidad de contacto físico y combinando desarrollo web con visión por computador.

## 🔗 Enlaces del proyecto

- 🖥️ **Frontend:** https://detector-de-gestos.vercel.app/
- ⚙️ **Backend:** https://detector-de-gestos-c6j4.onrender.com
- 📚 **Documentación API (Swagger):** https://detector-de-gestos-c6j4.onrender.com/docs
