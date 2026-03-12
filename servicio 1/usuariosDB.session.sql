CREATE TABLE IF NOT EXISTS usuarios(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR (100),
    email VARCHAR (100)
)

SELECT * FROM usuarios