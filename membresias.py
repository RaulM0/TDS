import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from conn import get_connection
import re

class MembershipManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_membership = None
        
        self._create_ui()
        self.update_memberships_list()
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
        
        ctk.CTkLabel(search_frame, text="Buscar Membresía:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, width=300,
            placeholder_text="Estudiante, club o estado..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_memberships())
        
        ctk.CTkButton(
            search_frame, text="Buscar", command=self.search_memberships, width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame, text="Limpiar", command=self.clear_search, width=100
        ).pack(side="left")
        
        # Lista de membresías
        self._create_memberships_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(self.main_frame, text="Listo", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_memberships_list(self):
        """Crea el panel de lista de membresías con mejor visualización de botones"""
        self.list_frame = ctk.CTkFrame(self.main_frame, width=450)  # Aumentamos un poco el ancho
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        # Cabecera
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.membership_count_label = ctk.CTkLabel(
            header_frame,
            text="Membresías (0)",
            font=ctk.CTkFont(weight="bold")
        )
        self.membership_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame,
            text="+ Nueva",
            width=80,
            command=self.new_membership
        ).pack(side="right")
        
        # Lista con scroll - aumentamos el ancho mínimo
        self.list_scroll = ctk.CTkScrollableFrame(
            self.list_frame,
            height=550,
            width=430  # Ancho mínimo mayor
        )
        self.list_scroll.pack(fill="both", expand=True)
    
    def _create_form(self):
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")

        self.form_title = ctk.CTkLabel(
            self.form_frame, text="Nueva Membresía", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))

        fields = [
            {"label": "ID Estudiante*", "name": "student_id"},
            {"label": "ID Club*", "name": "club_id"},
            {"label": "Fecha Inscripción*", "name": "start_date", "placeholder": "AAAA-MM-DD"},
            {"label": "Fecha Expiración", "name": "end_date", "placeholder": "AAAA-MM-DD"},
            {"label": "Estado*", "name": "status", "type": "combobox", 
             "values": ["Activa", "Inactiva", "Suspendida", "En proceso"]},
            {"label": "Rol*", "name": "role", "type": "combobox",
             "values": ["Miembro", "Coordinador", "Secretario", "Tesorero", "Asesor"]},
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
                    widget.set("En proceso")
                elif field["name"] == "role":
                    widget.set("Miembro")
            else:
                widget = ctk.CTkEntry(frame)
                if field.get("placeholder"):
                    widget.configure(placeholder_text=field["placeholder"])
                widget.pack(side="right", fill="x", expand=True)
                
                if field["name"] == "start_date":
                    widget.insert(0, datetime.now().strftime("%Y-%m-%d"))

            self.form_widgets[field["name"]] = widget

        # Botones
        button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            button_frame, text="Guardar", command=self.save_membership, fg_color="#28a745"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame, text="Cancelar", command=self.cancel_edit
        ).pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(
            button_frame, text="Eliminar", command=self.delete_membership,
            fg_color="#dc3545", state="disabled"
        )
        self.delete_btn.pack(side="right")
    
    def return_to_menu(self):
        self.app.show_menu(self.app.current_user)
    
    def update_memberships_list(self):
        """Actualiza la lista de membresías con mejor distribución"""
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        self.memberships_data = self.get_memberships_from_db()
        self.membership_count_label.configure(text=f"Membresías ({len(self.memberships_data)})")
        
        if not self.memberships_data:
            ctk.CTkLabel(
                self.list_scroll,
                text="No se encontraron membresías",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for membership in self.memberships_data:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2, padx=2)  # Añadimos padx para espacio lateral
            
            # Configuramos pesos para la distribución
            frame.grid_columnconfigure(0, weight=3)  # Más espacio para la info
            frame.grid_columnconfigure(1, weight=1)  # Menos espacio para el botón
            
            # Texto de la membresía
            text = (f"Est.ID:{membership['id_estudiante']} Club.ID:{membership['id_club']} - "
                f"{membership['estado_membresia']} ({membership['rol']})")
            
            label = ctk.CTkLabel(
                frame,
                text=text,
                anchor="w",
                wraplength=300  # Permite ajuste de texto
            )
            label.grid(row=0, column=0, sticky="ew", padx=(5, 0))
            
            # Botón Editar - ahora más visible
            edit_btn = ctk.CTkButton(
                frame,
                text="Editar",
                width=70,
                command=lambda m=membership: self.load_membership_data(m),
                fg_color="#0d6efd",  # Azul más llamativo
                hover_color="#0b5ed7"
            )
            edit_btn.grid(row=0, column=1, sticky="e", padx=(0, 5))
    
    def load_membership_data(self, membership):
        self.current_membership = membership
        self.form_title.configure(
            text=f"Editando: Est. ID:{membership['id_estudiante']} en Club ID:{membership['id_club']}"
        )
        self.delete_btn.configure(state="normal")
        
        field_mapping = {
            "student_id": str(membership.get("id_estudiante", "")),
            "club_id": str(membership.get("id_club", "")),
            "start_date": membership.get("fecha_inscripcion", ""),
            "end_date": membership.get("fecha_expiracion", ""),
            "status": membership.get("estado_membresia", "En proceso"),
            "role": membership.get("rol", "Miembro")
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
        
        self.current_membership = None
        self.form_title.configure(text="Nueva Membresía")
        self.delete_btn.configure(state="disabled")
        self.form_widgets["status"].set("En proceso")
        self.form_widgets["role"].set("Miembro")
        self.form_widgets["start_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def validate_form(self):
        errors = []

        # Validar campos obligatorios
        required_fields = ["student_id", "club_id", "start_date", "status", "role"]
        for field in required_fields:
            widget = self.form_widgets[field]
            value = widget.get() if hasattr(widget, 'get') else ""
            if not value.strip():
                field_name = field.replace("_", " ").title()
                errors.append(f"El campo {field_name} es obligatorio")

        # Validar que los IDs sean números
        student_id = self.form_widgets["student_id"].get().strip()
        club_id = self.form_widgets["club_id"].get().strip()
        
        if student_id and not student_id.isdigit():
            errors.append("El ID del estudiante debe ser un número")
        
        if club_id and not club_id.isdigit():
            errors.append("El ID del club debe ser un número")

        # Validar formato de fechas
        start_date = self.form_widgets["start_date"].get().strip()
        end_date = self.form_widgets["end_date"].get().strip()
        
        try:
            if start_date:
                datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Las fechas deben estar en formato AAAA-MM-DD")

        return errors if errors else None
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {}
        
        # Obtener valores de los widgets
        data["id_estudiante"] = int(self.form_widgets["student_id"].get().strip())
        data["id_club"] = int(self.form_widgets["club_id"].get().strip())
        data["fecha_inscripcion"] = self.form_widgets["start_date"].get().strip()
        
        end_date = self.form_widgets["end_date"].get().strip()
        data["fecha_expiracion"] = end_date if end_date else None
        
        data["estado_membresia"] = self.form_widgets["status"].get()
        data["rol"] = self.form_widgets["role"].get()
        
        return data
    
    def save_membership(self):
        """Guarda los datos de la membresía"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return
        
        membership_data = self.get_form_data()
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_membership:
                # Actualizar membresía existente
                membership_data["id_membresia"] = self.current_membership["id_membresia"]
                cursor.execute("""
                    UPDATE membresias SET
                    id_estudiante=%s, id_club=%s,
                    fecha_inscripcion=%s, fecha_expiracion=%s,
                    estado_membresia=%s, rol=%s
                    WHERE id_membresia=%s
                """, (
                    membership_data["id_estudiante"],
                    membership_data["id_club"],
                    membership_data["fecha_inscripcion"],
                    membership_data["fecha_expiracion"],
                    membership_data["estado_membresia"],
                    membership_data["rol"],
                    membership_data["id_membresia"]
                ))
                action = "actualizada"
            else:
                # Crear nueva membresía
                cursor.execute("""
                    INSERT INTO membresias (
                        id_estudiante, id_club,
                        fecha_inscripcion, fecha_expiracion,
                        estado_membresia, rol
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    membership_data["id_estudiante"],
                    membership_data["id_club"],
                    membership_data["fecha_inscripcion"],
                    membership_data["fecha_expiracion"],
                    membership_data["estado_membresia"],
                    membership_data["rol"]
                ))
                action = "creada"
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Membresía {action} correctamente")
            self.update_memberships_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la membresía: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_membership(self):
        """Elimina la membresía actual"""
        if not self.current_membership:
            return
            
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar la membresía:\n\n"
            f"Estudiante ID: {self.current_membership.get('id_estudiante', '')}\n"
            f"Club ID: {self.current_membership.get('id_club', '')}\n"
            f"Rol: {self.current_membership.get('rol', '')}",
            icon="warning"
        )
        
        if confirm:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM membresias WHERE id_membresia = %s",
                    (self.current_membership["id_membresia"],)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    messagebox.showinfo("Éxito", "Membresía eliminada correctamente")
                    self.update_memberships_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la membresía")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar membresía: {str(e)}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
    
    def search_memberships(self):
        """Busca membresías según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_memberships_list()
            return
        
        all_memberships = self.get_memberships_from_db()
        
        filtered = [
            m for m in all_memberships
            if (search_term in str(m.get("id_estudiante", "")).lower() or
               search_term in str(m.get("id_club", "")).lower() or
               search_term in m.get("estado_membresia", "").lower() or
               search_term in m.get("rol", "").lower()
            )
        ]
        
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for membership in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = (f"Est. ID:{membership['id_estudiante']} en Club ID:{membership['id_club']} - "
                   f"{membership['estado_membresia']} ({membership['rol']})")
            
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda m=membership: self.load_membership_data(m)
            ).pack(side="right", padx=2)
        
        self.membership_count_label.configure(text=f"Membresías ({len(filtered)} encontradas)")
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, "end")
        self.update_memberships_list()
    
    def new_membership(self):
        """Prepara el formulario para nueva membresía"""
        self.clear_form()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()

    # ======================
    # MÉTODOS DE BASE DE DATOS
    # ======================

    def get_memberships_from_db(self):
        """Obtiene todas las membresías de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT m.id_membresia, m.id_estudiante, m.id_club,
                       m.fecha_inscripcion, m.fecha_expiracion,
                       m.estado_membresia, m.rol
                FROM membresias m
                ORDER BY m.id_estudiante, m.id_club
            """)
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar membresías: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()