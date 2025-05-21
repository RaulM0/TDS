import customtkinter as ctk
from tkinter import messagebox
from clubs import ClubManagementWindow

class Menu:
    def __init__(self, root, app_manager, usuario):
        self.root = root
        self.app = app_manager
        self.usuario = usuario
        self.club_window = None  # Referencia para la ventana de clubs
        
        # Configurar el contenedor principal
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_top_bar()
        self._create_menu_buttons()
    
    def _create_top_bar(self):
        """Crea la barra superior con información de usuario"""
        top_frame = ctk.CTkFrame(
            self.main_frame,
            height=60,
            fg_color=("#3a7ebf", "#1f538d"),
            corner_radius=10
        )
        top_frame.pack(fill="x", pady=(0, 20))
        top_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            top_frame,
            text="CLUB MANAGER",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)
        
        user_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        user_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.usuario.upper()}",
            font=ctk.CTkFont(size=14),
            text_color="white"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            user_frame,
            text="Cerrar Sesión",
            command=self.logout,
            width=100,
            height=30,
            fg_color=("#ff6b6b", "#d63031"),
            hover_color=("#ff5252", "#c0392b"),
            text_color="white"
        ).pack(side="left")
    
    def _create_menu_buttons(self):
        """Crea los botones grandes del menú principal"""
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(fill="both", expand=True)
        
        button_config = [
            {"text": "GESTIÓN DE CLUBS", "command": self.open_clubs_window},
            {"text": "GESTIÓN DE MIEMBROS", "command": self.open_members_window},
            {"text": "GESTIÓN DE MEMBRESÍAS", "command": self.open_subscriptions_window},
            {"text": "GESTON DE PAGOS", "command": self.open_pagos_window},
            {"text": "GESTION DE USUARIOS", "command": self.open_usuarios_window},
            {"text": "HISTORIAL ACADEMICO ", "command": self.open_historial_window},
            {"text": "CURSOS", "command": self.open_cursos_window}
        ]
        
        for config in button_config:
            btn = ctk.CTkButton(
                buttons_frame,
                text=config["text"],
                command=config["command"],
                height=70,
                corner_radius=10,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=("#f8f9fa", "#2b2b2b"),
                hover_color=("#e9ecef", "#343a40"),
                border_width=1,
                border_color=("#dee2e6", "#495057")
            )
            btn.pack(fill="both", expand=True, pady=10, padx=50)

# Método para abrir la ventana de gestión de clubs
    def open_clubs_window(self):
        """Abre la ventana de gestión de clubs"""
        if hasattr(self.app, 'club_management'):
            self.app._clear_window()
        self.app.show_club_management()
        self.app.root.update_idletasks()

# Método para abrir la ventana de gestión de usuarios
    def open_usuarios_window(self):
        """Abre la ventana de gestión de usuarios"""
        if hasattr(self.app, 'usuarios'):
            self.app._clear_window()
        self.app.show_users_management()
        self.app.root.update_idletasks()
       
    
# Método para abrir la ventana de gestión de miembros
    def open_members_window(self):
        """Abre la ventana de gestión de miembros"""
        if hasattr(self.app, 'miembros'):
            self.app._clear_window()
        self.app.show_members_management()
        self.app.root.update_idletasks()
        
# Método para abrir la ventana de gestión de membresías
    def open_subscriptions_window(self):
        """Abre la ventana de membresías"""
        if hasattr(self.app, 'membresias'):
            self.app._clear_window()
        self.app.show_membresias_management()
        self.app.root.update_idletasks()
    
# Método para abrir la ventana de gestión de pagos
    def open_pagos_window(self):
        """Abre la ventana de pagos"""
        if hasattr(self.app, 'pagos'):
            self.app._clear_window()
        self.app.show_pagos_management()
        self.app.root.update_idletasks()

# Método para abrir la ventana de gestión de cursos
    def open_cursos_window(self):
        """Abre la ventana de gestión de cursos"""
        if hasattr(self.app, 'cursos'):
            self.app._clear_window()
        self.app.show_cursos_management()
        self.app.root.update_idletasks()

    def open_historial_window(self):
        """Abre la ventana de historial académico"""
        if hasattr(self.app, 'historial'):
            self.app._clear_window()
        self.app.show_historial_academico()
        self.app.root.update_idletasks()
    
    def show_menu(self):
        """Muestra nuevamente el menú principal"""
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def logout(self):
        """Cierra la sesión actual"""
        if messagebox.askyesno(
            "Cerrar Sesión", 
            f"¿Estás seguro de cerrar sesión, {self.usuario}?"
        ):
            self.main_frame.pack_forget()
            self.app.show_login()

            