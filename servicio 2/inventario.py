from fastapi import FastAPI,HTTPException,Header
from jose import jwt
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO,  # --> livel de log que voy a estar usando
    format="%(asctime)s - %(levelname)s - %(message)s"  # --> el formato en el que se va a ver mi log
)

app = FastAPI() # --> creacion del framework con motor fastAPI

token = "dan321" # --> llave o clave secreta para mi servicio

conn = psycopg2.connect(
    host="localhost",
    database="inventarioDB",  # --> conexion con mi base de datos
    user="postgres",
    password="dan"
)
# verifica el token 
def verificaToken(authorization: str = Header()):
    try:
        clave = authorization.split(" ")[1] # --> divide el token con espacio y accede al segundo valor (token) con [1]
        jwt.decode(clave,token,algorithms=["HS256"]) # --> verifica la firma y si no es correcta jwt.decode la rechaza
    except:
        logging.error("token invalido - acceso denegado")
        raise HTTPException(status_code=401, detail="token invalido") # --> log y estado de codigo 


@app.get("/token")
def generarToken():
    Token = jwt.encode({"token": "admin"},token,algorithm="HS256") # crea el token basandose en mi clave y le da una firma o la "cifra"
    return {"token": Token}

@app.get("/inventario")
def obtenerProductos(authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")   # --> obtiene los productos de mi base de datos inventario
    productos = cursor.fetchall()
    logging.info("se obtuvo los datos de productos")
    return {"productos": productos}

@app.get("/inventario/{id}")
def obtenerProductoid(id: int,authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()                      # --> obtiene productos de la bse de datos inventario pero por su id
    cursor.execute(
        "SELECT * FROM productos WHERE id = %s ",
        (id,)
    )
    producto = cursor.fetchone()
    
    if producto is None:
        logging.info(f"producto no encontrado - id: {id}")
        raise HTTPException(status_code=402, detail="producto no encontrado") # --> log y estado de codigo de la peticion 
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
        (nombre,precio,stock)                                      # --> envia o inserta esos productos en mi base de datos
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
    cursor = conn.cursor()              # --> actualiza los productos basandose por su id 
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
    cursor = conn.cursor()        # --> elimina ese producto de la base de datos inventario
    cursor.execute(
        "DELETE FROM productos " \
        "WHERE id = %s",
        (id,)
    )
    conn.commit()
    logging.info("se elimino producto correctamente")
    return {"mensaje": "producto eliminado correctamente"}

 