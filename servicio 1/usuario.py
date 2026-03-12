from fastapi import FastAPI,HTTPException,Header
from jose import jwt
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

token = "dan123"

conn = psycopg2.connect(
    host="localhost",
    database="usuariosDB",
    user="postgres",
    password="dan"
)

def verificaToken(authorization: str = Header()):
    try:
        clave = authorization.split(" ")[1]
        jwt.decode(clave,token,algorithms=["HS256"])
    except:
        logging.error("token invalido - acceso denegado")
        raise HTTPException(status_code=401, detail="TOKEN INVALIDO")
    
@app.get("/token")
def generaToken():
    Token = jwt.encode({"usuario": "admin"}, token, algorithm="HS256")
    return {"token": Token}
    
@app.get("/usuarios")
def obtenerUsuarios(authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    logging.info("se obtuvo la lista de usuarios")
    return {"usuarios": usuarios}

@app.post("/usuarios")
def crearUsuarios(nombre: str, email: str, authorization: str = Header()):
    verificaToken(authorization)
    cursor = conn.cursor()
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
        (nombre,email,id)
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
        (id,)
    )
    conn.commit()
    logging.info(f"Usuario eliminado - id: {id}")
    return {"mensaje": "usuario eliminado exitosamente"}