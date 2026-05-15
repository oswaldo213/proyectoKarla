from flask import Flask, request, jsonify
import mariadb
from datetime import datetime
from flask import render_template

app = Flask(__name__)
def get_db():
    return mariadb.connect(
        host="localhost",
        user="root",
        password="Ce1574528390",
        database="Prueba"
    )




id_usuario_actual = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/accesos")
def api_accesos():
    db = get_db();
    cursor = db.cursor()
    cursor.execute("""
        SELECT U.Nombre, U.Apellido, U.Rol, P.Fecha, P.Hora 
        FROM Peticion P
        LEFT JOIN Usuarios U 
        ON P.Identificador = U.Identificador
        ORDER BY P.Fecha DESC, P.Hora DESC
        LIMIT 5
    """)
    accesos = cursor.fetchall()
    datos = []
    for acceso in accesos:
        datos.append(({
            "nombre": acceso[0],
            "apellido": acceso[1],
            "rol": acceso[2],
            "fecha": str(acceso[3]),
            "hora": str(acceso[4])
        }))
    db.close()
    return jsonify(datos)


@app.route("/api/Prestamos")
def api_prestamos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            SELECT 
                e.Nombre AS Equipo,
                u.Nombre AS Usuario,
                pd.Fecha,
                pd.Hora
            FROM Prestamo p
            LEFT JOIN Equipo e ON p.Id_equipo = e.Id_equipo
            LEFT JOIN Usuarios u ON p.Id_usuario = u.Id_usuario
            LEFT JOIN Prestamos_Detalles pd ON p.Id_prestamo = pd.Id_prestamo
    """)
    prestamos = cursor.fetchall()
    datos = []
    for prestamo in prestamos:
        datos.append(({
            "nombre": prestamo[0],
            "usuario": prestamo[1],
            "fecha": str(prestamo[2]),
            "hora": str(prestamo[3])
        }))     
    db.close()
    return jsonify(datos)
    
@app.route("/api/Denegadas")
def api_Denegadas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            SELECT P.Identificador, P.Fecha, P.Hora FROM Peticiones_negadas P
            ORDER BY P.Fecha DESC, P.Hora DESC
            LIMIT 5
    """)
    negaciones = cursor.fetchall()
    datos = []
    for negacion in negaciones:
        datos.append(({
            "identificador": negacion[0],
            "fecha": str(negacion[1]),
            "hora": str(negacion[2])
        }))     
    db.close()
    return jsonify(datos)
    







@app.route("/identificar", methods=["POST"])
def identificar():
    db = get_db()
    cursor = db.cursor()
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
        cursor.execute("INSERT INTO Prestamo (Id_usuario, Id_equipo, Fecha, Hora) VALUES (?,?,?,?)",
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
    db.close()
    return jsonify({"acceso": "denegado"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)