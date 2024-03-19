import mysql.connector
from mysql.connector import Error

# try:
conexion = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='12345',
    database='Resolvamos_Juntos_BD'
)


#     if conexion.is_connected():
#         print('Conexión Exitosa')
#         InfoServer = conexion.get_server_info()
#         print('Información del servidor:', InfoServer)
#         cursor = conexion.cursor()
#         cursor.execute("SELECT database();")
#         database = cursor.fetchone()
#         print('Conectado a la base de datos: {}'.format(database))


# except Error as ex:
#     print("Error durante la conexión:", ex)

# finally:
#     if conexion.is_connected():
#         conexion.close()
#         print('La conexión ha finalizado')
