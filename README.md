# 💪 GymLog

App de seguimiento de entrenamientos con perfiles de usuario (Admin / Profesor / Cliente), splits por grupos musculares, historial con gráficas y cronómetro de descanso.

## Stack
- **Backend:** Python · Flask · PyMongo
- **Base de datos:** MongoDB (Atlas para producción)
- **Frontend:** HTML/CSS/JS vanilla (en `/static`)
- **Deploy:** Render

---

## Estructura MVC

```
gymlog/
├── app.py               ← Entry point Flask
├── requirements.txt
├── render.yaml          ← Config de deploy en Render
├── .env.example
├── config/
│   └── db.py            ← Conexión MongoDB (singleton)
├── models/
│   ├── user.py          ← Usuarios + seed inicial
│   ├── exercise.py      ← Ejercicios globales y personalizados
│   ├── split.py         ← Splits y asignación a clientes
│   └── workout.py       ← Sesiones de entrenamiento
├── controllers/
│   ├── auth.py          ← Autenticación, perfiles, week_plan
│   ├── exercises.py
│   ├── splits.py
│   └── workouts.py
├── routes/
│   ├── __init__.py      ← Registra todos los blueprints
│   ├── auth.py
│   ├── exercises.py
│   ├── splits.py
│   └── workouts.py
└── static/
    └── index.html       ← Frontend completo
```

---

## Setup local

### 1. Clonar e instalar dependencias
```bash
git clone <repo>
cd gymlog
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env con tu MONGODB_URI y SECRET_KEY
```

### 3. Correr
```bash
python app.py
# → http://localhost:5000
```

El primer arranque crea automáticamente el usuario **Admin** (PIN: `0000`) y carga los ejercicios por defecto.

---

## Deploy en Render

### 1. MongoDB Atlas
1. Crea un cluster gratuito en [mongodb.com/atlas](https://mongodb.com/atlas)
2. Crea un usuario de base de datos con permisos read/write
3. Copia el connection string: `mongodb+srv://user:pass@cluster.mongodb.net/gymlog`
4. En **Network Access** → agrega `0.0.0.0/0` (permite conexiones desde Render)

### 2. Render
1. Crea cuenta en [render.com](https://render.com)
2. **New → Web Service** → conecta tu repo de GitHub
3. Render detecta automáticamente el `render.yaml`
4. En **Environment Variables** agrega:
   - `MONGODB_URI` → tu connection string de Atlas
   - `CORS_ORIGINS` → `https://tu-app.onrender.com`
5. Deploy → en ~2 minutos tu app está live

### Variables de entorno en Render
| Variable | Valor |
|---|---|
| `MONGODB_URI` | `mongodb+srv://...` |
| `MONGODB_DB` | `gymlog` |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | se genera automáticamente |
| `CORS_ORIGINS` | `https://tu-app.onrender.com` |

---

## Roles de usuario

| Rol | Permisos |
|---|---|
| **Admin** | Ve y gestiona todos los usuarios y sus datos |
| **Profesor** | Crea clientes, les asigna splits, ve su historial |
| **Cliente** | Solo ve y gestiona sus propios entrenamientos |

El Admin inicial se crea con PIN `0000`. **Cámbialo desde el panel de usuarios.**

---

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/users` | Lista usuarios (pública, para picker) |
| POST | `/api/auth/login` | Login con PIN |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Usuario actual |
| GET/POST | `/api/users` | Lista / crea usuarios |
| PUT/DELETE | `/api/users/<id>` | Edita / elimina usuario |
| GET | `/api/exercises` | Ejercicios (global + del usuario) |
| POST/PUT/DELETE | `/api/exercises` | CRUD ejercicios |
| GET/POST | `/api/splits` | Splits del usuario |
| DELETE | `/api/splits/<id>` | Elimina split |
| POST | `/api/splits/<id>/assign` | Asigna split a clientes |
| GET/PUT | `/api/week_plan` | Plan semanal |
| GET/POST/DELETE | `/api/workouts` | Historial de entrenamientos |
