import mariadb
import serial
from datetime import datetime

db = mariadb.connect(
    host="localhost",
    user="root",
    password="Ce1574528390",
    database="Prueba"
)
cursor = db.cursor()

puerto = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
print("Escuchando puerto serial...")

id_usuario_actual = None

while True:
    linea = puerto.readline().decode("utf-8").strip()
    if not linea:
        continue

    print("Recibido:", linea)
    partes = linea.split("|")

    if partes[0] != "UID":
        continue

    uid = partes[1]

    cursor.execute("SELECT Id_usuario, Nombre, Apellido, Rol FROM Usuarios WHERE Identificador=?", (uid,))
    usuario = cursor.fetchone()


    if usuario:

        ahora = datetime.now()
        cursor.execute("INSERT INTO Peticion (Identificador,Fecha,Hora) VALUES (?,?,?)",
            (uid, ahora.date(),ahora.time())
        )
        db.commit()

        id_usuario_actual = usuario[0]
        nombre = usuario[1] + " " + usuario[2]
        rol = usuario[3]
        print(f"Usuario: {nombre} | Rol: {rol}")
        continue

    cursor.execute("SELECT Id_equipo, Nombre FROM Equipo WHERE Identificador=?", (uid,))
    equipo = cursor.fetchone()

    if equipo and id_usuario_actual:
        id_equipo = equipo[0]
        nombre_equipo = equipo[1]

        cursor.execute(
            "INSERT INTO Prestamo (Id_usuario, Id_equipo) VALUES (?,?)",
            (id_usuario_actual, id_equipo)
        )
        db.commit()
        id_prestamo = cursor.lastrowid

        ahora = datetime.now()
        cursor.execute(
            "INSERT INTO Prestamos_Detalles (Id_prestamo, Id_equipo, Fecha, Hora) VALUES (?,?,?,?)",
            (id_prestamo, id_equipo, ahora.date(), ahora.time())
        )
        db.commit()
        print(f"Prestamo registrado: {nombre_equipo}")
        id_usuario_actual = None

    else:
        print(f"Acceso denegado: {uid}")
        ahora = datetime.now()
        cursor.execute("INSERT INTO Peticiones_negadas (Identificador,Fecha,Hora) VALUES (?,?,?)",
            (uid, ahora.date(),ahora.time())
        )
        db.commit()