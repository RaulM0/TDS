import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from conn import get_connection
import re

class ClubManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_club = None
        self.clubs_data = []
        
        self._create_ui()
        self.update_clubs_list()
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
        
        ctk.CTkLabel(search_frame, text="Buscar Club:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, width=300,
            placeholder_text="Nombre, código o responsable..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_clubs())
        
        ctk.CTkButton(search_frame, text="Buscar", command=self.search_clubs, width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(search_frame, text="Limpiar", command=self.clear_search, width=100
        ).pack(side="left")
        
        # Lista de clubs
        self._create_clubs_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(self.main_frame, text="Listo", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_clubs_list(self):
        self.list_frame = ctk.CTkFrame(self.main_frame, width=350)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.club_count_label = ctk.CTkLabel(
            header_frame, text="Clubs (0)", font=ctk.CTkFont(weight="bold")
        )
        self.club_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame, text="+ Nuevo", width=80, command=self.new_club
        ).pack(side="right")
        
        self.list_scroll = ctk.CTkScrollableFrame(self.list_frame, height=550)
        self.list_scroll.pack(fill="both", expand=True)
    
    def _create_form(self):
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")

        self.form_title = ctk.CTkLabel(
            self.form_frame, text="Nuevo Club", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))

        fields = [
            {"label": "Código Club*", "name": "code"},
            {"label": "Nombre Club*", "name": "name"},
            {"label": "Responsable", "name": "responsable"},
            {"label": "Correo Contacto", "name": "email"},
            {"label": "Estado*", "name": "status", "type": "combobox", "values": ["Activo", "Inactivo", "En pausa"]},
            {"label": "Fecha Creación", "name": "creation_date"},
            {"label": "Máx. Miembros", "name": "max_members"},
            {"label": "Requisitos", "name": "requirements", "type": "textbox"},
            {"label": "Descripción", "name": "description", "type": "textbox"},
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
                if field["name"] == "status":
                    widget.set("Activo")
            elif field.get("type") == "textbox":
                widget = ctk.CTkTextbox(frame, height=60)
                widget.pack(side="right", fill="x", expand=True)
            else:
                widget = ctk.CTkEntry(frame)
                widget.pack(side="right", fill="x", expand=True)
                if field["name"] == "creation_date":
                    widget.insert(0, datetime.now().strftime("%Y-%m-%d"))

            self.form_widgets[field["name"]] = widget

        # Botones
        button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            button_frame, text="Guardar", command=self.save_club, fg_color="#28a745"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame, text="Cancelar", command=self.cancel_edit
        ).pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(
            button_frame, text="Eliminar", command=self.delete_club,
            fg_color="#dc3545", state="disabled"
        )
        self.delete_btn.pack(side="right")

    def return_to_menu(self):
        self.app.show_menu(self.app.current_user)
    
    def update_clubs_list(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        self.clubs_data = self.get_clubs_from_db()
        self.club_count_label.configure(text=f"Clubs ({len(self.clubs_data)})")
        
        if not self.clubs_data:
            ctk.CTkLabel(
                self.list_scroll, text="No se encontraron clubs", text_color="gray"
            ).pack(pady=20)
            return
        
        for club in self.clubs_data:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = f"{club.get('codigo_club', '')} - {club.get('nombre_club', '')}"
            ctk.CTkLabel(frame, text=text, anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame, text="Editar", width=60,
                command=lambda c=club: self.load_club_data(c)
            ).pack(side="right", padx=2)
    
    def load_club_data(self, club):
        self.current_club = club
        self.form_title.configure(text=f"Editando: {club.get('nombre_club', '')}")
        self.delete_btn.configure(state="normal")
        
        # Mapeo de campos de la base de datos a los widgets del formulario
        field_mapping = {
            "code": club.get("codigo_club", ""),
            "name": club.get("nombre_club", ""),
            "responsable": club.get("responsable", ""),
            "email": club.get("correo_contacto", ""),
            "status": club.get("estado", "Activo"),
            "creation_date": club.get("fecha_creacion", ""),
            "max_members": str(club.get("max_miembros", "")),
            "requirements": club.get("requisitos", ""),
            "description": club.get("descripcion", "")
        }

        for field_name, value in field_mapping.items():
            widget = self.form_widgets[field_name]
            
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                widget.insert(0, value)
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
                widget.insert("1.0", value)
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(value)
    
    def clear_form(self):
        for widget in self.form_widgets.values():
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
            elif isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")
        
        # Restablecer valores por defecto
        self.current_club = None
        self.form_title.configure(text="Nuevo Club")
        self.delete_btn.configure(state="disabled")
        self.form_widgets["status"].set("Activo")
        self.form_widgets["creation_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def validate_form(self):
        errores = []

        if not self.form_widgets["code"].get().strip():
            errores.append("El código del club es obligatorio.")
        if not self.form_widgets["name"].get().strip():
            errores.append("El nombre del club es obligatorio.")
        if not self.form_widgets["status"].get().strip():
            errores.append("El estado es obligatorio.")

        # Validar correo si no está vacío
        email = self.form_widgets["email"].get().strip()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errores.append("Correo no es válido.")

        # Validar fecha creación (simple)
        fecha = self.form_widgets["creation_date"].get().strip()
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            errores.append("Fecha de creación no válida, usar formato AAAA-MM-DD.")

        # Validar max miembros si no está vacío
        max_members = self.form_widgets["max_members"].get().strip()
        if max_members and not max_members.isdigit():
            errores.append("Máximo de miembros debe ser un número.")

        return errores if errores else None
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {}
        
        for field_name, widget in self.form_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get().strip()
                data[field_name] = value if value else None
            elif isinstance(widget, ctk.CTkTextbox):
                value = widget.get("1.0", "end-1c").strip()
                data[field_name] = value if value else None
            elif isinstance(widget, ctk.CTkComboBox):
                data[field_name] = widget.get().strip()
        
        # Convertir max_members a entero si existe
        if data.get("max_members"):
            try:
                data["max_members"] = int(data["max_members"])
            except ValueError:
                data["max_members"] = None
        
        return data
    
    def save_club(self):
        """Guarda los datos del club (nueva versión corregida)"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return
        
        club_data = self.get_form_data()
        
        # Mapear nombres de campos a los de la base de datos
        db_mapping = {
            "code": "codigo_club",
            "name": "nombre_club",
            "responsable": "responsable",
            "email": "correo_contacto",
            "status": "estado",
            "creation_date": "fecha_creacion",
            "max_members": "max_miembros",
            "requirements": "requisitos",
            "description": "descripcion"
        }
        
        # Crear diccionario para la base de datos
        db_data = {db_mapping[k]: v for k, v in club_data.items()}
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_club:
                # Actualizar club existente
                db_data["id_club"] = self.current_club["id_club"]
                cursor.execute("""
                    UPDATE clubes SET
                    codigo_club=%s, nombre_club=%s, responsable=%s, 
                    correo_contacto=%s, estado=%s, fecha_creacion=%s,
                    max_miembros=%s, requisitos=%s, descripcion=%s
                    WHERE id_club=%s
                """, (
                    db_data["codigo_club"], db_data["nombre_club"], db_data["responsable"],
                    db_data["correo_contacto"], db_data["estado"], db_data["fecha_creacion"],
                    db_data["max_miembros"], db_data["requisitos"], db_data["descripcion"],
                    db_data["id_club"]
                ))
                action = "actualizado"
            else:
                # Crear nuevo club
                cursor.execute("""
                    INSERT INTO clubes (
                        codigo_club, nombre_club, responsable, 
                        correo_contacto, estado, fecha_creacion, 
                        max_miembros, requisitos, descripcion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    db_data["codigo_club"], db_data["nombre_club"], db_data["responsable"],
                    db_data["correo_contacto"], db_data["estado"], db_data["fecha_creacion"],
                    db_data["max_miembros"], db_data["requisitos"], db_data["descripcion"]
                ))
                action = "creado"
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Club {action} correctamente")
            self.update_clubs_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el club: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_club(self):
        """Elimina el club actual"""
        if not self.current_club:
            return
            
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar el club {self.current_club.get('nombre_club', '')}?\n\n"
            f"Código: {self.current_club.get('codigo_club', '')}\n"
            f"Responsable: {self.current_club.get('responsable', '')}",
            icon="warning"
        )
        
        if confirm:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM clubes WHERE id_club = %s", (self.current_club["id_club"],))
                conn.commit()
                
                if cursor.rowcount > 0:
                    messagebox.showinfo("Éxito", "Club eliminado correctamente")
                    self.update_clubs_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el club")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar club: {str(e)}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()
    
    def get_clubs_from_db(self):
        """Obtiene todos los clubs de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_club, codigo_club, nombre_club, responsable, 
                       correo_contacto, estado, fecha_creacion, 
                       max_miembros, requisitos, descripcion 
                FROM clubes
                ORDER BY nombre_club
            """)
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clubs: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    def search_clubs(self):
        """Busca clubs según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_clubs_list()
            return
        
        # Obtener datos actualizados
        all_clubs = self.get_clubs_from_db()
        
        filtered = [
            club for club in all_clubs
            if (search_term in club.get("nombre_club", "").lower() or
                search_term in club.get("codigo_club", "").lower() or
                search_term in (club.get("responsable", "") or "").lower() or
                search_term in (club.get("correo_contacto", "") or "").lower())
        ]
        
        # Actualizar lista visual
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for club in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = f"{club.get('codigo_club', '')} - {club.get('nombre_club', '')}"
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda c=club: self.load_club_data(c)
            ).pack(side="right", padx=2)
        
        self.club_count_label.configure(text=f"Clubs ({len(filtered)} encontrados)")
    
    def clear_search(self):
        """Limpia la búsqueda y muestra todos los clubs"""
        self.search_entry.delete(0, "end")
        self.update_clubs_list()
    
    def new_club(self):
        """Prepara el formulario para un nuevo club"""
        self.clear_form()