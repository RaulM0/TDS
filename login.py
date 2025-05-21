import customtkinter as ctk
from tkinter import messagebox
import os
from conn import get_connection

class LoginApp:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        
        # Configuración inicial de la aplicación
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # Frame principal del login con diseño mejorado
        self.frame_login = ctk.CTkFrame(
            self.root, 
            fg_color=("white", "#2b2b2b"),
            border_width=1,
            border_color=("#e0e0e0", "#444444"),
            corner_radius=12
        )
        self.frame_login.pack(expand=True, padx=20, pady=20)

        # Logo o imagen de la aplicación
        self.logo = ctk.CTkLabel(
            self.frame_login, 
            text="🏆 Club Manager", 
            font=ctk.CTkFont("Arial", 32, weight="bold"),
            text_color=("#3a7ebf", "#1f538d")
        )
        self.logo.pack(pady=(40, 20))

        # Subtítulo
        self.subtitulo = ctk.CTkLabel(
            self.frame_login, 
            text="Sistema de Gestión de Clubes", 
            font=ctk.CTkFont("Arial", 14),
            text_color=("#666", "#aaa")
        )
        self.subtitulo.pack(pady=(0, 40))

        # Contenedor de formulario
        self.form_frame = ctk.CTkFrame(
            self.frame_login, 
            fg_color="transparent"
        )
        self.form_frame.pack(fill="x", padx=100)

        # Campo de usuario con icono
        self.usuario_frame = ctk.CTkFrame(
            self.form_frame, 
            fg_color="transparent"
        )
        self.usuario_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.usuario_frame, 
            text="👤 Usuario",
            font=ctk.CTkFont(size=12),
            anchor="w"
        ).pack(fill="x")

        self.entrada_usuario = ctk.CTkEntry(
            self.usuario_frame, 
            placeholder_text="Ingrese su usuario",
            width=300,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.entrada_usuario.pack(fill="x", pady=(5, 0))

        # Campo de contraseña con icono
        self.clave_frame = ctk.CTkFrame(
            self.form_frame, 
            fg_color="transparent"
        )
        self.clave_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.clave_frame, 
            text="🔒 Contraseña",
            font=ctk.CTkFont(size=12),
            anchor="w"
        ).pack(fill="x")

        self.entrada_clave = ctk.CTkEntry(
            self.clave_frame, 
            placeholder_text="Ingrese su contraseña",
            show="•",
            width=300,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.entrada_clave.pack(fill="x", pady=(5, 0))

        # Checkbox para recordar usuario
        self.recordar = ctk.CTkCheckBox(
            self.form_frame,
            text="Recordar mi usuario",
            font=ctk.CTkFont(size=12)
        )
        self.recordar.pack(pady=(10, 0))

        # Botón de login con estilo moderno
        self.boton_login = ctk.CTkButton(
            self.form_frame, 
            text="Iniciar Sesión", 
            command=self.iniciar_sesion,
            width=300,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#3a7ebf", "#1f538d"),
            hover_color=("#2d6da3", "#184477")
        )
        self.boton_login.pack(pady=(20, 10))

        """
        # Enlace para recuperar contraseña
        self.recuperar_clave = ctk.CTkButton(
            self.form_frame,
            text="¿Olvidaste tu contraseña?",
            command=self.recuperar_contrasena,
            font=ctk.CTkFont(size=12, underline=True),
            fg_color="transparent",
            hover_color=("#f0f0f0", "#333333"),
            text_color=("#3a7ebf", "#5dade2"),
            width=0
        )
        self.recuperar_clave.pack()
        """
        

        # Separador
        ctk.CTkLabel(
            self.form_frame, 
            text="───── o ─────\n",
            font=ctk.CTkFont(size=12),
            text_color=("#aaa", "#666")
        ).pack(pady=20)

        # Botón de registro
        """
        self.boton_registro = ctk.CTkButton(
            self.form_frame, 
            text="Crear una cuenta nueva", 
            command=self.registrarse,
            width=300,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=1,
            border_color=("#3a7ebf", "#1f538d"),
            hover_color=("#e8f4fc", "#2a3b4a"),
            text_color=("#3a7ebf", "#5dade2")
        )
        self.boton_registro.pack(pady=(0, 30))
        """
        

        # Manejar la tecla Enter para iniciar sesión
        self.entrada_clave.bind("<Return>", lambda event: self.iniciar_sesion())

        # Cargar credenciales guardadas si existen
        self.cargar_credenciales()

    def cargar_credenciales(self):
        """Carga las credenciales recordadas si existen"""
        try:
            with open("credenciales.txt", "r") as f:
                usuario = f.readline().strip()
                if usuario:
                    self.entrada_usuario.insert(0, usuario)
                    self.recordar.select()
        except FileNotFoundError:
            pass

    def guardar_credenciales(self, usuario):
        """Guarda las credenciales si el usuario lo desea"""
        if self.recordar.get():
            with open("credenciales.txt", "w") as f:
                f.write(usuario)
        else:
            try:
                os.remove("credenciales.txt")
            except:
                pass

    def iniciar_sesion(self):
        """Maneja el proceso de inicio de sesión validando contra la base de datos"""
        usuario = self.entrada_usuario.get().strip()
        clave = self.entrada_clave.get().strip()

        if not usuario or not clave:
            messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos")
            return

        # Efecto visual de carga
        self.boton_login.configure(text="Validando...", state="disabled")
        self.root.update()

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Consulta para verificar credenciales
            query = """
                SELECT id_usuario, nombre_usuario, rol, estado 
                FROM usuarios 
                WHERE nombre_usuario = %s AND contrasena = %s
            """
            cursor.execute(query, (usuario, clave))
            user_data = cursor.fetchone()
            
            if user_data:
                # Verificar estado del usuario
                if user_data['estado'] != 'Activo':
                    messagebox.showerror(
                        "Cuenta no activa", 
                        f"Su cuenta está marcada como {user_data['estado']}.\n"
                        "Por favor contacte al administrador."
                    )
                    return
                
                # Actualizar último acceso
                update_query = """
                    UPDATE usuarios 
                    SET ultimo_acceso = CURRENT_TIMESTAMP 
                    WHERE id_usuario = %s
                """
                cursor.execute(update_query, (user_data['id_usuario'],))
                conn.commit()
                
                # Guardar credenciales si el usuario lo desea
                self.guardar_credenciales(usuario)
                
                # Mostrar mensaje de bienvenida
                messagebox.showinfo(
                    "Bienvenido", 
                    f"¡Bienvenido, {user_data['nombre_usuario']}!\n"
                    f"Rol: {user_data['rol']}\n\n"
                    "Acceso concedido al sistema."
                )
                
                # Navegar al menú principal con los datos del usuario
                self.app.show_menu(user_data['nombre_usuario'])

            else:
                messagebox.showerror(
                    "Error de autenticación", 
                    "Usuario o contraseña incorrectos"
                )
                self.entrada_clave.delete(0, "end")
                
        except Exception as e:
            messagebox.showerror(
                "Error de conexión", 
                f"No se pudo verificar las credenciales:\n{str(e)}"
            )
        finally:
            # Restaurar estado del botón
            if self.boton_login.winfo_exists():
                self.boton_login.configure(text="Iniciar Sesión", state="normal")

            if conn:
                conn.close()

    def completar_login_exitoso(self, usuario):
        """Completa el proceso de login exitoso"""
        messagebox.showinfo(
            "Bienvenido", 
            f"¡Bienvenido, {usuario}!\n\nAcceso concedido al sistema."
        )
        
        # Navegar al menú principal a través del app_manager
        self.app.show_menu(usuario)

    def recuperar_contrasena(self):
        print("Recuperar contraseña no implementado")

    def registrarse(self):
        print("Registro no implementado")

    



        

    