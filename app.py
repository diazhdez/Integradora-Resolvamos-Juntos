from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
from tkinter import *
from tkinter import messagebox as MessageBox
import conexion as db
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'Resolvamos_Juntos_BD',
}

# Configurar la aplicacion para ser ejecutado
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__)
app.secret_key = 'M0i1Xc$GfPw3Yz@2SbQ9lKpA5rJhDtE7'

@app.route('/', methods=['GET'])
def home():
    insertObjeto = []
    if 'logueado' in session and session['logueado']:
            
        return render_template('index.html', datos=insertObjeto)
    else:
        return redirect('/login')
    
####registro e inicio de sesion###
@app.route('/login', methods=["GET","POST"])
def login():
   if request.method == 'POST':
        correo = request.form.get('txtcorreo')
        contraseña = request.form.get('txtcontraseña')

        # Aquí asumimos que "connection" es un objeto de conexión MySQL ya configurado
        cursor = db.conexion.cursor()
        cursor.execute("SELECT * FROM users WHERE correo = %s AND contraseña = %s", (correo, contraseña))
        account = cursor.fetchone()
        cursor.close()

        if account:
            session['logueado'] = True
            session['id_rol'] = account[5]

            if session['id_rol'] == 1:
                return redirect(url_for('administrador'))
            else:
                return redirect('/')
        else:
            # Si no se encuentra la cuenta, muestra el mensaje como un modal
            mensaje = "Correo o Contraseña erronea"
            tipo_mensaje = "error"
            return render_template("login.html", mensaje=mensaje, tipo_mensaje=tipo_mensaje)
   return render_template("login.html")

@app.route('/registro', methods=['POST'])
def registro():
    # importamos las variables desde el form del index.htlm
    nombre = request.form["nombre"]
    apellidos = request.form["apellidos"]
    correo = request.form["correo"]
    contraseña = request.form["contraseña"]
    if nombre and apellidos and correo and contraseña:
        cursor = db.conexion.cursor()
        # Verificar si el correo electrónico ya existe en la base de datos
        sql_verificar_correo = "SELECT COUNT(*) FROM users WHERE correo = %s"
        cursor.execute(sql_verificar_correo, (correo,))
        num_registros = cursor.fetchone()[0]

    if num_registros > 0:
        mensaje = "Correo ya en uso"
        tipo_mensaje = "error"
        return redirect(url_for("login", mensajeError=mensaje, tipo_mensaje=tipo_mensaje))
    else:
        sql = """INSERT INTO users (nombre, apellidos, correo, contraseña) values (%s, %s, %s, %s)"""
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (nombre, apellidos, correo, contraseña)
    cursor.execute(sql, datos)
    mensaje = "Registro hecho de manera exitosa"
    tipo_mensaje = "exito"
    db.conexion.commit()
    return redirect(url_for("login", mensaje=mensaje, tipo_mensaje=tipo_mensaje))

@app.route('/logout')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect('/login') # Redirige al inicio de sesión

@app.route('/recuperar-cuenta')
def recuperar():
    return render_template('recuperar.html')


@app.route('/reestablecer')
def reestablecer():
    return render_template('reestablecer.html')


# @app.route('/inicio/')
# def inicio():
#     return render_template('index.html')


@app.route('/administrador')
def administrador():
    return render_template('administrador.html')


@app.route('/quejas/')
def quejas():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT * FROM quejas")
    datosDB = cursor.fetchall()
    # Convertir los datos a diccionario
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        insertObjeto.append(dict(zip(columnName, registro)))
    cursor.close()
    return render_template('quejas.html', data=insertObjeto)

# Crear  la ruta para insertar los registros en la BD
@app.route('/insertQueja', methods=['POST'])
def insertQueja():
    # Importamos las variables desde el form de index.html
    alumno = request.form["alumnoNombre"]
    apellidos = request.form["alumnoApellidos"]
    piso = request.form["pisoNumero"]
    aula = request.form["aulaNumero"]
    tipo = request.form["quejaTipo"]
    detalle = request.form["quejaDetalle"]
    evidencia = request.form["quejaEvidencia"]

    if tipo and alumno:
        cursor = db.conexion.cursor()
        sql = """INSERT INTO quejas (alumnoNombre, alumnoApellidos, pisoNumero, aulaNumero, quejaTipo, quejaDetalle, quejaEvidencia)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        # Declaramos a "datos" como una variable tipo tupla para mandar la informacion
        datos = (alumno, apellidos, piso, aula, tipo, detalle, evidencia)
        cursor.execute(sql, datos)
        db.conexion.commit()
    else:
        pass
    return redirect(url_for('quejas'))

# Crear  la ruta para que el usuario vea el seguimiento de sus quejas
@app.route('/estado-de-queja/', methods=['GET', 'POST'])
def estado_queja():
    if request.method == 'POST':
        folio = request.form['folio']
        cursor = db.conexion.cursor()
        cursor.execute("SELECT nombre, Causa_reporte, Estatus_queja FROM Folio_quejas WHERE Id_Folio = %s", (folio,))
        queja = cursor.fetchone()
        if queja:
            nombre, causa_reporte, estatus_queja = queja
            etapas = ["Pendiente", "En proceso", "Resuelto"]

            return render_template('estado_queja.html', estado_queja=estatus_queja, nombre=nombre, causa_reporte=causa_reporte, etapas=etapas)
        else:
            mensaje_error = "Folio no encontrado"
            return render_template('estado_queja.html', mensaje_error=mensaje_error)
    return render_template('estado_queja.html')


@app.route('/bandeja/')
def bandeja():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT * FROM quejas")  # ORDER BY quejaID DESC
    datosDB = cursor.fetchall()
    total = cursor.rowcount
    # Convertir los datos a diccionario
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        insertObjeto.append(dict(zip(columnName, registro)))
    cursor.close()
    return render_template('bandeja.html', data=insertObjeto, dataTotal=total)

# Crear la ruta para Eliminar registros de la BD
@app.route('/eliminaQueja/<string:id>')
def eliminaQueja(id):
    resultado = MessageBox.askokcancel(
        "Caso solucionado...", "¿Estas seguro de eliminar el registro?")
    if resultado == True:
        cursor = db.conexion.cursor()
        sql = """DELETE FROM quejas WHERE quejaID=%s"""
        # Declaramos a "datos" como una variable tipo tupla para mandar la informacion
        datos = (id,)
        cursor.execute(sql, datos)
        db.conexion.commit()
    else:
        pass
    return redirect(url_for('bandeja'))

# Crear la ruta para la grafica
@app.route('/grafica/')
def grafica():
    return render_template('grafica.html')

# Ruta para obtener los datos de la tabla 'inconvenientes' y enviarlos como JSON
@app.route('/datos_inconvenientes')
def obtener_datos_inconvenientes():
    try:
        # Realiza la conexión a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Consulta para obtener los datos de la tabla 'inconvenientes'
        query = "SELECT tipo, cantidad FROM inconvenientes"
        cursor.execute(query)

        # Obtén los resultados de la consulta
        datos = cursor.fetchall()

        # Cierra la conexión a la base de datos
        cursor.close()
        connection.close()

        # Retorna los datos como un JSON
        return jsonify(datos)
    except Exception as e:
        # Si ocurre algún error, muestra el mensaje de error
        print('Error al obtener datos:', e)
        return jsonify([])

def status_401(error):
    return redirect(url_for('login'))

def pagina_no_encontrada(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True)
