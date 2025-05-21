from tkinter import messagebox
import customtkinter as ctk
from clubs import ClubManagementWindow
from cursos import CourseManagementWindow
from historial_academico import AcademicHistoryWindow
from login import LoginApp
from menuAdmin import Menu
from miembros import MemberManagementWindow
from membresias import MembershipManagementWindow
from pagos import PaymentManagementWindow
from usuario import UserManagementWindow

class AppManager:
    def __init__(self):
        # Configuración inicial de la ventana principal
        self.root = ctk.CTk()
        self._configure_main_window()
        self._setup_ui_styles()
        self.current_user = None  # Almacena el usuario actual
        self.show_login()

    def _configure_main_window(self):
        """Configura los parámetros de la ventana principal"""
        self.root.title("Club Manager")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

    def _setup_ui_styles(self):
        """Establece estilos visuales usando temas integrados"""
        ctk.set_appearance_mode("System")  # "Light", "Dark" o "System"
        
        # Usamos un tema integrado en lugar de archivo externo
        ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"
        
        # Fuentes personalizadas (usando fuentes del sistema)
        self.font_title = ctk.CTkFont(family="Arial", size=24, weight="bold")
        self.font_normal = ctk.CTkFont(family="Arial", size=12)

    def show_login(self):
        """Muestra la pantalla de login"""
        self._clear_window()
        self.current_user = None  # Resetear usuario al volver al login
        LoginApp(self.root, self)

    def show_menu(self, usuario):
        """Muestra el menú principal"""
        self._clear_window()
        self.current_user = usuario  # Almacenar usuario actual
        self._configure_menu_window()
        Menu(self.root, self, usuario)  # This is correct - root, app_manager, usuario

    def show_club_management(self):
        """Muestra la ventana de gestión de clubes"""
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.club_management = ClubManagementWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )

# metodo para mostrar la ventana de gestión de miembros
    def show_members_management(self):
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.miembros_management = MemberManagementWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )

# metodo para mostrar la ventana de gestión de membresias

    def show_membresias_management(self):
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.membresias = MembershipManagementWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )

# metodo para mostrar la ventana de gestión de pagos
    def show_pagos_management(self):
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.pagos = PaymentManagementWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )

# metodo para mostrar la ventana de gestión de cursos
    def show_users_management(self):
        """Muestra la ventana de gestión de usuarios"""
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.usuarios = UserManagementWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )

# metodo para mostrar la ventana de gestión de cursos
    def show_historial_academico(self):
        """Muestra la ventana de historial académico"""
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.historial = AcademicHistoryWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )

# metodo para mostrar la ventana de gestión de cursos
    def show_cursos_management(self):
        """Muestra la ventana de gestión de cursos"""
        self._clear_window()
        
        # Crear frame contenedor
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instanciar la ventana de gestión dentro del contenedor
        self.cursos = CourseManagementWindow(
            root=container,  # Pasamos el frame como contenedor
            app_manager=self
        )
        

    def _configure_menu_window(self):
        """Configura la ventana para el menú principal"""
        self.root.geometry("1200x800")
        self.root.minsize(1400, 700)
        
        # Barra de estado (solo en el menú principal)
        self.status_bar = ctk.CTkLabel(
            self.root, 
            text=f"Usuario: {self.current_user} | Sistema Club Manager v1.0",
            anchor="w",
            font=self.font_normal,
            text_color=("#6c757d", "#adb5bd")
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

    def _clear_window(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Inicia el bucle principal de la aplicación"""
        self.root.mainloop()

    def open_clubs_window(self):
        """Abre la ventana de gestión de clubes"""
        

if __name__ == "__main__":
    try:
        app = AppManager()
        app.run()
    except Exception as e:
        ctk.CTk().withdraw()  # Ventana temporal para mostrar el error
        messagebox.showerror(
            "Error Inesperado", 
            f"No se pudo iniciar la aplicación:\n\n{str(e)}"
        )