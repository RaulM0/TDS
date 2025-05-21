import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from conn import get_connection
import re

class UserManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_user = None
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Construir interfaz
        self._create_ui()
        
        # Cargar datos iniciales
        self.update_users_list()

    def _create_ui(self):
        """Construye la interfaz gráfica"""
        # Configuración del grid principal
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Frame de búsqueda con botón de regreso
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Botón para regresar al menú
        ctk.CTkButton(
            search_frame,
            text="← Menú",
            width=80,
            command=self.return_to_menu,
            fg_color="#6c757d",
            hover_color="#5a6268"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(search_frame, text="Buscar Usuarios:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Nombre, usuario, correo o rol..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_users())
        
        ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self.search_users,
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="Limpiar",
            command=self.clear_search,
            width=100
        ).pack(side="left")
        
        # Lista de usuarios
        self._create_users_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Listo",
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_users_list(self):
        """Crea el panel de lista de usuarios"""
        self.list_frame = ctk.CTkFrame(self.main_frame, width=400)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        # Cabecera
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.user_count_label = ctk.CTkLabel(
            header_frame,
            text="Usuarios (0)",
            font=ctk.CTkFont(weight="bold")
        )
        self.user_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame,
            text="+ Nuevo",
            width=80,
            command=self.new_user
        ).pack(side="right")
        
        # Lista con scroll
        self.list_scroll = ctk.CTkScrollableFrame(
            self.list_frame,
            height=550
        )
        self.list_scroll.pack(fill="both", expand=True)
    
    def _create_form(self):
        """Crea el formulario de edición"""
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")
        
        # Título del formulario
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Nuevo Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))
        
        # Campos del formulario según la estructura de la tabla usuarios
        fields = [
            {"label": "ID Usuario", "name": "id", "editable": False},
            {"label": "Nombre Usuario*", "name": "username"},
            {"label": "Contraseña*", "name": "password", "password": True},
            {"label": "Correo Electrónico*", "name": "email"},
            {"label": "Rol*", "name": "role", "type": "combobox", 
             "values": ["Administrador", "Coordinador"]},
            {"label": "Estado*", "name": "status", "type": "combobox", 
             "values": ["Activo", "Inactivo", "Suspendido"]},
            {"label": "ID Estudiante", "name": "student_id"}
        ]
        
        self.form_widgets = {}
        
        for field in fields:
            frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            label_text = field["label"].replace("*", "") + (" *" if "*" in field["label"] else "")
            ctk.CTkLabel(frame, text=label_text, width=120).pack(side="left")
            
            if field.get("type") == "combobox":
                widget = ctk.CTkComboBox(frame, values=field["values"], state="readonly")
                widget.pack(side="right", fill="x", expand=True)
                widget.set(field["values"][0])
            elif field.get("password"):
                widget = ctk.CTkEntry(frame, show="•")
                widget.pack(side="right", fill="x", expand=True)
                
                # Botón para mostrar/ocultar contraseña
                eye_btn = ctk.CTkButton(
                    frame,
                    text="👁",
                    width=30,
                    command=lambda w=widget: self.toggle_password_visibility(w)
                )
                eye_btn.pack(side="right", padx=(5, 0))
            else:
                widget = ctk.CTkEntry(frame)
                if not field.get("editable", True):
                    widget.configure(state="disabled")
                widget.pack(side="right", fill="x", expand=True)
            
            self.form_widgets[field["name"]] = widget
        
        # Botones de acción
        button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.save_user,
            fg_color="#28a745"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.cancel_edit
        ).pack(side="left", padx=(0, 10))
        
        self.delete_btn = ctk.CTkButton(
            button_frame,
            text="Eliminar",
            command=self.delete_user,
            fg_color="#dc3545",
            state="disabled"
        )
        self.delete_btn.pack(side="right")
    
    def toggle_password_visibility(self, entry):
        """Alterna entre mostrar y ocultar la contraseña"""
        if entry.cget("show") == "":
            entry.configure(show="•")
        else:
            entry.configure(show="")
    
    def return_to_menu(self):
        """Regresa al menú principal"""
        self.app.show_menu(self.app.current_user)
    
    def update_users_list(self):
        """Actualiza la lista de usuarios"""
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        users = self.get_users_from_db()
        self.user_count_label.configure(text=f"Usuarios ({len(users)})")
        
        if not users:
            ctk.CTkLabel(
                self.list_scroll,
                text="No se encontraron usuarios",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for user in users:
            frame = ctk.CTkFrame(self.list_scroll, height=50)
            frame.pack(fill="x", pady=2, padx=5)

            frame.grid_columnconfigure(0, weight=1)  # Permite que el texto se expanda

            text = (f"{user['nombre_usuario']} - {user['correo']} "
                    f"({user['rol']}) - {user['estado']}")

            label = ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            )
            label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            edit_button = ctk.CTkButton(
                frame,
                text="Editar",
                width=70,
                height=30,
                command=lambda u=user: self.load_user_data(u)
            )
            edit_button.grid(row=0, column=1, sticky="e", padx=10)


    def load_user_data(self, user):
        """Carga los datos de un usuario en el formulario"""
        self.current_user = user
        self.form_title.configure(
            text=f"Editando Usuario #{user['id_usuario']}"
        )
        self.delete_btn.configure(state="normal")
        
        field_mapping = {
            "id": str(user.get("id_usuario", "")),
            "username": user.get("nombre_usuario", ""),
            "password": user.get("contrasena", ""),
            "email": user.get("correo", ""),
            "role": user.get("rol", "Coordinador"),
            "status": user.get("estado", "Activo"),
            "student_id": str(user.get("id_estudiante", "")) if user.get("id_estudiante") else ""
        }
        
        for field_name, value in field_mapping.items():
            widget = self.form_widgets[field_name]
            
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state="normal")
                widget.delete(0, "end")
                widget.insert(0, value)
                if field_name == "id":
                    widget.configure(state="disabled")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(value)
    
    def clear_form(self):
        """Limpia el formulario"""
        for field_name, widget in self.form_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state="normal")
                widget.delete(0, "end")
                if field_name == "id":
                    widget.configure(state="disabled")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(widget._values[0])
        
        self.current_user = None
        self.form_title.configure(text="Nuevo Usuario")
        self.delete_btn.configure(state="disabled")
    
    def validate_form(self):
        """Valida los campos del formulario"""
        errors = []
        
        required_fields = ["username", "password", "email", "role", "status"]
        for field in required_fields:
            widget = self.form_widgets[field]
            value = ""
            
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get().strip()
            elif isinstance(widget, ctk.CTkComboBox):
                value = widget.get().strip()
            
            if not value:
                field_name = field.replace("_", " ").title()
                errors.append(f"El campo {field_name} es obligatorio")
        
        # Validar formato de email
        email = self.form_widgets["email"].get().strip()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("El correo electrónico no es válido")
        
        # Validar que student_id sea numérico si existe
        student_id = self.form_widgets["student_id"].get().strip()
        if student_id and not student_id.isdigit():
            errors.append("El ID de estudiante debe ser un número")
        
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return False
        return True
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {
            "nombre_usuario": self.form_widgets["username"].get().strip(),
            "contrasena": self.form_widgets["password"].get().strip(),
            "correo": self.form_widgets["email"].get().strip(),
            "rol": self.form_widgets["role"].get().strip(),
            "estado": self.form_widgets["status"].get().strip(),
            "id_estudiante": int(self.form_widgets["student_id"].get()) if self.form_widgets["student_id"].get().strip() else None
        }
        
        if self.current_user:
            data["id_usuario"] = self.current_user["id_usuario"]
        
        return data
    
    def search_users(self):
        """Busca usuarios según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_users_list()
            return
        
        users = self.get_users_from_db()
        filtered = [
            u for u in users
            if (search_term in u['nombre_usuario'].lower() or
               search_term in u['correo'].lower() or
               search_term in u['rol'].lower() or
               search_term in u['estado'].lower() or
               search_term in str(u.get('id_estudiante', '')).lower())
        ]
        
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for user in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = (f"{user['nombre_usuario']} - {user['correo']} "
                   f"({user['rol']}) - {user['estado']}")
            
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda u=user: self.load_user_data(u)
            ).pack(side="right", padx=2)
        
        self.user_count_label.configure(text=f"Usuarios ({len(filtered)} encontrados)")
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, "end")
        self.update_users_list()
    
    def new_user(self):
        """Prepara el formulario para nuevo usuario"""
        self.clear_form()
    
    def save_user(self):
        """Guarda los datos del usuario"""
        if not self.validate_form():
            return
        
        user_data = self.get_form_data()
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_user:
                # Actualizar usuario existente
                query = """UPDATE usuarios SET 
                          nombre_usuario = %s,
                          contrasena = IF(%s IS NULL OR %s = '', contrasena, %s),
                          correo = %s,
                          rol = %s,
                          estado = %s,
                          id_estudiante = %s
                          WHERE id_usuario = %s"""
                params = (
                    user_data['nombre_usuario'],
                    user_data['contrasena'],
                    user_data['contrasena'],
                    user_data['contrasena'],
                    user_data['correo'],
                    user_data['rol'],
                    user_data['estado'],
                    user_data['id_estudiante'],
                    user_data['id_usuario']
                )
                action = "actualizado"
            else:
                # Crear nuevo usuario
                query = """INSERT INTO usuarios (
                          nombre_usuario, contrasena, correo,
                          rol, estado, id_estudiante
                          ) VALUES (%s, %s, %s, %s, %s, %s)"""
                params = (
                    user_data['nombre_usuario'],
                    user_data['contrasena'],
                    user_data['correo'],
                    user_data['rol'],
                    user_data['estado'],
                    user_data['id_estudiante']
                )
                action = "registrado"
            
            cursor.execute(query, params)
            conn.commit()
            
            messagebox.showinfo("Éxito", f"Usuario {action} correctamente")
            self.update_users_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar usuario:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_user(self):
        """Elimina el usuario actual"""
        if not self.current_user:
            return
            
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar este usuario?\n\n"
            f"Usuario: {self.current_user['nombre_usuario']}\n"
            f"Correo: {self.current_user['correo']}\n"
            f"Rol: {self.current_user['rol']}",
            icon="warning"
        )
        
        if not confirmacion:
            return
            
        conn = None
        try:
            # Verificar si el usuario a eliminar es el mismo que está logueado
            if hasattr(self.app, 'current_user') and self.app.current_user and self.app.current_user['id_usuario'] == self.current_user['id_usuario']:
                raise Exception("No puedes eliminar tu propio usuario mientras estás logueado")
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM usuarios WHERE id_usuario = %s",
                (self.current_user['id_usuario'],)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self.update_users_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar usuario:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()

    def get_users_from_db(self):
        """Obtiene todos los usuarios de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = '''
                SELECT u.*, 
                CONCAT(e.nombre, ' ', e.appat, ' ', e.apmat) AS nombre_estudiante
                FROM usuarios u
                LEFT JOIN estudiantes e ON u.id_estudiante = e.id_estudiante
                ORDER BY u.nombre_usuario
            '''
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios:\n{str(e)}")
            return []
        finally:
            if conn:
                conn.close()