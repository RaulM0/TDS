import customtkinter as ctk
from tkinter import messagebox
from conn import get_connection

class CourseManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_course = None
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Construir interfaz
        self._create_ui()
        
        # Cargar datos iniciales
        self.update_courses_list()

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
        
        ctk.CTkLabel(search_frame, text="Buscar Cursos:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Código, nombre o departamento..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_courses())
        
        ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self.search_courses,
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="Limpiar",
            command=self.clear_search,
            width=100
        ).pack(side="left")
        
        # Lista de cursos
        self._create_courses_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Listo",
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_courses_list(self):
        """Crea el panel de lista de cursos"""
        self.list_frame = ctk.CTkFrame(self.main_frame, width=400)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        # Cabecera
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.course_count_label = ctk.CTkLabel(
            header_frame,
            text="Cursos (0)",
            font=ctk.CTkFont(weight="bold")
        )
        self.course_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame,
            text="+ Nuevo",
            width=80,
            command=self.new_course
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
            text="Nuevo Curso",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))
        
        # Campos del formulario según la tabla cursos
        fields = [
            {"label": "ID Curso", "name": "id", "editable": False},
            {"label": "Código Curso*", "name": "code"},
            {"label": "Nombre Curso*", "name": "name"},
            {"label": "Créditos", "name": "credits"},
            {"label": "Departamento", "name": "department"},
            {"label": "Descripción", "name": "description", "type": "textbox"}
        ]
        
        self.form_widgets = {}
        
        for field in fields:
            frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            label_text = field["label"].replace("*", "") + (" *" if "*" in field["label"] else "")
            ctk.CTkLabel(frame, text=label_text, width=120).pack(side="left")
            
            if field.get("type") == "textbox":
                widget = ctk.CTkTextbox(frame, height=80)
                widget.pack(side="right", fill="x", expand=True)
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
            command=self.save_course,
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
            command=self.delete_course,
            fg_color="#dc3545",
            state="disabled"
        )
        self.delete_btn.pack(side="right")
    
    def return_to_menu(self):
        """Regresa al menú principal"""
        self.app.show_menu(self.app.current_user)
    
    def update_courses_list(self):
        """Actualiza la lista de cursos"""
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        courses = self.get_courses_from_db()
        self.course_count_label.configure(text=f"Cursos ({len(courses)})")
        
        if not courses:
            ctk.CTkLabel(
                self.list_scroll,
                text="No se encontraron cursos",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for course in courses:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=5)

            frame.grid_columnconfigure(0, weight=1)
            
            # Formatear información para mostrar
            text = f"{course['codigo_curso']} - {course['nombre_curso']}"
            if course['creditos']:
                text += f" ({course['creditos']} créditos)"
            
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).grid(row=0, column=0, padx=10,pady=5, sticky="w")
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda c=course: self.load_course_data(c)
            ).grid(row=0, column=1, sticky="e", padx=10)
    
    def load_course_data(self, course):
        """Carga los datos de un curso en el formulario"""
        self.current_course = course
        self.form_title.configure(
            text=f"Editando Curso #{course['id_curso']}"
        )
        self.delete_btn.configure(state="normal")
        
        field_mapping = {
            "id": str(course.get("id_curso", "")),
            "code": course.get("codigo_curso", ""),
            "name": course.get("nombre_curso", ""),
            "credits": str(course.get("creditos", "")) if course.get("creditos") is not None else "",
            "department": course.get("departamento", "") if course.get("departamento") else "",
            "description": course.get("descripcion", "") if course.get("descripcion") else ""
        }
        
        for field_name, value in field_mapping.items():
            widget = self.form_widgets[field_name]
            
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state="normal")
                widget.delete(0, "end")
                widget.insert(0, value)
                if field_name == "id":
                    widget.configure(state="disabled")
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
                widget.insert("1.0", value)
    
    def clear_form(self):
        """Limpia el formulario"""
        for field_name, widget in self.form_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state="normal")
                widget.delete(0, "end")
                if field_name == "id":
                    widget.configure(state="disabled")
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
        
        self.current_course = None
        self.form_title.configure(text="Nuevo Curso")
        self.delete_btn.configure(state="disabled")
    
    def validate_form(self):
        """Valida los campos del formulario"""
        errors = []
        
        required_fields = ["code", "name"]
        for field in required_fields:
            widget = self.form_widgets[field]
            value = widget.get().strip()
            if not value:
                field_name = field.replace("_", " ").title()
                errors.append(f"El campo {field_name} es obligatorio")
        
        # Validar que créditos sea numérico si existe
        credits = self.form_widgets["credits"].get().strip()
        if credits:
            try:
                int(credits)
            except ValueError:
                errors.append("Los créditos deben ser un número entero")
        
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return False
        return True
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {
            "codigo_curso": self.form_widgets["code"].get().strip(),
            "nombre_curso": self.form_widgets["name"].get().strip(),
            "descripcion": self.form_widgets["description"].get("1.0", "end-1c").strip() or None,
            "creditos": int(self.form_widgets["credits"].get()) if self.form_widgets["credits"].get().strip() else None,
            "departamento": self.form_widgets["department"].get().strip() or None
        }
        
        if self.current_course:
            data["id_curso"] = self.current_course["id_curso"]
        
        return data
    
    def search_courses(self):
        """Busca cursos según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_courses_list()
            return
        
        courses = self.get_courses_from_db()
        filtered = [
            c for c in courses
            if (search_term in c['codigo_curso'].lower() or
               search_term in c['nombre_curso'].lower() or
               search_term in (c['departamento'] or "").lower())
        ]
        
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for course in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2)
            
            text = f"{course['codigo_curso']} - {course['nombre_curso']}"
            if course['creditos']:
                text += f" ({course['creditos']} créditos)"
            
            ctk.CTkLabel(
                frame,
                text=text,
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                frame,
                text="Editar",
                width=60,
                command=lambda c=course: self.load_course_data(c)
            ).pack(side="right", padx=2)
        
        self.course_count_label.configure(text=f"Cursos ({len(filtered)} encontrados)")
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, "end")
        self.update_courses_list()
    
    def new_course(self):
        """Prepara el formulario para nuevo curso"""
        self.clear_form()
    
    def save_course(self):
        """Guarda los datos del curso"""
        if not self.validate_form():
            return
        
        course_data = self.get_form_data()
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_course:
                # Actualizar curso existente
                query = """UPDATE cursos SET 
                          codigo_curso = %s,
                          nombre_curso = %s,
                          descripcion = %s,
                          creditos = %s,
                          departamento = %s
                          WHERE id_curso = %s"""
                params = (
                    course_data['codigo_curso'],
                    course_data['nombre_curso'],
                    course_data['descripcion'],
                    course_data['creditos'],
                    course_data['departamento'],
                    course_data['id_curso']
                )
                action = "actualizado"
            else:
                # Crear nuevo curso
                query = """INSERT INTO cursos (
                          codigo_curso, nombre_curso, descripcion,
                          creditos, departamento
                          ) VALUES (%s, %s, %s, %s, %s)"""
                params = (
                    course_data['codigo_curso'],
                    course_data['nombre_curso'],
                    course_data['descripcion'],
                    course_data['creditos'],
                    course_data['departamento']
                )
                action = "registrado"
            
            cursor.execute(query, params)
            conn.commit()
            
            messagebox.showinfo("Éxito", f"Curso {action} correctamente")
            self.update_courses_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar curso:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_course(self):
        """Elimina el curso actual"""
        if not self.current_course:
            return
            
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar este curso?\n\n"
            f"Código: {self.current_course['codigo_curso']}\n"
            f"Nombre: {self.current_course['nombre_curso']}",
            icon="warning"
        )
        
        if not confirmacion:
            return
            
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM cursos WHERE id_curso = %s",
                (self.current_course['id_curso'],)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Curso eliminado correctamente")
                self.update_courses_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el curso")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar curso:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()

    def get_courses_from_db(self):
        """Obtiene todos los cursos de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = '''
                SELECT * FROM cursos
                ORDER BY nombre_curso
            '''
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar cursos:\n{str(e)}")
            return []
        finally:
            if conn:
                conn.close()