import customtkinter as ctk
from tkinter import messagebox

class UserManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_user = None
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._create_ui()
        
    def _create_ui(self):
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
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
        
        self._create_users_list()
        self._create_form()
        
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Listo",
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_users_list(self):
        self.list_frame = ctk.CTkFrame(self.main_frame, width=400)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
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
        
        self.list_scroll = ctk.CTkScrollableFrame(
            self.list_frame,
            height=550
        )
        self.list_scroll.pack(fill="both", expand=True)
    
    def _create_form(self):
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")
        
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Nuevo Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))
        
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
        if entry.cget("show") == "":
            entry.configure(show="•")
        else:
            entry.configure(show="")
    
    def return_to_menu(self):
        self.root.destroy()
    
    def search_users(self):
        pass
    
    def clear_search(self):
        pass
    
    def new_user(self):
        pass
    
    def save_user(self):
        pass
    
    def delete_user(self):
        pass
    
    def cancel_edit(self):
        pass
    
    def clear_form(self):
        pass

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Gestión de Usuarios")
    root.geometry("1000x700")
    
    class AppManager:
        def show_menu(self, user):
            root.destroy()
    
    app_manager = AppManager()
    UserManagementWindow(root, app_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()