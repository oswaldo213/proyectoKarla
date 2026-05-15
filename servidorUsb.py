import threading
import serial
import mariadb
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE   = 115200

puerto_serial = None 
id_usuario_actual = None
estado_lock = threading.Lock()

def get_db():
    return mariadb.connect(
        host="localhost",
        user="root",
        password="Ce1574528390",
        database="Prueba"
    )

def responder(codigo, mensaje=""):
    if puerto_serial and puerto_serial.is_open:
        linea = f"RESP|{codigo}|{mensaje}\n"
        puerto_serial.write(linea.encode("utf-8"))
        print("→ ESP32:", linea.strip())

def hilo_serial():
    global id_usuario_actual, puerto_serial
    try:
        puerto_serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Serial abierto en {SERIAL_PORT}")
    except Exception as e:
        print(f"Error abriendo serial: {e}")
        return

    while True:
        try:
            linea = puerto_serial.readline().decode("utf-8").strip()
        except Exception as e:
            print("Error leyendo serial:", e)
            continue

        if not linea:
            continue

        print("← ESP32:", linea)
        partes = linea.split("|")
        if partes[0] != "UID" or len(partes) < 2:
            continue

        uid = partes[1]
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT Id_usuario, Nombre, Apellido, Rol FROM Usuarios WHERE Identificador=?",
            (uid,)
        )
        usuario = cursor.fetchone()

        if usuario:
            ahora = datetime.now()
            cursor.execute(
                "INSERT INTO Peticion (Identificador, Fecha, Hora) VALUES (?,?,?)",
                (uid, ahora.date(), ahora.time())
            )
            db.commit()
            nombre = usuario[1] + " " + usuario[2]
            with estado_lock:
                id_usuario_actual = usuario[0]
            print(f"Usuario: {nombre} | Rol: {usuario[3]}")
            responder("USUARIO", nombre)
            db.close()
            continue

        cursor.execute(
            "SELECT Id_equipo, Nombre FROM Equipo WHERE Identificador=?",
            (uid,)
        )
        equipo = cursor.fetchone()

        with estado_lock:
            uid_usuario = id_usuario_actual

        if equipo and uid_usuario:
            id_equipo = equipo[0]
            nombre_equipo = equipo[1]
            cursor.execute(
                "INSERT INTO Prestamo (Id_usuario, Id_equipo) VALUES (?,?)",
                (uid_usuario, id_equipo)
            )
            db.commit()
            id_prestamo = cursor.lastrowid
            ahora = datetime.now()
            cursor.execute(
                "INSERT INTO Prestamos_Detalles (Id_prestamo, Id_equipo, Fecha, Hora) VALUES (?,?,?,?)",
                (id_prestamo, id_equipo, ahora.date(), ahora.time())
            )
            db.commit()
            with estado_lock:
                id_usuario_actual = None
            print(f"Préstamo registrado: {nombre_equipo}")
            responder("OK", nombre_equipo)
        else:
            ahora = datetime.now()
            cursor.execute(
                "INSERT INTO Peticiones_negadas (Identificador, Fecha, Hora) VALUES (?,?,?)",
                (uid, ahora.date(), ahora.time())
            )
            db.commit()
            print(f"Acceso denegado: {uid}")
            responder("DENEGADO", uid)

        db.close()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/accesos")
def api_accesos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT U.Nombre, U.Apellido, U.Rol, P.Fecha, P.Hora 
        FROM Peticion P
        LEFT JOIN Usuarios U ON P.Identificador = U.Identificador
        ORDER BY P.Fecha DESC, P.Hora DESC
        LIMIT 5
    """)
    datos = [
        {"nombre": r[0], "apellido": r[1], "rol": r[2],
         "fecha": str(r[3]), "hora": str(r[4])}
        for r in cursor.fetchall()
    ]
    db.close()
    return jsonify(datos)

@app.route("/api/Prestamos")
def api_prestamos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.Nombre, u.Nombre, pd.Fecha, pd.Hora
        FROM Prestamo p
        LEFT JOIN Equipo e ON p.Id_equipo = e.Id_equipo
        LEFT JOIN Usuarios u ON p.Id_usuario = u.Id_usuario
        LEFT JOIN Prestamos_Detalles pd ON p.Id_prestamo = pd.Id_prestamo
    """)
    datos = [
        {"nombre": r[0], "usuario": r[1],
         "fecha": str(r[2]), "hora": str(r[3])}
        for r in cursor.fetchall()
    ]
    db.close()
    return jsonify(datos)

@app.route("/api/Denegadas")
def api_denegadas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT Identificador, Fecha, Hora FROM Peticiones_negadas
        ORDER BY Fecha DESC, Hora DESC LIMIT 5
    """)
    datos = [
        {"identificador": r[0], "fecha": str(r[1]), "hora": str(r[2])}
        for r in cursor.fetchall()
    ]
    db.close()
    return jsonify(datos)

@app.route("/api/estado")
def api_estado():
    with estado_lock:
        uid = id_usuario_actual
    return jsonify({
        "serial_conectado": puerto_serial is not None and puerto_serial.is_open,
        "usuario_pendiente": uid is not None
    })

# ── Arranque ───────────────────────────────────────────────────
if __name__ == "__main__":
    t = threading.Thread(target=hilo_serial, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False)