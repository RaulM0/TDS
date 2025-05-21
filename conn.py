import mysql.connector


def get_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",      # reemplaza con tu usuario
            password="2403",  # reemplaza con tu contraseña
            database="gestion_clubes"
        )