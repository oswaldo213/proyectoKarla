from flask import Flask, request, jsonify
import mariadb
from datetime import datetime
from flask import render_template

app = Flask(__name__)

db = mariadb.connect(
    host="localhost",
    user="root",
    password="Ce1574528390",
    database="Prueba"
)

cursor = db.cursor()


@app.route("/")
def index():
    cursor.execute("""
        SELECT U.Nombre, U.Apellido, U.Rol, P.Fecha, P.Hora 
        FROM Peticion P
        LEFT JOIN Usuarios U ON P.Identificador = U.Identificador
        ORDER BY P.Fecha DESC, P.Hora DESC
        LIMIT 10
    """)
    accesos = cursor.fetchall()

    cursor.execute("""
        SELECT E.Nombre, U.Nombre, U.Apellido, PD.Fecha, PD.Hora
        FROM Prestamos_Detalles PD
        LEFT JOIN Equipo E ON PD.Id_equipo = E.Id_equipo
        LEFT JOIN Prestamo PR ON PD.Id_prestamo = PR.Id_Prestamo
        LEFT JOIN Usuarios U ON PR.Id_usuario = U.Id_usuario
        ORDER BY PD.Fecha DESC, PD.Hora DESC
        LIMIT 10
    """)
    prestamos = cursor.fetchall()

    cursor.execute("""
        SELECT Identificador, Fecha, Hora 
        FROM Peticiones_negadas
        ORDER BY Fecha DESC, Hora DESC
        LIMIT 10
    """)
    denegados = cursor.fetchall()

    return render_template("index.html", accesos=accesos, prestamos=prestamos, denegados=denegados)


id_usuario_actual = None

@app.route("/identificar", methods=["POST"])
def identificar():
    global id_usuario_actual
    datos = request.json
    uid = datos.get("uid")

    cursor.execute("SELECT Id_usuario, Nombre, Apellido, Rol FROM Usuarios WHERE Identificador=?", (uid,))
    usuario = cursor.fetchone()

    if usuario:
        id_usuario_actual = usuario[0]
        ahora = datetime.now()
        cursor.execute("INSERT INTO Peticion (Identificador, Fecha, Hora) VALUES (?,?,?)",
            (uid, ahora.date(), ahora.time())
        )
        db.commit()
        return jsonify({
            "acceso": "permitido",
            "nombre": usuario[1] + " " + usuario[2],
            "rol": usuario[3]
        })

    cursor.execute("SELECT Id_equipo, Nombre FROM Equipo WHERE Identificador=?", (uid,))
    equipo = cursor.fetchone()

    if equipo and id_usuario_actual:
        cursor.execute("INSERT INTO Prestamo (Id_usuario, Id_equipo) VALUES (?,?)",
            (id_usuario_actual, equipo[0])
        )
        db.commit()
        id_prestamo = cursor.lastrowid
        ahora = datetime.now()
        cursor.execute("INSERT INTO Prestamos_Detalles (Id_prestamo, Id_equipo, Fecha, Hora) VALUES (?,?,?,?)",
            (id_prestamo, equipo[0], ahora.date(), ahora.time())
        )
        db.commit()
        id_usuario_actual = None
        return jsonify({
            "acceso": "equipo",
            "nombre": equipo[1]
        })

    ahora = datetime.now()
    cursor.execute("INSERT INTO Peticiones_negadas (Identificador, Fecha, Hora) VALUES (?,?,?)",
        (uid, ahora.date(), ahora.time())
    )
    db.commit()
    return jsonify({"acceso": "denegado"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)