from fastapi import FastAPI,HTTPException,Header
from jose import jwt
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

token = "dan321"

conn = psycopg2.connect(
    host="localhost",
    database="inventarioDB",
    user="postgres",
    password="dan"
)

def verificaToken(authorization: str = Header()):
    try:
        clave = authorization.split(" ")[1]
        jwt.decode(clave,token,algorithms=["HS256"])
    except:
        logging.error("token invalido - acceso denegado")
        raise HTTPException(status_code=401, detail="token invalido")


@app.get("/token")
def generarToken():
    Token = jwt.encode({"token": "admin"},token,algorithm="HS256")
    return {"token": Token}

@app.get("/inventario")
def obtenerProductos(authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    logging.info("se obtuvo los datos de productos")
    return {"productos": productos}

@app.get("/inventario/{id}")
def obtenerProductoid(id: int,authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM productos WHERE id = %s ",
        (id,)
    )
    producto = cursor.fetchone()
    
    if producto is None:
        logging.info(f"producto no encontrado - id: {id}")
        raise HTTPException(status_code=402, detail="producto no encontrado")
    logging.info(f"se obtuvo producto - id: {id}")
    return {"producto": producto}

@app.post("/inventario")
def crearProductos(
    nombre: str,
    precio: int, 
    stock: int, 
    authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre,precio,stock) VALUES (%s,%s,%s)",
        (nombre,precio,stock)
    )
    conn.commit()
    logging.info("se insertaron productos correctamente")
    return {"mensaje" : "producto creado exitosamente"}

@app.put("/inventario/{id}")
def actualizarProducto(
    id: int,
    nombre: str,
    precio: int,
    stock: int,
    authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos " \
        "SET nombre = %s,precio = %s,stock = %s " \
        "WHERE id = (%s)",
        (nombre,precio,stock,id)
    )
    conn.commit()
    logging.info("se actualizo producto correcctamente")
    return {"mensaje": "productos actualizaddo correctamente"}

@app.delete("/inventario/{id}")
def eliminarProducto(
    id: int,
    authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM productos " \
        "WHERE id = %s",
        (id,)
    )
    conn.commit()
    logging.info("se elimino producto correctamente")
    return {"mensaje": "producto eliminado correctamente"}

 