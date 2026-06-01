import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ==================== Configuración de estados ====================
ESTADOS = {
    "Libre":   {"bg": "#e8f5e9", "fg": "#2e7d32", "indicador": "●", "texto": "Libre"},
    "Ocupado": {"bg": "#ffebee", "fg": "#c62828", "indicador": "●", "texto": "Ocupado"},
    "Ausente": {"bg": "#fff8e1", "fg": "#f57f17", "indicador": "●", "texto": "Ausente"},
}


# ==================== Ventana Secundaria de Turnos ====================
class PantallaTurnos:
    def __init__(self, root):
        self.win = tk.Toplevel(root)
        self.win.title("SCA SSUAS - Pantalla de Turnos")
        self.win.configure(bg="#003087")
        self.win.geometry("800x500")
        self.win.resizable(True, True)

        self.win.bind("<F11>", self._toggle_fullscreen)
        self.win.bind("<Escape>", self._exit_fullscreen)
        self._fullscreen = False

        self._build_ui()

    def _toggle_fullscreen(self, event=None):
        self._fullscreen = not self._fullscreen
        self.win.attributes("-fullscreen", self._fullscreen)

    def _exit_fullscreen(self, event=None):
        self._fullscreen = False
        self.win.attributes("-fullscreen", False)

    def _build_ui(self):
        header = tk.Frame(self.win, bg="#003087")
        header.pack(fill="x", pady=(20, 0))
        tk.Label(header, text="SCA  •  SS UAS", bg="#003087", fg="white",
                 font=("Arial", 18, "bold")).pack()
        tk.Label(header, text="Sistema de Control de Atención", bg="#003087",
                 fg="#90caf9", font=("Arial", 11)).pack()

        turno_frame = tk.Frame(self.win, bg="#1565c0")
        turno_frame.pack(fill="x", padx=40, pady=20)

        tk.Label(turno_frame, text="TURNO EN ATENCIÓN",
                 bg="#1565c0", fg="#90caf9", font=("Arial", 13, "bold")).pack(pady=(15, 0))

        self.lbl_turno_actual = tk.Label(
            turno_frame, text="---",
            bg="#1565c0", fg="white", font=("Arial", 72, "bold")
        )
        self.lbl_turno_actual.pack()

        self.lbl_nombre_actual = tk.Label(
            turno_frame, text="En espera de primer turno",
            bg="#1565c0", fg="#e3f2fd", font=("Arial", 16)
        )
        self.lbl_nombre_actual.pack()

        self.lbl_asesor_actual = tk.Label(
            turno_frame, text="",
            bg="#1565c0", fg="#90caf9", font=("Arial", 12, "italic")
        )
        self.lbl_asesor_actual.pack(pady=(0, 15))

        sig_frame = tk.Frame(self.win, bg="#003087")
        sig_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        tk.Label(sig_frame, text="PRÓXIMOS TURNOS",
                 bg="#003087", fg="#90caf9", font=("Arial", 11, "bold")).pack(anchor="w")

        self.frame_siguientes = tk.Frame(sig_frame, bg="#003087")
        self.frame_siguientes.pack(fill="x", pady=5)

        self.lbl_hora = tk.Label(self.win, text="", bg="#003087",
                                 fg="#546e7a", font=("Arial", 10))
        self.lbl_hora.pack(pady=(0, 4))
        self._actualizar_hora()

        tk.Label(self.win, text="F11 — Pantalla completa  |  Esc — Salir",
                 bg="#003087", fg="#37474f", font=("Arial", 8)).pack()

    def _actualizar_hora(self):
        self.lbl_hora.config(text=datetime.now().strftime("%A %d de %B  •  %H:%M:%S"))
        self.win.after(1000, self._actualizar_hora)

    def actualizar(self, turno_actual, siguientes):
        if turno_actual:
            self.lbl_turno_actual.config(text=turno_actual["turno"])
            self.lbl_nombre_actual.config(text=turno_actual["alumno"])
            self.lbl_asesor_actual.config(text=f"Asesor: {turno_actual['asesor']}")
        else:
            self.lbl_turno_actual.config(text="---")
            self.lbl_nombre_actual.config(text="En espera de primer turno")
            self.lbl_asesor_actual.config(text="")

        for w in self.frame_siguientes.winfo_children():
            w.destroy()

        if not siguientes:
            tk.Label(self.frame_siguientes, text="No hay más turnos en espera.",
                     bg="#003087", fg="#546e7a", font=("Arial", 10, "italic")).pack(anchor="w")
            return

        for item in siguientes[:4]:
            card = tk.Frame(self.frame_siguientes, bg="#01579b", padx=12, pady=6)
            card.pack(side="left", padx=6)
            tk.Label(card, text=item["turno"], bg="#01579b",
                     fg="white", font=("Arial", 18, "bold")).pack()
            tk.Label(card, text=item["alumno"], bg="#01579b",
                     fg="#b3e5fc", font=("Arial", 9)).pack()


# ==================== Ventanas de Gestión ====================
class VentanaGestionAsesores:
    def __init__(self, app_ref, mysql_disponible):
        self.app_ref = app_ref
        self.mysql = mysql_disponible
        self.win = tk.Toplevel(app_ref.root)
        self.win.title("Gestión de Asesores")
        self.win.geometry("550x450")
        self.win.resizable(False, False)
        self.win.configure(bg="white")
        self.win.transient(app_ref.root)
        self.win.grab_set()

        self._build_ui()
        self._cargar_asesores()
        self._cargar_cubiculos_disponibles()

    def _build_ui(self):
        tk.Label(self.win, text="GESTIÓN DE ASESORES", font=("Arial", 14, "bold"),
                 bg="white").pack(pady=10)

        columns = ("Asesor", "Cubículo")
        self.tree = ttk.Treeview(self.win, columns=columns, show="headings", height=8)
        self.tree.heading("Asesor", text="Asesor")
        self.tree.heading("Cubículo", text="Cubículo Asignado")
        self.tree.column("Asesor", width=240, anchor="w")
        self.tree.column("Cubículo", width=240, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=5)

        add_frame = tk.LabelFrame(self.win, text="Agregar Nuevo Asesor",
                                  font=("Arial", 10, "bold"), bg="white",
                                  fg="#003087", padx=10, pady=10)
        add_frame.pack(fill="x", padx=15, pady=(10, 5))

        row_frame = tk.Frame(add_frame, bg="white")
        row_frame.pack(fill="x")

        tk.Label(row_frame, text="Nombre:", bg="white", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.nombre_entry = ttk.Entry(row_frame, width=24, font=("Arial", 10))
        self.nombre_entry.pack(side="left", padx=(0, 10))

        tk.Label(row_frame, text="Cubículo:", bg="white", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.cubiculo_combo = ttk.Combobox(row_frame, values=["(Primero disponible)"],
                                           state="readonly", width=18, font=("Arial", 10))
        self.cubiculo_combo.pack(side="left", padx=(0, 10))
        self.cubiculo_combo.set("(Primero disponible)")

        ttk.Button(row_frame, text="Agregar", command=self._agregar).pack(side="left")

        tk.Label(add_frame, text="Deja \"(Primero disponible)\" para asignar el primer cubículo libre automáticamente.",
                 bg="white", fg="#666", font=("Arial", 8)).pack(anchor="w", pady=(5, 0))

        btn_frame = tk.Frame(self.win, bg="white")
        btn_frame.pack(fill="x", padx=15, pady=(10, 15))

        ttk.Button(btn_frame, text="Reasignar Cubículo", command=self._cambiar_cubiculo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar Asesor", command=self._eliminar).pack(side="left", padx=5)

    def _cargar_asesores(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if self.mysql:
            from db import obtener_asesores
            for asesor in obtener_asesores():
                cub = asesor["cubiculo"] if asesor["cubiculo"] else "Sin asignar"
                self.tree.insert("", "end", values=(asesor["nombre"], cub))

    def _cargar_cubiculos_disponibles(self):
        if not self.mysql:
            self.cubiculo_combo["values"] = ["(Primero disponible)"]
            return
        from db import obtener_cubiculos_disponibles
        disp = obtener_cubiculos_disponibles()
        if disp:
            opciones = ["(Primero disponible)"] + [f"{c[0]}  —  {c[1]}" for c in disp]
        else:
            opciones = ["(Primero disponible)"]
        self.cubiculo_combo["values"] = opciones
        self.cubiculo_combo.set("(Primero disponible)")

    def _agregar(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Nombre requerido", "Ingresa el nombre del asesor.", parent=self.win)
            return
        nombre = nombre.strip().title()

        seleccion = self.cubiculo_combo.get()
        cubiculo_id = None
        if seleccion and seleccion != "(Primero disponible)":
            cubiculo_id = seleccion.split("  —  ")[0].strip()

        if self.mysql:
            from db import insertar_asesor
            if insertar_asesor(nombre, cubiculo_id):
                self._cargar_asesores()
                self._cargar_cubiculos_disponibles()
                self.app_ref._refrescar_asesores()
                self.app_ref._refrescar_cubiculos_db()
                self.nombre_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Error", "El asesor ya existe.", parent=self.win)
        else:
            messagebox.showinfo("Modo Local", "Conecta MySQL para gestionar asesores.", parent=self.win)

    def _eliminar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un asesor de la tabla.", parent=self.win)
            return
        nombre = self.tree.item(seleccion[0], "values")[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar asesor '{nombre}'?", parent=self.win):
            if self.mysql:
                from db import eliminar_asesor
                eliminar_asesor(nombre)
                self._cargar_asesores()
                self._cargar_cubiculos_disponibles()
                self.app_ref._refrescar_asesores()
                self.app_ref._refrescar_cubiculos_db()

    def _cambiar_cubiculo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un asesor de la tabla.", parent=self.win)
            return
        nombre = self.tree.item(seleccion[0], "values")[0]

        from db import obtener_cubiculos_disponibles
        disp = obtener_cubiculos_disponibles()
        if not disp:
            messagebox.showinfo("Sin opciones", "No hay cubículos disponibles.", parent=self.win)
            return

        dialog = tk.Toplevel(self.win)
        dialog.title(f"Asignar Cubículo")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(self.win)
        dialog.grab_set()

        tk.Label(dialog, text="Reasignar cubículo para:",
                 font=("Arial", 10), bg="white", fg="#666").pack(pady=(15, 0))
        tk.Label(dialog, text=nombre,
                 font=("Arial", 13, "bold"), bg="white", fg="#003087").pack()

        combo_frame = tk.Frame(dialog, bg="white")
        combo_frame.pack(pady=15)

        tk.Label(combo_frame, text="Nuevo cubículo:",
                 bg="white", font=("Arial", 10)).pack(side="left", padx=(0, 8))

        opciones = [f"{c[0]}  —  {c[1]}" for c in disp]
        ids = [c[0] for c in disp]
        combo_var = tk.StringVar()
        combo = ttk.Combobox(combo_frame, textvariable=combo_var,
                             values=opciones, state="readonly", width=24, font=("Arial", 10))
        combo.pack(side="left")
        if opciones:
            combo.current(0)

        def confirmar():
            idx = combo.current()
            if idx >= 0:
                cub_id = ids[idx]
                from db import actualizar_asesor_cubiculo
                actualizar_asesor_cubiculo(cub_id, nombre)
                self._cargar_asesores()
                self._cargar_cubiculos_disponibles()
                self.app_ref._refrescar_cubiculos_db()
                dialog.destroy()

        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(pady=(0, 15))
        ttk.Button(btn_frame, text="Asignar", command=confirmar).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=8)


class VentanaGestionCubiculos:
    def __init__(self, app_ref, mysql_disponible):
        self.app_ref = app_ref
        self.mysql = mysql_disponible
        self.win = tk.Toplevel(app_ref.root)
        self.win.title("Gestión de Cubículos")
        self.win.geometry("500x400")
        self.win.resizable(False, False)
        self.win.configure(bg="white")
        self.win.transient(app_ref.root)
        self.win.grab_set()

        self._build_ui()
        self._cargar_cubiculos()

    def _build_ui(self):
        tk.Label(self.win, text="GESTIÓN DE CUBÍCULOS", font=("Arial", 14, "bold"),
                 bg="white").pack(pady=10)

        columns = ("Cubículo", "Asesor", "Estado")
        self.tree = ttk.Treeview(self.win, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=5)

        add_frame = tk.Frame(self.win, bg="white")
        add_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(add_frame, text="ID:", bg="white").grid(row=0, column=0, padx=5)
        self.id_entry = ttk.Entry(add_frame, width=8)
        self.id_entry.grid(row=0, column=1, padx=5)

        ttk.Button(add_frame, text="➕ Agregar Cubículo", command=self._agregar).grid(row=0, column=2, padx=5)

        btn_frame = tk.Frame(self.win, bg="white")
        btn_frame.pack(fill="x", padx=15, pady=5)
        ttk.Button(btn_frame, text="✖ Eliminar Seleccionado", command=self._eliminar).pack(side="left", padx=5)

    def _cargar_cubiculos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if self.mysql:
            from db import obtener_cubiculos_completos
            for cub_id, asesor, estado in obtener_cubiculos_completos():
                self.tree.insert("", "end", values=(cub_id, asesor, estado))

    def _agregar(self):
        cub_id = self.id_entry.get().strip().upper()
        if not cub_id:
            messagebox.showwarning("ID requerido", "Ingresa un ID para el cubículo.", parent=self.win)
            return
        if self.mysql:
            from db import insertar_cubiculo
            if insertar_cubiculo(cub_id):
                self._cargar_cubiculos()
                self.app_ref._refrescar_cubiculos_db()
                self.id_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Error", "El cubículo ya existe.", parent=self.win)
        else:
            messagebox.showinfo("Modo Local", "Conecta MySQL para gestionar cubículos.", parent=self.win)

    def _eliminar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un cubículo de la tabla.", parent=self.win)
            return
        valores = self.tree.item(seleccion[0], "values")
        if messagebox.askyesno("Confirmar", f"¿Eliminar cubículo '{valores[0]}'?" +
                               ("\nSe desvinculará del asesor asignado." if valores[1] != "Sin asignar" else ""),
                               parent=self.win):
            if self.mysql:
                from db import eliminar_cubiculo
                eliminar_cubiculo(valores[0])
                self._cargar_cubiculos()
                self.app_ref._refrescar_cubiculos_db()


# ==================== Aplicación Principal ====================
class SCA_App:
    def __init__(self, root, mysql_disponible=False):
        self.root = root
        self.mysql = mysql_disponible
        self.root.title("SCA SSUAS - Panel de Brigadista")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        self.estados_cubiculos = {}
        self.asesores_disponibles = ["Graciela Argüelles", "Edgar Galaz", "Otro"]
        self.widgets_cubiculos = {}
        self.turno_actual = None

        self._build_top_bar()
        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

        self.pantalla = PantallaTurnos(self.root)
        self.pantalla.actualizar(None, [])

        if self.mysql:
            from db import obtener_asesores_nombres, obtener_turnos_espera
            asesores_bd = obtener_asesores_nombres()
            if asesores_bd:
                self.asesores_disponibles = asesores_bd
                self._refrescar_asesores()
            self._cargar_cubiculos_iniciales()
            turnos = obtener_turnos_espera()
            for t in turnos:
                self.agregar_a_lista(t[0], t[1], t[2], t[3], t[4])
            self._actualizar_contador()

    # ==================== Barra superior ====================
    def _build_top_bar(self):
        top_bar = tk.Frame(self.root, bg="#003087", height=50)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="SCA SSUAS - Panel de Brigadista",
                 bg="#003087", fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=10)

        btn_frame = tk.Frame(top_bar, bg="#003087")
        btn_frame.pack(side="right", padx=15)

        ttk.Button(btn_frame, text="📺 Pantalla de Turnos",
                   command=self._abrir_pantalla).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="👤 Gestión Asesores",
                   command=self._abrir_gestion_asesores).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="🏢 Gestión Cubículos",
                   command=self._abrir_gestion_cubiculos).pack(side="left", padx=3)

    def _abrir_pantalla(self):
        try:
            if not self.pantalla.win.winfo_exists():
                raise Exception
        except Exception:
            self.pantalla = PantallaTurnos(self.root)
        self.pantalla.win.lift()
        self._refrescar_pantalla()

    def _abrir_gestion_asesores(self):
        VentanaGestionAsesores(self, self.mysql)

    def _abrir_gestion_cubiculos(self):
        VentanaGestionCubiculos(self, self.mysql)

    # ==================== Panel Izquierdo ====================
    def _build_left_panel(self):
        left_frame = tk.Frame(self.root, bg="white", relief="ridge", bd=2, padx=15, pady=15)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        logo_frame = tk.Frame(left_frame, bg="#003087")
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="SCA\nSS UAS", bg="#003087", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(left_frame, text="REGISTRO DE ALUMNO", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))

        tk.Label(left_frame, text="Nombre completo:").pack(anchor="w")
        self.nombre_entry = ttk.Entry(left_frame, width=35)
        self.nombre_entry.pack(fill="x", pady=2)

        tk.Label(left_frame, text="Facultad:").pack(anchor="w", pady=(8, 2))
        self.facultad_combo = ttk.Combobox(left_frame, values=["FIM", "UANEG", "FCQB", "FCA", "Otra"],
                                           width=32, state="readonly")
        self.facultad_combo.pack(fill="x", pady=2)
        self.facultad_combo.set("Seleccione la Facultad")

        tk.Label(left_frame, text="Asesor:").pack(anchor="w", pady=(8, 2))
        self.asesor_combo = ttk.Combobox(left_frame, values=self.asesores_disponibles,
                                         width=32, state="readonly")
        self.asesor_combo.pack(fill="x", pady=2)
        self.asesor_combo.set("Seleccione al Asesor")

        ttk.Button(left_frame, text="➕ Generar Turno", command=self.generar_turno).pack(pady=(15, 5))

        # Sección de llamado de turnos
        tk.Label(left_frame, text="LLAMAR / SALTAR TURNO", font=("Arial", 11, "bold"),
                 bg="white").pack(anchor="w", pady=(5, 5))
        tk.Label(left_frame, text="Selecciona un estudiante de la lista y\nelige qué hacer:",
                 font=("Arial", 9), bg="white", fg="#555").pack(anchor="w")

        btn_call_frame = tk.Frame(left_frame, bg="white")
        btn_call_frame.pack(fill="x", pady=5)
        ttk.Button(btn_call_frame, text="📢 Llamar Seleccionado",
                   command=self.llamar_seleccionado).pack(side="left", padx=3, fill="x", expand=True)
        ttk.Button(btn_call_frame, text="⏭ Saltar Seleccionado",
                   command=self.saltar_seleccionado).pack(side="left", padx=3, fill="x", expand=True)

        tk.Label(left_frame, text="Turno en Atención:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.ultimo_turno_label = tk.Label(left_frame, text="---", bg="#e0e0e0",
                                           font=("Arial", 12, "bold"), width=15, relief="sunken")
        self.ultimo_turno_label.pack(pady=2)

        tk.Label(left_frame, text="Cambiar Estado Cubículo",
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
        self.cubiculo_combo = ttk.Combobox(left_frame, values=list(self.estados_cubiculos.keys()),
                                           state="readonly")
        self.cubiculo_combo.pack(fill="x")
        self.cubiculo_combo.set("Seleccionar Cubículo")

        btn_frame = tk.Frame(left_frame, bg="white")
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="🟢 Libre",
                   command=lambda: self.cambiar_estado("Libre")).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="🔴 Ocupar",
                   command=lambda: self.cambiar_estado("Ocupado")).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="🟡 Ausentar",
                   command=lambda: self.cambiar_estado("Ausente")).pack(side="left", padx=3)

        tk.Label(left_frame, text="Leyenda:", font=("Arial", 9, "bold"), bg="white").pack(anchor="w", pady=(12, 2))
        for estado, cfg in ESTADOS.items():
            tk.Label(left_frame, text=f"  {cfg['indicador']}  {estado}",
                     fg=cfg["fg"], bg="white", font=("Arial", 9)).pack(anchor="w")

    # ==================== Panel Central ====================
    def _build_center_panel(self):
        center_frame = tk.Frame(self.root, bg="white", relief="ridge", bd=2)
        center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        header = tk.Frame(center_frame, bg="white")
        header.pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(header, text="LISTA DE ESPERA", font=("Arial", 14, "bold"), bg="white").pack(side="left")
        self.lbl_contador = tk.Label(header, text="En espera: 0", font=("Arial", 10),
                                     bg="#e3f2fd", fg="#1565c0", relief="solid", bd=1, padx=6)
        self.lbl_contador.pack(side="right")

        columns = ("Turno", "Alumno", "Facultad", "Asesor", "Hora")
        self.tree = ttk.Treeview(center_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    # ==================== Panel Derecho ====================
    def _build_right_panel(self):
        right_frame = tk.Frame(self.root, bg="white", relief="ridge", bd=2, padx=10, pady=10)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        tk.Label(right_frame, text="Cubículos", font=("Arial", 14, "bold"), bg="white").pack(pady=5)
        self.cubiculos_frame = tk.Frame(right_frame, bg="white")
        self.cubiculos_frame.pack()
        self._crear_cubiculos()

    # ==================== Cubículos UI ====================
    def _cargar_cubiculos_iniciales(self):
        from db import inicializar_cubiculos, obtener_cubiculos_completos
        cubs = obtener_cubiculos_completos()
        if not cubs:
            cubs_default = {
                "A1": "Graciela Argüelles",
                "A2": "Graciela Argüelles",
                "A3": "Edgar Galaz",
                "B1": "Edgar Galaz",
                "B2": "Otro",
                "B3": "Otro",
                "C1": "Sin asignar",
                "C2": "Sin asignar",
            }
            inicializar_cubiculos(cubs_default)
            cubs = obtener_cubiculos_completos()

        self.estados_cubiculos = {}
        self.cubiculos_info = {}
        for cub_id, asesor, estado in cubs:
            self.estados_cubiculos[cub_id] = estado
            self.cubiculos_info[cub_id] = asesor

        self.cubiculo_combo["values"] = list(self.estados_cubiculos.keys())
        self._crear_cubiculos()

    def _crear_cubiculos(self):
        for widget in self.cubiculos_frame.winfo_children():
            widget.destroy()
        self.widgets_cubiculos.clear()

        cubiculos = list(self.estados_cubiculos.keys())
        for i, cub in enumerate(cubiculos):
            estado = self.estados_cubiculos.get(cub, "Libre")
            cfg = ESTADOS[estado]
            asesor = getattr(self, 'cubiculos_info', {}).get(cub, "")

            frame = tk.Frame(self.cubiculos_frame, relief="ridge", bd=2,
                             width=120, height=130, bg=cfg["bg"], cursor="hand2")
            frame.grid(row=i // 3, column=i % 3, padx=6, pady=6)
            frame.grid_propagate(False)
            frame.pack_propagate(False)

            lbl_indicador = tk.Label(frame, text=cfg["indicador"],
                                     fg=cfg["fg"], bg=cfg["bg"], font=("Arial", 16),
                                     width=6, anchor="center")
            lbl_indicador.place(relx=0.5, rely=0.05, anchor="n")

            lbl_nombre = tk.Label(frame, text=cub, font=("Arial", 10, "bold"),
                                  bg=cfg["bg"], width=10, anchor="center")
            lbl_nombre.place(relx=0.5, rely=0.35, anchor="center")

            lbl_asesor = tk.Label(frame, text=asesor,
                                  font=("Arial", 7), fg="#555", bg=cfg["bg"],
                                  width=14, anchor="center", justify="center")
            lbl_asesor.place(relx=0.5, rely=0.54, anchor="center")

            lbl_estado = tk.Label(frame, text=cfg["texto"],
                                  font=("Arial", 7, "italic"), fg=cfg["fg"], bg=cfg["bg"],
                                  width=10, anchor="center")
            lbl_estado.place(relx=0.5, rely=0.83, anchor="center")

            self.widgets_cubiculos[cub] = {
                "frame": frame,
                "lbl_indicador": lbl_indicador,
                "lbl_nombre": lbl_nombre,
                "lbl_asesor": lbl_asesor,
                "lbl_estado": lbl_estado,
            }

            for widget in (frame, lbl_indicador, lbl_nombre, lbl_asesor, lbl_estado):
                widget.bind("<Button-1>", lambda e, c=cub: self._seleccionar_cubiculo(c))

    def _seleccionar_cubiculo(self, cub):
        self.cubiculo_combo.set(cub)

    # ==================== Refrescos ====================
    def _refrescar_asesores(self):
        if self.mysql:
            from db import obtener_asesores_nombres
            asesores = obtener_asesores_nombres()
            if asesores:
                self.asesores_disponibles = asesores
        self.asesor_combo["values"] = self.asesores_disponibles

    def _refrescar_cubiculos_db(self):
        if self.mysql:
            from db import obtener_cubiculos_completos
            cubs = obtener_cubiculos_completos()
            self.estados_cubiculos = {}
            self.cubiculos_info = {}
            for cub_id, asesor, estado in cubs:
                self.estados_cubiculos[cub_id] = estado
                self.cubiculos_info[cub_id] = asesor
            self.cubiculo_combo["values"] = list(self.estados_cubiculos.keys())
            self._crear_cubiculos()

    # ==================== Estados ====================
    def cambiar_estado(self, nuevo_estado):
        cub = self.cubiculo_combo.get()
        if cub not in self.estados_cubiculos:
            messagebox.showwarning("Selecciona cubículo", "Por favor selecciona un cubículo válido.")
            return
        self.estados_cubiculos[cub] = nuevo_estado
        cfg = ESTADOS[nuevo_estado]
        w = self.widgets_cubiculos[cub]
        w["frame"].config(bg=cfg["bg"])
        w["lbl_indicador"].config(text=cfg["indicador"], fg=cfg["fg"], bg=cfg["bg"])
        w["lbl_nombre"].config(bg=cfg["bg"])
        w["lbl_asesor"].config(bg=cfg["bg"])
        w["lbl_estado"].config(text=cfg["texto"], fg=cfg["fg"], bg=cfg["bg"])

        if self.mysql:
            from db import actualizar_estado_cubiculo
            actualizar_estado_cubiculo(cub, nuevo_estado)

    # ==================== Turnos ====================
    def _obtener_siguiente_numero_turno(self):
        if self.mysql:
            from db import contar_turnos_espera
            return contar_turnos_espera() + 1
        return len(self.tree.get_children()) + 1

    def generar_turno(self):
        nombre = self.nombre_entry.get().strip()
        facultad = self.facultad_combo.get()
        asesor = self.asesor_combo.get()

        if not nombre or facultad == "Seleccione la Facultad" or asesor == "Seleccione al Asesor":
            messagebox.showwarning("Datos incompletos", "Por favor completa todos los campos.")
            return

        num = self._obtener_siguiente_numero_turno()
        turno = f"T{num:02d}"
        hora = datetime.now().strftime("%H:%M")
        self.agregar_a_lista(turno, nombre, facultad, asesor, hora)

        if self.mysql:
            from db import insertar_turno
            insertar_turno(turno, nombre, facultad, asesor, hora)

        self.nombre_entry.delete(0, tk.END)
        self.facultad_combo.set("Seleccione la Facultad")
        self.asesor_combo.set("Seleccione al Asesor")
        self._actualizar_contador()
        self._refrescar_pantalla()
        messagebox.showinfo("Turno Generado", f"¡Turno {turno} generado correctamente!")

    def _obtener_seleccionado(self):
        """Obtiene el turno seleccionado en el Treeview."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Sin selección", "Selecciona un estudiante de la lista de espera.")
            return None
        valores = self.tree.item(seleccion[0], "values")
        return {
            "id": seleccion[0],
            "turno": valores[0],
            "alumno": valores[1],
            "facultad": valores[2],
            "asesor": valores[3],
            "hora": valores[4],
        }

    def llamar_seleccionado(self):
        """Llama al turno que el usuario seleccionó en la lista."""
        data = self._obtener_seleccionado()
        if not data:
            return

        self.turno_actual = {
            "turno": data["turno"],
            "alumno": data["alumno"],
            "asesor": data["asesor"],
        }

        self.tree.delete(data["id"])
        self._actualizar_contador()
        self.ultimo_turno_label.config(text=self.turno_actual["turno"])
        self._refrescar_pantalla()

        if self.mysql:
            from db import llamar_turno_especifico
            llamar_turno_especifico(data["turno"])

        messagebox.showinfo(
            "Turno Llamado",
            f"Turno {data['turno']} ({data['alumno']}) → Asesor: {data['asesor']}"
        )

    def saltar_seleccionado(self):
        """
        Salta el turno seleccionado: lo mueve al final de la lista de espera
        y llama al siguiente cuyo asesor esté libre.
        """
        data = self._obtener_seleccionado()
        if not data:
            return

        # Mover al final de la lista
        self.tree.delete(data["id"])
        self.agregar_a_lista(data["turno"], data["alumno"], data["facultad"], data["asesor"], data["hora"])
        self._actualizar_contador()

        # Llamar al siguiente disponible
        if self.mysql:
            from db import llamar_siguiente_turno
            siguiente = llamar_siguiente_turno()
            if siguiente:
                self.turno_actual = {
                    "turno": siguiente["turno"],
                    "alumno": siguiente["alumno"],
                    "asesor": siguiente["asesor"],
                }
                self.ultimo_turno_label.config(text=self.turno_actual["turno"])
                messagebox.showinfo(
                    "Turno Saltado",
                    f"Turno {data['turno']} ({data['alumno']}) movido al final.\n"
                    f"Se llamó al siguiente: {siguiente['turno']} ({siguiente['alumno']})"
                )
            else:
                self.turno_actual = None
                self.ultimo_turno_label.config(text="---")
                messagebox.showinfo(
                    "Turno Saltado",
                    f"Turno {data['turno']} ({data['alumno']}) movido al final.\n"
                    "No hay más turnos en espera."
                )
        else:
            # Modo local: busca el primer turno que no sea el saltado
            self.turno_actual = None
            hijos = self.tree.get_children()
            if hijos:
                primero = hijos[0]
                v = self.tree.item(primero, "values")
                self.turno_actual = {
                    "turno": v[0],
                    "alumno": v[1],
                    "asesor": v[3],
                }
                self.tree.delete(primero)
                self.ultimo_turno_label.config(text=self.turno_actual["turno"])
            else:
                self.ultimo_turno_label.config(text="---")

            messagebox.showinfo(
                "Turno Saltado",
                f"Turno {data['turno']} ({data['alumno']}) movido al final."
            )

        self._actualizar_contador()
        self._refrescar_pantalla()

    def agregar_a_lista(self, turno, alumno, facultad, asesor, hora):
        self.tree.insert("", "end", values=(turno, alumno, facultad, asesor, hora))

    def _actualizar_contador(self):
        n = len(self.tree.get_children())
        self.lbl_contador.config(text=f"En espera: {n}")

    def _refrescar_pantalla(self):
        try:
            if not self.pantalla.win.winfo_exists():
                return
        except Exception:
            return

        siguientes = []
        for item_id in self.tree.get_children():
            v = self.tree.item(item_id, "values")
            siguientes.append({"turno": v[0], "alumno": v[1]})

        self.pantalla.actualizar(self.turno_actual, siguientes)


if __name__ == "__main__":
    root = tk.Tk()
    app = SCA_App(root)
    root.mainloop()