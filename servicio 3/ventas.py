from fastapi import FastAPI,HTTPException,Header
from jose import jwt
import psycopg2
import requests
import logging
import time

logging.basicConfig(
    level=logging.INFO,  # --> nivel de log (info)
    format="%(asctime)s - %(levelname)s - %(message)s" # --> formato de como se vera log
)

app = FastAPI() # --> crea framework motor fastAPI

fallos = 0          # cuenta los fallos consecutivos
circuito_abierto = False    # si True, no intenta consultar
tiempo_apertura = None      # cuando se abrió el circuito

token = "dan1234" # --> clave secreta para el servicio de ventas

tokenInventario = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6ImFkbWluIn0.umdkldA1oJg5ez0TM6cM44UM4d6UlAVck84yElwtLY8" # --> Token de inventario para autenticar mas abajo

conn = psycopg2.connect(
    host="localhost",
    database="inventarioDB", # --> conexion a mi base de datos
    user="postgres",
    password="dan"
)

# verifica token
def verificaToken(authorization: str = Header()):
    try:
        clave = authorization.split(" ")[1] # --> separa token con espacio y accede con [1] al token
        jwt.decode(clave,token,algorithms=["HS256"]) # --> verifica la firma y si no coincide jwt.decode la rechaza
    except:
        logging.error("token invalido - acceso denegado")
        raise HTTPException(status_code=401, detail="token invalido") # --> log y estado de codigo
    
@app.get("/token")
def generaToken():
    Token = jwt.encode({"usuario": "admin"}, token,algorithm="HS256") # --> genera y cifra el token basandose de la llave
    return {"token": Token}

@app.get("/ventas")
def obtenerVentas(authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas")   # --> obtiene las ventas de mi base de datos
    ventas= cursor.fetchall()
    logging.info("se obtuvo ventas del producto")
    return {"mensaje":ventas}

@app.post("/ventas")
def crearVentas(productoID: int,cantidad: int,authorization: str = Header()):
    verificaToken(authorization)
    global fallos,circuito_abierto,tiempo_apertura  # --> al traer de manera global esas variables me parmite modificarlas dentro de esta funcion
    if circuito_abierto:
        if time.time() - tiempo_apertura > 30:
            circuito_abierto = False                # --> el circuito esta cerrado y pasaron 30 seg de su apertura esta todo normal y vuelve a intentar
            fallos = 0
            logging.info("circuito cerrado, reintentando...")
        else:
            logging.error("circuito abierto, servicio no disponible")   # --> si el circuito esta abierto y no paso aun los 30 seg inhabilita el servicio y devuelve ell log con estado de codigo
            raise HTTPException(status_code=503, detail="servicio no disponible")
        
            
    for intentos in range(3):
        try:
            consultar = requests.get(
                f"http://127.0.0.1:8002/inventario/{productoID}",
                headers={"Authorization": f"Bearer {tokenInventario}"}) # --> hace una request a inventario si todo esta bien y el estado es 200 corta el ciclo de intentos 
            if consultar.status_code == 200:
                break
        except:
            logging.warning(f"intento { intentos + 1} fallido, reitentando...") # --> en caso de que no haya respuesta sigue intentando
            time.sleep(1)
    else:
        fallos +=1
        if fallos >= 3:
            circuito_abierto = True         # evalua las fallas si ya alcanzo las 3, abre el circuito por demasiadas fallas
            tiempo_apertura = time.time()
            logging.error("circuito abierto por demasiados fallos")

        logging.error(f"producto no encontrado despues de 3 intentos - id: {productoID}") # --> log y estado de codigo en caso de no encontrar producto
        raise HTTPException(status_code=402,detail="producto no encontrado")

    
    producto = consultar.json()["producto"] # --> consulta a inventario en la tabla productos
    precio = producto[2] # --> devuelve el precio del producto 

    total = cantidad * precio # --> se multiplica

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ventas (producto_id,cantidad,total) VALUES (%s,%s,%s)",
        (productoID,cantidad,total)                                          # --> y se inserta el resultado dentro de la tabla de ventas 
    )
    conn.commit()
    logging.info(f"se inserto venta correctamente - id: {productoID}") # --> log y estado de codigo 
    return {"mensaje": "productos agregado correctamente"}