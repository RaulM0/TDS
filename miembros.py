import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from conn import get_connection
import re

class MemberManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_member = None
        
        self._create_ui()
        self.update_members_list()
        self.search_entry.focus()
    
    def _create_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuración del grid
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Frame de búsqueda
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(
            search_frame, text="← Menú", width=80,
            command=self.return_to_menu, fg_color="#6c757d"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(search_frame, text="Buscar Estudiante:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, width=300,
            placeholder_text="Nombre, código o correo..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_members())
        
        ctk.CTkButton(
            search_frame, text="Buscar", command=self.search_members, width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame, text="Limpiar", command=self.clear_search, width=100
        ).pack(side="left")
        
        # Lista de estudiantes
        self._create_members_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(self.main_frame, text="Listo", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_members_list(self):
        self.list_frame = ctk.CTkFrame(self.main_frame, width=350)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.member_count_label = ctk.CTkLabel(
            header_frame, text="Estudiantes (0)", font=ctk.CTkFont(weight="bold")
        )
        self.member_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame, text="+ Nuevo", width=80, command=self.new_member
        ).pack(side="right")
        
        self.list_scroll = ctk.CTkScrollableFrame(self.list_frame, height=550)
        self.list_scroll.pack(fill="both", expand=True)
    
    def _create_form(self):
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")

        self.form_title = ctk.CTkLabel(
            self.form_frame, text="Nuevo Estudiante", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))

        fields = [
            {"label": "Código Estudiante*", "name": "code"},
            {"label": "Nombre*", "name": "name"},
            {"label": "Apellido Paterno*", "name": "lastname1"},
            {"label": "Apellido Materno*", "name": "lastname2"},
            {"label": "Correo*", "name": "email"},
            {"label": "Teléfono", "name": "phone"},
            {"label": "Fecha Nacimiento", "name": "birthdate", "placeholder": "AAAA-MM-DD"},
            {"label": "Carrera", "name": "career"},
            {"label": "Semestre", "name": "semester"},
            {"label": "Estado*", "name": "status", "type": "combobox", 
             "values": ["Inscrito", "No inscrito", "Graduado", "Baja temporal"]},
        ]

        self.form_widgets = {}

        for field in fields:
            frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)

            label = ctk.CTkLabel(frame, text=field["label"], width=120)
            label.pack(side="left")

            if field.get("type") == "combobox":
                widget = ctk.CTkComboBox(frame, values=field["values"], state="readonly")
                widget.pack(side="right", fill="x", expand=True)
                widget.set("Inscrito")
            else:
                widget = ctk.CTkEntry(frame)
                if field.get("placeholder"):
                    widget.configure(placeholder_text=field["placeholder"])
                widget.pack(side="right", fill="x", expand=True)
                
                if field["name"] == "semester":
                    widget.insert(0, "1")

            self.form_widgets[field["name"]] = widget

        # Botones
        button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            button_frame, text="Guardar", command=self.save_member, fg_color="#28a745"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame, text="Cancelar", command=self.cancel_edit
        ).pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(
            button_frame, text="Eliminar", command=self.delete_member,
            fg_color="#dc3545", state="disabled"
        )
        self.delete_btn.pack(side="right")
    
    def return_to_menu(self):
        self.app.show_menu(self.app.current_user)
    
    def update_members_list(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        self.members_data = self.get_members_from_db()
        self.member_count_label.configure(text=f"Estudiantes ({len(self.members_data)})")
        
        if not self.members_data:
            ctk.CTkLabel(
                self.list_scroll, text="No se encontraron estudiantes", text_color="gray"
            ).pack(pady=20)
            return
        
        for member in self.members_data:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = f"{member.get('codigo_estudiante', '')} - {member.get('nombre', '')} {member.get('appat', '')} {member.get('apmat', '')}"
            ctk.CTkLabel(frame, text=text, anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame, text="Editar", width=60,
                command=lambda m=member: self.load_member_data(m)
            ).pack(side="right", padx=2)
    
    def load_member_data(self, member):
        self.current_member = member
        full_name = f"{member.get('nombre', '')} {member.get('appat', '')} {member.get('apmat', '')}"
        self.form_title.configure(text=f"Editando: {full_name}")
        self.delete_btn.configure(state="normal")
        
        field_mapping = {
            "code": member.get("codigo_estudiante", ""),
            "name": member.get("nombre", ""),
            "lastname1": member.get("appat", ""),
            "lastname2": member.get("apmat", ""),
            "email": member.get("correo", ""),
            "phone": member.get("telefono", ""),
            "birthdate": member.get("fecha_nacimiento", ""),
            "career": member.get("carrera", ""),
            "semester": str(member.get("semestre", "")),
            "status": member.get("estado_inscripcion", "Inscrito")
        }

        for field_name, value in field_mapping.items():
            widget = self.form_widgets[field_name]
            
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                widget.insert(0, value)
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(value)
    
    def clear_form(self):
        for widget in self.form_widgets.values():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")
        
        self.current_member = None
        self.form_title.configure(text="Nuevo Estudiante")
        self.delete_btn.configure(state="disabled")
        self.form_widgets["status"].set("Inscrito")
        self.form_widgets["semester"].insert(0, "1")
    
    def validate_form(self):
        errors = []

        required_fields = ["code", "name", "lastname1", "lastname2", "email", "status"]
        for field in required_fields:
            widget = self.form_widgets[field]
            value = widget.get() if hasattr(widget, 'get') else ""
            if not value.strip():
                field_name = field.replace("lastname1", "Apellido Paterno")\
                                .replace("lastname2", "Apellido Materno")\
                                .replace("code", "Código")\
                                .replace("name", "Nombre")\
                                .replace("email", "Correo")\
                                .replace("status", "Estado")
                errors.append(f"El campo {field_name} es obligatorio")

        # Validar formato de correo
        email = self.form_widgets["email"].get().strip()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("El correo electrónico no es válido")

        # Validar semestre numérico
        semester = self.form_widgets["semester"].get().strip()
        if semester and not semester.isdigit():
            errors.append("El semestre debe ser un número")

        # Validar fecha de nacimiento si está presente
        birthdate = self.form_widgets["birthdate"].get().strip()
        if birthdate:
            try:
                datetime.strptime(birthdate, "%Y-%m-%d")
            except ValueError:
                errors.append("La fecha de nacimiento debe tener formato AAAA-MM-DD")

        return errors if errors else None
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {}
        
        field_mapping = {
            "code": "codigo_estudiante",
            "name": "nombre",
            "lastname1": "appat",
            "lastname2": "apmat",
            "email": "correo",
            "phone": "telefono",
            "birthdate": "fecha_nacimiento",
            "career": "carrera",
            "semester": "semestre",
            "status": "estado_inscripcion"
        }
        
        for form_name, db_name in field_mapping.items():
            widget = self.form_widgets[form_name]
            
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get().strip()
                data[db_name] = value if value else None
            elif isinstance(widget, ctk.CTkComboBox):
                data[db_name] = widget.get().strip()
        
        # Convertir semestre a entero si existe
        if data.get("semestre"):
            try:
                data["semestre"] = int(data["semestre"])
            except ValueError:
                data["semestre"] = None
        
        # Convertir fecha vacía a None
        if data.get("fecha_nacimiento") == "":
            data["fecha_nacimiento"] = None
        
        return data
    
    def save_member(self):
        """Guarda los datos del estudiante"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return
        
        member_data = self.get_form_data()
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_member:
                # Actualizar estudiante existente
                cursor.execute("""
                    UPDATE estudiantes SET
                    codigo_estudiante=%s, nombre=%s, appat=%s, apmat=%s,
                    correo=%s, telefono=%s, fecha_nacimiento=%s,
                    carrera=%s, semestre=%s, estado_inscripcion=%s
                    WHERE id_estudiante=%s
                """, (
                    member_data["codigo_estudiante"], member_data["nombre"], 
                    member_data["appat"], member_data["apmat"],
                    member_data["correo"], member_data["telefono"],
                    member_data["fecha_nacimiento"], member_data["carrera"], 
                    member_data["semestre"], member_data["estado_inscripcion"],
                    self.current_member["id_estudiante"]
                ))
                action = "actualizado"
            else:
                # Crear nuevo estudiante
                cursor.execute("""
                    INSERT INTO estudiantes (
                        codigo_estudiante, nombre, appat, apmat,
                        correo, telefono, fecha_nacimiento,
                        carrera, semestre, estado_inscripcion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    member_data["codigo_estudiante"], member_data["nombre"], 
                    member_data["appat"], member_data["apmat"],
                    member_data["correo"], member_data["telefono"],
                    member_data["fecha_nacimiento"], member_data["carrera"], 
                    member_data["semestre"], member_data["estado_inscripcion"]
                ))
                action = "creado"
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Estudiante {action} correctamente")
            self.update_members_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el estudiante: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_member(self):
        """Elimina el estudiante actual"""
        if not self.current_member:
            return
            
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar al estudiante:\n\n"
            f"{self.current_member.get('nombre', '')} {self.current_member.get('appat', '')} {self.current_member.get('apmat', '')}\n"
            f"Código: {self.current_member.get('codigo_estudiante', '')}",
            icon="warning"
        )
        
        if confirm:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM estudiantes WHERE id_estudiante = %s",
                    (self.current_member["id_estudiante"],)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    messagebox.showinfo("Éxito", "Estudiante eliminado correctamente")
                    self.update_members_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el estudiante")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar estudiante: {str(e)}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
    
    def search_members(self):
        """Busca estudiantes según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_members_list()
            return
        
        all_members = self.get_members_from_db()
        
        filtered = [
            m for m in all_members
            if (search_term in m.get("codigo_estudiante", "").lower() or
                search_term in m.get("nombre", "").lower() or
                search_term in m.get("appat", "").lower() or
                search_term in m.get("apmat", "").lower() or
                search_term in (m.get("correo", "") or "").lower())
        ]
        
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for member in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = f"{member.get('codigo_estudiante', '')} - {member.get('nombre', '')} {member.get('appat', '')} {member.get('apmat', '')}"
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda m=member: self.load_member_data(m)
            ).pack(side="right", padx=2)
        
        self.member_count_label.configure(text=f"Estudiantes ({len(filtered)} encontrados)")
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, "end")
        self.update_members_list()
    
    def new_member(self):
        """Prepara el formulario para nuevo estudiante"""
        self.clear_form()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()

    # ======================
    # MÉTODOS DE BASE DE DATOS
    # ======================

    def get_members_from_db(self):
        """Obtiene todos los estudiantes de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_estudiante, codigo_estudiante, nombre, appat, apmat,
                       correo, telefono, fecha_nacimiento, carrera, semestre, estado_inscripcion
                FROM estudiantes
                ORDER BY appat, apmat, nombre
            """)
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estudiantes: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()