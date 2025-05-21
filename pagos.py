import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from conn import get_connection
import re

class PaymentManagementWindow:
    def __init__(self, root, app_manager):
        self.root = root
        self.app = app_manager
        self.current_payment = None
        
        self._create_ui()
        self.update_payments_list()
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
        
        ctk.CTkLabel(search_frame, text="Buscar Pagos:").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, width=300,
            placeholder_text="Membresía, referencia o estado..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_payments())
        
        ctk.CTkButton(
            search_frame, text="Buscar", command=self.search_payments, width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame, text="Limpiar", command=self.clear_search, width=100
        ).pack(side="left")
        
        # Lista de pagos
        self._create_payments_list()
        
        # Formulario de edición
        self._create_form()
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(self.main_frame, text="Listo", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _create_payments_list(self):
        """Crea el panel de lista de pagos con mejor visualización"""
        self.list_frame = ctk.CTkFrame(self.main_frame, width=450)  # Aumentado para mejor visualización
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_propagate(False)
        
        header_frame = ctk.CTkFrame(self.list_frame)
        header_frame.pack(fill="x")
        
        self.payment_count_label = ctk.CTkLabel(
            header_frame, text="Pagos (0)", font=ctk.CTkFont(weight="bold")
        )
        self.payment_count_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_frame, text="+ Nuevo", width=80, command=self.new_payment
        ).pack(side="right")
        
        # Lista con scroll - más ancha para mejor visualización
        self.list_scroll = ctk.CTkScrollableFrame(
            self.list_frame,
            height=550,
            width=440
        )
        self.list_scroll.pack(fill="both", expand=True)
    
    def _create_form(self):
        """Crea el formulario de edición con los campos de la tabla pagos"""
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")

        self.form_title = ctk.CTkLabel(
            self.form_frame, text="Nuevo Pago", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.pack(pady=(0, 20))

        fields = [
            {"label": "ID Membresía*", "name": "membership_id"},
            {"label": "Fecha Pago*", "name": "payment_date", "placeholder": "AAAA-MM-DD"},
            {"label": "Monto*", "name": "amount"},
            {"label": "Método Pago*", "name": "payment_method", "type": "combobox", 
             "values": ["Efectivo", "Transferencia", "Tarjeta", "Beca"]},
            {"label": "Referencia", "name": "reference"},
            {"label": "Periodo Cubierto", "name": "covered_period"},
            {"label": "Estado*", "name": "status", "type": "combobox",
             "values": ["Completo", "Pendiente", "Rechazado", "Reembolsado"]},
            {"label": "Notas", "name": "notes", "type": "textbox"}
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
                if field["name"] == "payment_method":
                    widget.set("Efectivo")
                elif field["name"] == "status":
                    widget.set("Pendiente")
            elif field.get("type") == "textbox":
                widget = ctk.CTkTextbox(frame, height=60)
                widget.pack(side="right", fill="x", expand=True)
            else:
                widget = ctk.CTkEntry(frame)
                if field.get("placeholder"):
                    widget.configure(placeholder_text=field["placeholder"])
                widget.pack(side="right", fill="x", expand=True)
                
                if field["name"] == "payment_date":
                    widget.insert(0, datetime.now().strftime("%Y-%m-%d"))

            self.form_widgets[field["name"]] = widget

        # Botones de acción
        button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            button_frame, text="Guardar", command=self.save_payment, fg_color="#28a745"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame, text="Cancelar", command=self.cancel_edit
        ).pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(
            button_frame, text="Eliminar", command=self.delete_payment,
            fg_color="#dc3545", state="disabled"
        )
        self.delete_btn.pack(side="right")
    
    def return_to_menu(self):
        self.app.show_menu(self.app.current_user)
    
    def update_payments_list(self):
        """Actualiza la lista de pagos con mejor visualización de botones"""
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        self.payments_data = self.get_payments_from_db()
        self.payment_count_label.configure(text=f"Pagos ({len(self.payments_data)})")
        
        if not self.payments_data:
            ctk.CTkLabel(
                self.list_scroll, text="No se encontraron pagos", text_color="gray"
            ).pack(pady=20)
            return
        
        for payment in self.payments_data:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2, padx=2)
            
            # Usamos grid para mejor control del espacio
            frame.grid_columnconfigure(0, weight=3)  # Más espacio para la info
            frame.grid_columnconfigure(1, weight=1)  # Menos espacio para el botón
            
            # Texto del pago
            text = (f"Membresía #{payment['id_membresia']} - ${payment['monto']:.2f} "
                   f"({payment['metodo_pago']}) - {payment['estado_pago']}")
            
            label = ctk.CTkLabel(
                frame,
                text=text,
                anchor="w",
                wraplength=300  # Permite ajuste de texto
            )
            label.grid(row=0, column=0, sticky="ew", padx=(5, 0))
            
            # Botón Editar - más visible
            edit_btn = ctk.CTkButton(
                frame,
                text="Editar",
                width=70,
                command=lambda p=payment: self.load_payment_data(p),
                fg_color="#0d6efd",  # Azul más llamativo
                hover_color="#0b5ed7"
            )
            edit_btn.grid(row=0, column=1, sticky="e", padx=(0, 5))
    
    def load_payment_data(self, payment):
        """Carga los datos de un pago en el formulario"""
        self.current_payment = payment
        self.form_title.configure(text=f"Editando Pago #{payment['id_pago']}")
        self.delete_btn.configure(state="normal")
        
        field_mapping = {
            "membership_id": str(payment.get("id_membresia", "")),
            "payment_date": payment.get("fecha_pago", ""),
            "amount": f"{payment.get('monto', 0):.2f}",
            "payment_method": payment.get("metodo_pago", "Efectivo"),
            "reference": payment.get("referencia_pago", ""),
            "covered_period": payment.get("periodo_cubierto", ""),
            "status": payment.get("estado_pago", "Pendiente"),
            "notes": payment.get("notas", "")
        }

        for field_name, value in field_mapping.items():
            widget = self.form_widgets[field_name]
            
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                widget.insert(0, value)
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(value)
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
                widget.insert("1.0", value)
    
    def clear_form(self):
        """Limpia el formulario"""
        for widget in self.form_widgets.values():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
        
        self.current_payment = None
        self.form_title.configure(text="Nuevo Pago")
        self.delete_btn.configure(state="disabled")
        self.form_widgets["payment_method"].set("Efectivo")
        self.form_widgets["status"].set("Pendiente")
        self.form_widgets["payment_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def validate_form(self):
        """Valida los campos del formulario"""
        errors = []

        required_fields = ["membership_id", "payment_date", "amount", "payment_method", "status"]
        for field in required_fields:
            widget = self.form_widgets[field]
            value = widget.get() if hasattr(widget, 'get') else ""
            if not value.strip():
                field_name = field.replace("_", " ").title()
                errors.append(f"El campo {field_name} es obligatorio")

        # Validar ID de membresía como número
        membership_id = self.form_widgets["membership_id"].get().strip()
        if membership_id and not membership_id.isdigit():
            errors.append("El ID de membresía debe ser un número")

        # Validar fecha
        payment_date = self.form_widgets["payment_date"].get().strip()
        try:
            if payment_date:
                datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            errors.append("La fecha debe estar en formato AAAA-MM-DD")

        # Validar monto como número
        amount = self.form_widgets["amount"].get().strip()
        try:
            if amount:
                float(amount)
        except ValueError:
            errors.append("El monto debe ser un valor numérico")

        return errors if errors else None
    
    def get_form_data(self):
        """Obtiene los datos del formulario en un diccionario"""
        data = {}
        
        data["id_membresia"] = int(self.form_widgets["membership_id"].get().strip())
        data["fecha_pago"] = self.form_widgets["payment_date"].get().strip()
        data["monto"] = float(self.form_widgets["amount"].get().strip())
        data["metodo_pago"] = self.form_widgets["payment_method"].get()
        
        reference = self.form_widgets["reference"].get().strip()
        data["referencia_pago"] = reference if reference else None
        
        covered_period = self.form_widgets["covered_period"].get().strip()
        data["periodo_cubierto"] = covered_period if covered_period else None
        
        data["estado_pago"] = self.form_widgets["status"].get()
        
        notes = self.form_widgets["notes"].get("1.0", "end-1c").strip()
        data["notas"] = notes if notes else None
        
        return data
    
    def save_payment(self):
        """Guarda los datos del pago"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Errores en el formulario", "\n".join(errors))
            return
        
        payment_data = self.get_form_data()
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if self.current_payment:
                # Actualizar pago existente
                payment_data["id_pago"] = self.current_payment["id_pago"]
                cursor.execute("""
                    UPDATE pagos SET
                    id_membresia=%s, fecha_pago=%s, monto=%s,
                    metodo_pago=%s, referencia_pago=%s, periodo_cubierto=%s,
                    estado_pago=%s, notas=%s
                    WHERE id_pago=%s
                """, (
                    payment_data["id_membresia"],
                    payment_data["fecha_pago"],
                    payment_data["monto"],
                    payment_data["metodo_pago"],
                    payment_data["referencia_pago"],
                    payment_data["periodo_cubierto"],
                    payment_data["estado_pago"],
                    payment_data["notas"],
                    payment_data["id_pago"]
                ))
                action = "actualizado"
            else:
                # Crear nuevo pago
                cursor.execute("""
                    INSERT INTO pagos (
                        id_membresia, fecha_pago, monto,
                        metodo_pago, referencia_pago, periodo_cubierto,
                        estado_pago, notas
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    payment_data["id_membresia"],
                    payment_data["fecha_pago"],
                    payment_data["monto"],
                    payment_data["metodo_pago"],
                    payment_data["referencia_pago"],
                    payment_data["periodo_cubierto"],
                    payment_data["estado_pago"],
                    payment_data["notas"]
                ))
                action = "registrado"
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Pago {action} correctamente")
            self.update_payments_list()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el pago: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def delete_payment(self):
        """Elimina el pago actual"""
        if not self.current_payment:
            return
            
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar este pago?\n\n"
            f"Membresía: #{self.current_payment['id_membresia']}\n"
            f"Monto: ${self.current_payment['monto']:.2f}\n"
            f"Fecha: {self.current_payment['fecha_pago']}",
            icon="warning"
        )
        
        if confirm:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM pagos WHERE id_pago = %s",
                    (self.current_payment["id_pago"],)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    messagebox.showinfo("Éxito", "Pago eliminado correctamente")
                    self.update_payments_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el pago")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar pago: {str(e)}")
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()
    
    def search_payments(self):
        """Busca pagos según el criterio"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_payments_list()
            return
        
        all_payments = self.get_payments_from_db()
        
        filtered = [
            p for p in all_payments
            if (search_term in str(p.get("id_membresia", "")).lower() or
                search_term in (p.get("referencia_pago", "") or "").lower() or
                search_term in p.get("estado_pago", "").lower() or
                search_term in p.get("metodo_pago", "").lower())
        ]
        
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        for payment in filtered:
            frame = ctk.CTkFrame(self.list_scroll, height=45)
            frame.pack(fill="x", pady=2, padx=2)
            
            frame.grid_columnconfigure(0, weight=3)
            frame.grid_columnconfigure(1, weight=1)
            
            text = (f"Membresía #{payment['id_membresia']} - ${payment['monto']:.2f} "
                   f"({payment['metodo_pago']}) - {payment['estado_pago']}")
            
            label = ctk.CTkLabel(
                frame,
                text=text,
                anchor="w",
                wraplength=300
            )
            label.grid(row=0, column=0, sticky="ew", padx=(5, 0))
            
            edit_btn = ctk.CTkButton(
                frame,
                text="Editar",
                width=70,
                command=lambda p=payment: self.load_payment_data(p),
                fg_color="#0d6efd",
                hover_color="#0b5ed7"
            )
            edit_btn.grid(row=0, column=1, sticky="e", padx=(0, 5))
        
        self.payment_count_label.configure(text=f"Pagos ({len(filtered)} encontrados)")
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, "end")
        self.update_payments_list()
    
    def new_payment(self):
        """Prepara el formulario para nuevo pago"""
        self.clear_form()
    
    def cancel_edit(self):
        """Cancela la edición actual"""
        self.clear_form()

    # ======================
    # MÉTODOS DE BASE DE DATOS
    # ======================

    def get_payments_from_db(self):
        """Obtiene todos los pagos de la base de datos"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.id_pago, p.id_membresia, p.fecha_pago, p.monto,
                       p.metodo_pago, p.referencia_pago, p.periodo_cubierto,
                       p.estado_pago, p.notas
                FROM pagos p
                ORDER BY p.fecha_pago DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pagos: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()