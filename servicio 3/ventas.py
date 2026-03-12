from fastapi import FastAPI,HTTPException,Header
from jose import jwt
import psycopg2
import requests
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

fallos = 0          # cuenta los fallos consecutivos
circuito_abierto = False    # si True, no intenta consultar
tiempo_apertura = None      # cuando se abrió el circuito

token = "dan1234"

token_servicio2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6ImFkbWluIn0.umdkldA1oJg5ez0TM6cM44UM4d6UlAVck84yElwtLY8"

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
def generaToken():
    Token = jwt.encode({"usuario": "admin"}, token,algorithm="HS256")
    return {"token": Token}

@app.get("/ventas")
def obtenerVentas(authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas")
    ventas= cursor.fetchall()
    logging.info("se obtuvo ventas del producto")
    return {"mensaje":ventas}

@app.post("/ventas")
def crearVentas(productoID: int,cantidad: int,authorization: str = Header()):
    verificaToken(authorization)
    global fallos,circuito_abierto,tiempo_apertura
    if circuito_abierto:
        if time.time() - tiempo_apertura > 30:
            circuito_abierto = False
            fallos = 0
            logging.info("circuito cerrado, reintentando...")
        else:
            logging.error("circuito abierto, servicio no disponible")
            raise HTTPException(status_code=503, detail="servicio no disponible")
        
            
    for intentos in range(3):
        try:
            consultar = requests.get(
                f"http://127.0.0.1:8002/inventario/{productoID}",
                headers={"Authorization": f"Bearer {token_servicio2}"})
            if consultar.status_code == 200:
                break
        except:
            logging.warning(f"intento { intentos + 1} fallido, reitentando...")
            time.sleep(1)
    else:
        fallos +=1
        if fallos >= 3:
            circuito_abierto = True
            tiempo_apertura = time.time()
            logging.error("circuito abierto por demasiados fallos")

        logging.error(f"producto no encontrado despues de 3 intentos - id: {productoID}")
        raise HTTPException(status_code=402,detail="producto no encontrado")

    
    producto = consultar.json()["producto"]
    precio = producto[2]

    total = cantidad * precio

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ventas (producto_id,cantidad,total) VALUES (%s,%s,%s)",
        (productoID,cantidad,total)
    )
    conn.commit()
    logging.info(f"se inserto venta correctamente - id: {productoID}")
    return {"mensaje": "productos agregado correctamente"}