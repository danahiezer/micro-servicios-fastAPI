from fastapi import FastAPI,HTTPException,Header
from jose import jwt
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO, # --> es el nivel de log que utilice 
    format="%(asctime)s - %(levelname)s - %(message)s" # --> es el formato para ese log
)

app = FastAPI()  # --> la creacion de el servidor web (app)

token = "dan123" # --> llave o clave secreta que mi servidor reconoce

conn = psycopg2.connect(
    host="localhost",
    database="usuariosDB", # --> conexion con mi base de datos
    user="postgres",
    password="dan"
)
# verifica el token
def verificaToken(authorization: str = Header()): 
    try:
        clave = authorization.split(" ")[1] # --> debide el token en una lista usando espacios y el [1] es el segundo elemento (token)
        jwt.decode(clave,token,algorithms=["HS256"]) # --> verifica que coincida la firma y si no jwt.decode lo rechaza
    except:
        logging.error("token invalido - acceso denegado")
        raise HTTPException(status_code=401, detail="TOKEN INVALIDO") # --> en caso de tokens invalidos se lanzan un log y tipo de estado 

@app.get("/token")
def generaToken():
    Token = jwt.encode({"usuario": "admin"}, token, algorithm="HS256") # --> genera el token tomando la llave o clave secreta y genera un jwt firmado o "cifrado"
    return {"token": Token}

@app.get("/usuarios")
def obtenerUsuarios(authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")         # --> obtiene usuarios de mi base de datos
    usuarios = cursor.fetchall()
    logging.info("se obtuvo la lista de usuarios")
    return {"usuarios": usuarios}

@app.post("/usuarios")
def crearUsuarios(nombre: str, email: str, authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()                                         # --> que envia o inserta usuarios en mi base de datos (nombre y email)
    cursor.execute(
        "INSERT INTO usuarios (nombre,email) VALUES (%s,%s)",
        (nombre,email)
    )
    conn.commit()
    logging.info("usuario creado exitosamente")
    return {"mensaje": "usuario creado exitosamente"}

@app.put("/usuarios/{id}")
def actualizarUsuario(id: int, nombre: str, email: str, authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios " \
        "SET nombre = %s, email = %s " \
        "WHERE id = (%s)",
        (nombre,email,id)                             # --> actualiza los datos del usuario por medio de su id
    )

    conn.commit()
    logging.info(f"Usuario actualizado - id: {id}")
    return {"mensaje": "usuario actualizado exitosamente"}

@app.delete("/usuarios/{id}")
def eliminarUsuario(id: int, authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM usuarios WHERE id = %s",
        (id,)                                                 # --> elimina al usuario de mi base de datos
    )
    conn.commit()
    logging.info(f"Usuario eliminado - id: {id}")
    return {"mensaje": "usuario eliminado exitosamente"}