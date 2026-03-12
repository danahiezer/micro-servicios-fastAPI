# 🛒 Sistema de Microservicios
### Usuarios · Inventario · Ventas
> Python · FastAPI · PostgreSQL · JWT

---

## 📋 ¿Qué es este proyecto?

Este proyecto es mi primera implementación de una arquitectura de microservicios. Dividí un sistema en 3 servicios pequeños e independientes que se comunican entre sí a través de APIs REST.

Cada servicio tiene su propia base de datos, su propio puerto y su propia autenticación. La idea principal es que cada servicio haga una sola cosa y la haga bien.

---

## 🏗️ Arquitectura del sistema

| Servicio | Puerto | Base de datos | Responsabilidad |
|----------|--------|---------------|-----------------|
| 🐾 Usuarios | :8001 | usuariosDB | Gestión de usuarios |
| 📦 Inventario | :8002 | inventarioDB (productos) | Gestión de productos |
| 💰 Ventas | :8003 | inventarioDB (ventas) | Registro de ventas |

**Comunicación entre servicios:**
El servicio de Ventas consulta al servicio de Inventario via HTTP para verificar que el producto existe antes de registrar la venta. Los otros dos servicios son completamente independientes.

```
Ventas  →  HTTP GET  →  Inventario
```

---

## ⚙️ Requisitos previos

- Python 3.10+
- PostgreSQL
- Librerías de Python:

```bash
pip install fastapi uvicorn psycopg2-binary requests python-jose
```

---

## 🚀 Cómo correr el proyecto

### Paso 1 — Crear las tablas en PostgreSQL

```sql
-- usuariosDB
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    email VARCHAR
);

-- inventarioDB
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR,
    precio FLOAT,
    stock INTEGER
);

CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER,
    cantidad INTEGER,
    total FLOAT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Paso 2 — Correr cada servicio en una terminal distinta

**Servicio 1 — Usuarios (puerto 8001):**
```bash
cd "servicio 1"
uvicorn usuario:app --reload --port 8001
```

**Servicio 2 — Inventario (puerto 8002):**
```bash
cd "servicio 2"
uvicorn inventario:app --reload --port 8002
```

**Servicio 3 — Ventas (puerto 8003):**
```bash
cd "servicio 3"
uvicorn ventas:app --reload --port 8003
```

---

## 🔐 Autenticación JWT

Cada servicio usa su propio token JWT. Antes de usar cualquier endpoint hay que generar el token de ese servicio:

| Servicio | Endpoint para obtener token |
|----------|-----------------------------|
| Usuarios | GET http://localhost:8001/token |
| Inventario | GET http://localhost:8002/token |
| Ventas | GET http://localhost:8003/token |

Luego usarlo en el header de cada request:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

> Si el token no es válido o no se envía, el servicio responde con error **401**.

---

## 📡 Endpoints disponibles

### Servicio 1 — Usuarios (:8001)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /token | Genera un token JWT |
| GET | /usuarios | Obtiene todos los usuarios |
| POST | /usuarios | Crea un nuevo usuario (nombre, email) |
| PUT | /usuarios/{id} | Actualiza un usuario por ID |
| DELETE | /usuarios/{id} | Elimina un usuario por ID |

### Servicio 2 — Inventario (:8002)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /token | Genera un token JWT |
| GET | /inventario | Obtiene todos los productos |
| GET | /inventario/{id} | Obtiene un producto por ID |
| POST | /inventario | Crea un nuevo producto (nombre, precio, stock) |
| PUT | /inventario/{id} | Actualiza un producto por ID |
| DELETE | /inventario/{id} | Elimina un producto por ID |

### Servicio 3 — Ventas (:8003)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /token | Genera un token JWT |
| GET | /ventas | Obtiene todas las ventas |
| POST | /ventas | Registra una venta (productoID, cantidad) |

---

## 🛡️ Manejo de errores

### Logs
Cada servicio registra lo que pasa en la terminal con fecha, nivel y mensaje:

```
2026-03-12 10:30:00 - INFO  - usuario creado exitosamente
2026-03-12 10:31:00 - ERROR - token invalido - acceso denegado
2026-03-12 10:32:00 - WARNING - intento 1 fallido, reintentando...
```

- `INFO` → operaciones exitosas
- `WARNING` → intentos fallidos (retry)
- `ERROR` → errores graves o accesos denegados

### Retry *(solo en Ventas)*
Cuando el servicio de Ventas consulta al servicio de Inventario, si falla lo intenta hasta **3 veces** esperando **1 segundo** entre cada intento. Si los 3 intentos fallan, devuelve error 402.

```
Intento 1 → falla → espera 1s
Intento 2 → falla → espera 1s
Intento 3 → falla → error 402
```

### Circuit Breaker *(solo en Ventas)*
Si el servicio de Inventario acumula **3 fallos consecutivos**, el Circuit Breaker se abre y bloquea las consultas por **30 segundos** para no sobrecargar el sistema. Después vuelve a intentar automáticamente.

| Estado | Descripción |
|--------|-------------|
| 🟢 CERRADO | Todo normal, las requests fluyen con normalidad |
| 🔴 ABIERTO | Circuito cortado, responde inmediatamente con error 503 |

---

## 📝 Notas del desarrollador

Cosas que aprendí haciendo este proyecto:

- `jwt.encode` usa `algorithm` (sin s) y `jwt.decode` usa `algorithms` (con s). Son distintos y me costó darme cuenta.
- En psycopg2 cuando pasás un solo valor en una tupla hay que poner una coma al final: `(id,)`. Sin la coma Python no lo trata como tupla.
- El Circuit Breaker se llama "abierto" cuando está cortado, al revés de lo que uno pensaría. Es como un disyuntor eléctrico.
- Cada servicio tiene su propia clave secreta JWT, así los tokens no son intercambiables entre servicios.
- El token largo (`eyJ...`) se genera a partir de la clave secreta. La clave secreta nunca viaja en los headers, solo el token firmado.

---

*Desarrollado como proyecto de aprendizaje de microservicios con FastAPI* 🚀