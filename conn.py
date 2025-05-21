import mysql.connector


def get_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",      # reemplaza con tu usuario
            password="",  # reemplaza con tu contraseña
            database="tds"
        )