import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from conn import get_connection
import re

class AcademicHistoryWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_record = None
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Construir interfaz
        self._create_ui()
        
        # Cargar datos iniciales
        self.update_records_list()

    def _create_ui(self):
        """Construye la interfaz gráfica"""
        # Configuración del grid principal
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Frame de búsqueda
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
        
        ctk.CTkLabel(search_frame, text="Buscar Historial:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="ID Estudiante, Curso o Estado..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_records())
        
        ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self.search_records,
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="Limpiar",
            command=self.clear_search,
            width=100
        ).pack(side="left")
        
        # Lista de registros
        self._create_records_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Listo",
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_records_list(self):
        """Crea el panel de lista de registros"""
        self.list_frame = ctk.CTkFrame(self.main_frame, width=400)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        # Cabecera
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.record_count_label = ctk.CTkLabel(
            header_frame,
            text="Registros (0)",
            font=ctk.CTkFont(weight="bold")
        )
        self.record_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame,
            text="+ Nuevo",
            width=80,
            command=self.new_record
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
            text="Nuevo Registro",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))
        
        # Campos del formulario según la tabla historial_academico
        fields = [
            {"label": "ID Historial", "name": "id", "editable": False},
            {"label": "ID Estudiante*", "name": "student_id"},
            {"label": "ID Curso*", "name": "course_id"},
            {"label": "Calificación", "name": "grade"},
            {"label": "Fecha Inicio*", "name": "start_date", "placeholder": "YYYY-MM-DD"},
            {"label": "Fecha Fin", "name": "end_date", "placeholder": "YYYY-MM-DD"},
            {"label": "Periodo", "name": "period"},
            {"label": "Estado*", "name": "status", "type": "combobox", 
             "values": ["Aprobado", "Reprobado", "En curso", "Retirado"]}
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
                widget.set("En curso")
            else:
                widget = ctk.CTkEntry(frame)
                if field.get("placeholder"):
                    widget.configure(placeholder_text=field["placeholder"])
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
            command=self.save_record,
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
            command=self.delete_record,
            fg_color="#dc3545",
            state="disabled"
        )
        self.delete_btn.pack(side="right")
    
    def return_to_menu(self):
        """Regresa al menú principal"""
        self.app.show_menu(self.app.current_user)
    
    def update_records_list(self):
        """Actualiza la lista de registros"""
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        records = self.get_records_from_db()
        self.record_count_label.configure(text=f"Registros ({len(records)})")
        
        if not records:
            ctk.CTkLabel(
                self.list_scroll,
                text="No se encontraron registros",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for record in records:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)

            frame.grid_columnconfigure(0, weight=1)
            
            # Formatear información para mostrar
            text = (f"Estudiante #{record['id_estudiante']} - Curso #{record['id_curso']} "
                   f"- {record['estado']} - Calif: {record['calificacion'] or 'N/A'}")
            
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).grid(row=0, column=0, padx=10,pady= 5, sticky="w")
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda r=record: self.load_record_data(r)
            ).grid(row=0, column=1, sticky="e", padx=10, pady= 5)

    def load_record_data(self, record):
        """Carga los datos de un registro en el formulario"""
        self.current_record = record
        self.form_title.configure(
            text=f"Editando Registro #{record['id_historial']}"
        )
        self.delete_btn.configure(state="normal")
        
        field_mapping = {
            "id": str(record.get("id_historial", "")),
            "student_id": str(record.get("id_estudiante", "")),
            "course_id": str(record.get("id_curso", "")),
            "grade": str(record.get("calificacion", "")) if record.get("calificacion") is not None else "",
            "start_date": record.get("fecha_inicio", ""),
            "end_date": record.get("fecha_fin", "") if record.get("fecha_fin") else "",
            "period": record.get("periodo", "") if record.get("periodo") else "",
            "status": record.get("estado", "En curso")
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
                widget.set("En curso")
        
        # Establecer fecha actual como valor por defecto para fecha inicio
        self.form_widgets["start_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.current_record = None
        self.form_title.configure(text="Nuevo Registro")
        self.delete_btn.configure(state="disabled")
    
    def validate_form(self):
        """Valida los campos del formulario"""
        errors = []
        
        required_fields = ["student_id", "course_id", "start_date", "status"]
        for field in required_fields:
            widget = self.form_widgets[field]
            value = widget.get() if hasattr(widget, 'get') else ""
            if not value.strip():
                field_name = field.replace("_", " ").title()
                errors.append(f"El campo {field_name} es obligatorio")
        
        # Validar que los IDs sean numéricos
        try:
            int(self.form_widgets["student_id"].get())
            int(self.form_widgets["course_id"].get())
        except ValueError:
            errors.append("Los IDs de estudiante y curso deben ser números")
        
        # Validar formato de fechas
        date_fields = ["start_date", "end_date"]
        for field in date_fields:
            date_str = self.form_widgets[field].get().strip()
            if date_str:
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    errors.append(f"La fecha {field.replace('_', ' ').title()} debe estar en formato YYYY-MM-DD")
        
        # Validar calificación si existe
        grade = self.form_widgets["grade"].get().strip()
        if grade:
            try:
                grade_num = float(grade)
                if not (0 <= grade_num <= 10):
                    errors.append("La calificación debe estar entre 0 y 10")
            except ValueError:
                errors.append("La calificación debe ser un número válido")
        
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return False
        return True
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {
            "id_estudiante": int(self.form_widgets["student_id"].get()),
            "id_curso": int(self.form_widgets["course_id"].get()),
            "calificacion": float(self.form_widgets["grade"].get()) if self.form_widgets["grade"].get().strip() else None,
            "fecha_inicio": self.form_widgets["start_date"].get().strip(),
            "fecha_fin": self.form_widgets["end_date"].get().strip() or None,
            "periodo": self.form_widgets["period"].get().strip() or None,
            "estado": self.form_widgets["status"].get()
        }
        
        if self.current_record:
            data["id_historial"] = self.current_record["id_historial"]
        
        return data
    
    def search_records(self):
        """Busca registros según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_records_list()
            return
        
        records = self.get_records_from_db()
        filtered = [
            r for r in records
            if (search_term in str(r['id_estudiante']).lower() or
               search_term in str(r['id_curso']).lower() or
               search_term in r['estado'].lower() or
               search_term in (r['periodo'] or "").lower())
        ]
        
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for record in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = (f"Estudiante #{record['id_estudiante']} - Curso #{record['id_curso']} "
                   f"- {record['estado']} - Calif: {record['calificacion'] or 'N/A'}")
            
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda r=record: self.load_record_data(r)
            ).pack(side="right", padx=2)
        
        self.record_count_label.configure(text=f"Registros ({len(filtered)} encontrados)")
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, "end")
        self.update_records_list()
    
    def new_record(self):
        """Prepara el formulario para nuevo registro"""
        self.clear_form()
    
    def save_record(self):
        """Guarda los datos del registro"""
        if not self.validate_form():
            return
        
        record_data = self.get_form_data()
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_record:
                # Actualizar registro existente
                query = """UPDATE historial_academico SET 
                          id_estudiante = %s,
                          id_curso = %s,
                          calificacion = %s,
                          fecha_inicio = %s,
                          fecha_fin = %s,
                          periodo = %s,
                          estado = %s
                          WHERE id_historial = %s"""
                params = (
                    record_data['id_estudiante'],
                    record_data['id_curso'],
                    record_data['calificacion'],
                    record_data['fecha_inicio'],
                    record_data['fecha_fin'],
                    record_data['periodo'],
                    record_data['estado'],
                    record_data['id_historial']
                )
                action = "actualizado"
            else:
                # Crear nuevo registro
                query = """INSERT INTO historial_academico (
                          id_estudiante, id_curso, calificacion,
                          fecha_inicio, fecha_fin, periodo, estado
                          ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                params = (
                    record_data['id_estudiante'],
                    record_data['id_curso'],
                    record_data['calificacion'],
                    record_data['fecha_inicio'],
                    record_data['fecha_fin'],
                    record_data['periodo'],
                    record_data['estado']
                )
                action = "registrado"
            
            cursor.execute(query, params)
            conn.commit()
            
            messagebox.showinfo("Éxito", f"Registro {action} correctamente")
            self.update_records_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar registro:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_record(self):
        """Elimina el registro actual"""
        if not self.current_record:
            return
            
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar este registro?\n\n"
            f"Estudiante: #{self.current_record['id_estudiante']}\n"
            f"Curso: #{self.current_record['id_curso']}\n"
            f"Estado: {self.current_record['estado']}",
            icon="warning"
        )
        
        if not confirmacion:
            return
            
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM historial_academico WHERE id_historial = %s",
                (self.current_record['id_historial'],)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Registro eliminado correctamente")
                self.update_records_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el registro")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar registro:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()

    def get_records_from_db(self):
        """Obtiene todos los registros de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = '''
                SELECT h.*, 
                CONCAT(e.nombre, ' ', e.appat, ' ', e.apmat) AS nombre_estudiante,
                c.nombre_curso
                FROM historial_academico h
                LEFT JOIN estudiantes e ON h.id_estudiante = e.id_estudiante
                LEFT JOIN cursos c ON h.id_curso = c.id_curso
                ORDER BY h.fecha_inicio DESC
            '''
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar registros:\n{str(e)}")
            return []
        finally:
            if conn:
                conn.close()