"""
Módulo de Formulario Modal para Registro de Actas de Presentación.
Capa: Presentación / Vista (View en MVC).

Diseño y UX:
- Ventana modal CTkToplevel (900x750) centrada con grab_set().
- Tarjeta blanca principal dividida en 4 secciones visuales con bordes sutiles:
  1. Datos del Libro
  2. Datos del Presentante (Declarante)
  3. Datos del Presentado (Niño/Niña)
  4. Lugar de Nacimiento
- Inputs con height=45, fuentes 14-15px y focus rings interactivos (#2563EB).
- Selectores de fecha modernos con popup flotante tkcalendar.
"""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from typing import Any
import customtkinter as ctk
from tkcalendar import Calendar


class FormularioActa(ctk.CTkToplevel):
    """
    Ventana modal para capturar y validar el registro de una nueva acta de presentación.
    """

    COLOR_BORDE_INACTIVO = "#CBD5E1"
    COLOR_BORDE_ACTIVO = "#2563EB"

    def __init__(self, controlador: Any, parent: Any = None) -> None:
        super().__init__(master=parent)

        self.controlador = controlador
        self._popup_calendario: tk.Toplevel | None = None

        # 1. Configuración de la ventana modal
        self.title("Registrar Nueva Acta de Presentación")
        self.configure(fg_color="#F0F2F5")
        self._centrar_ventana(ancho=900, alto=750)
        self.resizable(False, False)

        if parent is not None:
            self.transient(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 2. Construcción de la interfaz
        self._crear_cabecera()
        self._crear_tarjeta_formulario()
        self._crear_botones_inferiores()
        self._configurar_accesibilidad_focus()

        # 3. Bloqueo modal y foco inicial en No. Acta
        self.bind("<Escape>", lambda _e: self.destroy())
        self.update_idletasks()
        self.grab_set()
        self.entry_acta.focus_set()
        self.after(50, self.entry_acta.focus_set)

    def _centrar_ventana(self, ancho: int, alto: int) -> None:
        """Centra la ventana modal en la pantalla."""
        pantalla_w = self.winfo_screenwidth()
        pantalla_h = self.winfo_screenheight()
        pos_x = max(0, (pantalla_w - ancho) // 2)
        pos_y = max(0, (pantalla_h - alto) // 2)
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    def _crear_cabecera(self) -> None:
        """Título interno grande superior."""
        frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        frame_cabecera.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))

        lbl_titulo = ctk.CTkLabel(
            frame_cabecera,
            text="Registrar Nueva Acta de Presentación",
            font=("Segoe UI", 22, "bold"),
            text_color="#0F172A",
            anchor="w",
        )
        lbl_titulo.pack(anchor="w")

    def _crear_seccion(self, parent: Any, titulo: str, fila: int) -> ctk.CTkFrame:
        """Crea una sección visual con borde sutil y encabezado homogéneo."""
        seccion = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color="#F8FAFC",
            border_width=1,
            border_color="#E2E8F0",
        )
        seccion.grid(row=fila, column=0, sticky="ew", padx=16, pady=6)

        lbl_seccion = ctk.CTkLabel(
            seccion,
            text=titulo,
            font=("Segoe UI", 15, "bold"),
            text_color="#1E293B",
            anchor="w",
        )
        lbl_seccion.grid(row=0, column=0, columnspan=10, sticky="w", padx=14, pady=(10, 6))
        return seccion

    def _crear_entry(
        self,
        parent: Any,
        width: int | None = None,
        placeholder: str = "",
    ) -> ctk.CTkEntry:
        """Crea un CTkEntry estándar con altura de 45px y bordes consistentes."""
        kwargs: dict[str, Any] = {
            "height": 45,
            "font": ("Segoe UI", 14),
            "border_width": 1,
            "corner_radius": 8,
            "border_color": self.COLOR_BORDE_INACTIVO,
            "fg_color": "#FFFFFF",
            "text_color": "#0F172A",
        }
        if width is not None:
            kwargs["width"] = width
        if placeholder:
            kwargs["placeholder_text"] = placeholder
        return ctk.CTkEntry(parent, **kwargs)

    def _crear_etiqueta(self, parent: Any, texto: str) -> ctk.CTkLabel:
        """Crea una etiqueta de campo con tipografía estándar."""
        return ctk.CTkLabel(
            parent,
            text=texto,
            font=("Segoe UI", 14, "bold"),
            text_color="#475569",
            anchor="w",
        )

    def _crear_tarjeta_formulario(self) -> None:
        """Construye la tarjeta blanca principal con las secciones del acta."""
        tarjeta = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E2E8F0",
        )
        tarjeta.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        tarjeta.grid_columnconfigure(0, weight=1)

        # =====================================================================
        # 1. SECCIÓN: Datos del Libro
        # =====================================================================
        sec_libro = self._crear_seccion(tarjeta, "Datos del Libro", fila=0)
        for col in range(4):
            sec_libro.grid_columnconfigure(col, weight=0)
        sec_libro.grid_columnconfigure(4, weight=1)

        # No. Acta
        col_acta = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_acta.grid(row=1, column=0, sticky="w", padx=(14, 10), pady=(0, 12))
        self._crear_etiqueta(col_acta, "No. Acta:").pack(anchor="w", pady=(0, 4))
        self.entry_acta = self._crear_entry(col_acta, width=100)
        self.entry_acta.pack()

        # Libro
        col_libro = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_libro.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 12))
        self._crear_etiqueta(col_libro, "Libro:").pack(anchor="w", pady=(0, 4))
        self.entry_libro = self._crear_entry(col_libro, width=80)
        self.entry_libro.pack()

        # Folio
        col_folio = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_folio.grid(row=1, column=2, sticky="w", padx=(0, 10), pady=(0, 12))
        self._crear_etiqueta(col_folio, "Folio:").pack(anchor="w", pady=(0, 4))
        self.entry_folio = self._crear_entry(col_folio, width=80)
        self.entry_folio.pack()

        # Año
        col_anio = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_anio.grid(row=1, column=3, sticky="w", padx=(0, 14), pady=(0, 12))
        self._crear_etiqueta(col_anio, "Año:").pack(anchor="w", pady=(0, 4))
        self.entry_anio = self._crear_entry(col_anio, width=80)
        self.entry_anio.pack()

        # Fecha de Presentación
        col_fecha_pres = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_fecha_pres.grid(row=1, column=4, sticky="ew", padx=(0, 14), pady=(0, 12))
        self._crear_etiqueta(col_fecha_pres, "Fecha de Presentación:").pack(anchor="w", pady=(0, 4))
        sub_fecha_pres, self.entry_fecha_presentacion = self._crear_campo_fecha(col_fecha_pres)
        sub_fecha_pres.pack(fill="x")

        # =====================================================================
        # 2. SECCIÓN: Datos del Presentante (Declarante)
        # =====================================================================
        sec_pres = self._crear_seccion(tarjeta, "Datos del Presentante (Declarante)", fila=1)
        sec_pres.grid_columnconfigure(0, weight=0)
        sec_pres.grid_columnconfigure(1, weight=1)

        # C.I.
        col_ci = ctk.CTkFrame(sec_pres, fg_color="transparent")
        col_ci.grid(row=1, column=0, sticky="w", padx=(14, 12), pady=(0, 12))
        self._crear_etiqueta(col_ci, "C.I.:").pack(anchor="w", pady=(0, 4))
        self.entry_ci = self._crear_entry(col_ci, width=150)
        self.entry_ci.pack()

        # Nombres y Apellidos
        col_nom_pres = ctk.CTkFrame(sec_pres, fg_color="transparent")
        col_nom_pres.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=(0, 12))
        self._crear_etiqueta(col_nom_pres, "Nombres y Apellidos:").pack(anchor="w", pady=(0, 4))
        self.entry_presentante_nombres = self._crear_entry(col_nom_pres)
        self.entry_presentante_nombres.pack(fill="x")

        # =====================================================================
        # 3. SECCIÓN: Datos del Presentado (Niño/Niña)
        # =====================================================================
        sec_nino = self._crear_seccion(tarjeta, "Datos del Presentado (Niño/Niña)", fila=2)
        sec_nino.grid_columnconfigure(0, weight=2)
        sec_nino.grid_columnconfigure(1, weight=1)
        sec_nino.grid_columnconfigure(2, weight=1)

        # Fila 1: Nombres y Apellidos (col 0-1) + Sexo (col 2)
        col_nom_nino = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_nom_nino.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(14, 12), pady=(0, 10))
        self._crear_etiqueta(col_nom_nino, "Nombres y Apellidos:").pack(anchor="w", pady=(0, 4))
        self.entry_presentado_nombres = self._crear_entry(col_nom_nino)
        self.entry_presentado_nombres.pack(fill="x")

        col_sexo = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_sexo.grid(row=1, column=2, sticky="ew", padx=(0, 14), pady=(0, 10))
        self._crear_etiqueta(col_sexo, "Sexo:").pack(anchor="w", pady=(0, 4))
        self.combo_sexo = ctk.CTkComboBox(
            col_sexo,
            values=["niño", "niña"],
            height=45,
            font=("Segoe UI", 14),
            dropdown_font=("Segoe UI", 14),
            border_width=1,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color="#FFFFFF",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color="#0F172A",
            state="readonly",
        )
        self.combo_sexo.set("")
        self.combo_sexo.pack(fill="x")

        # Fila 2: Fecha de Nacimiento (col 0) + Hora de Nacimiento (col 1) + Tipo de Parto (col 2)
        col_fecha_nac = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_fecha_nac.grid(row=2, column=0, sticky="ew", padx=(14, 12), pady=(0, 12))
        self._crear_etiqueta(col_fecha_nac, "Fecha de Nacimiento:").pack(anchor="w", pady=(0, 4))
        sub_fecha_nac, self.entry_fecha_nac = self._crear_campo_fecha(col_fecha_nac)
        sub_fecha_nac.pack(fill="x")

        col_hora_nac = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_hora_nac.grid(row=2, column=1, sticky="w", padx=(0, 12), pady=(0, 12))
        self._crear_etiqueta(col_hora_nac, "Hora de Nacimiento:").pack(anchor="w", pady=(0, 4))
        self.entry_hora_nac = self._crear_entry(col_hora_nac, width=100, placeholder="HH:MM AM/PM")
        self.entry_hora_nac.pack(anchor="w")

        col_parto = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_parto.grid(row=2, column=2, sticky="ew", padx=(0, 14), pady=(0, 12))
        self._crear_etiqueta(col_parto, "Tipo de Parto:").pack(anchor="w", pady=(0, 4))
        self.combo_tipo_parto = ctk.CTkComboBox(
            col_parto,
            values=["Único", "Gemelos", "Mellizos", "Múltiple"],
            height=45,
            font=("Segoe UI", 14),
            dropdown_font=("Segoe UI", 14),
            border_width=1,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color="#FFFFFF",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color="#0F172A",
            state="readonly",
        )
        self.combo_tipo_parto.set("")
        self.combo_tipo_parto.pack(fill="x")

        # =====================================================================
        # 4. SECCIÓN: Lugar de Nacimiento
        # =====================================================================
        sec_lugar = self._crear_seccion(tarjeta, "Lugar de Nacimiento", fila=3)
        sec_lugar.grid_columnconfigure(0, weight=1)
        sec_lugar.grid_columnconfigure(1, weight=1)
        sec_lugar.grid_columnconfigure(2, weight=2)

        col_estado = ctk.CTkFrame(sec_lugar, fg_color="transparent")
        col_estado.grid(row=1, column=0, sticky="ew", padx=(14, 12), pady=(0, 12))
        self._crear_etiqueta(col_estado, "Estado:").pack(anchor="w", pady=(0, 4))
        self.entry_estado = self._crear_entry(col_estado, placeholder="Ej. Barinas")
        self.entry_estado.pack(fill="x")

        col_ciudad = ctk.CTkFrame(sec_lugar, fg_color="transparent")
        col_ciudad.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(0, 12))
        self._crear_etiqueta(col_ciudad, "Ciudad:").pack(anchor="w", pady=(0, 4))
        self.entry_ciudad = self._crear_entry(col_ciudad, placeholder="Ej. Barinas")
        self.entry_ciudad.pack(fill="x")

        col_recinto = ctk.CTkFrame(sec_lugar, fg_color="transparent")
        col_recinto.grid(row=1, column=2, sticky="ew", padx=(0, 14), pady=(0, 12))
        self._crear_etiqueta(col_recinto, "Recinto:").pack(anchor="w", pady=(0, 4))
        self.entry_recinto = self._crear_entry(col_recinto, placeholder="Ej. Hospital Dr. Luis Razetti")
        self.entry_recinto.pack(fill="x")

    def _crear_campo_fecha(self, parent: Any) -> tuple[ctk.CTkFrame, ctk.CTkEntry]:
        """Crea un campo compuesto de fecha (Entry YYYY-MM-DD + botón calendario 📅)."""
        frame_compuesto = ctk.CTkFrame(parent, fg_color="transparent")

        entry = self._crear_entry(frame_compuesto, placeholder="YYYY-MM-DD")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_cal = ctk.CTkButton(
            frame_compuesto,
            text="📅",
            width=45,
            height=45,
            font=("Segoe UI", 16),
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=8,
        )
        btn_cal.configure(command=lambda e=entry, b=btn_cal: self._abrir_calendario(e, b))
        btn_cal.pack(side="right")

        return frame_compuesto, entry

    def _abrir_calendario(self, entry_destino: ctk.CTkEntry, boton_invocador: ctk.CTkButton) -> None:
        """Abre el selector flotante tkcalendar y restaura el grab modal al cerrarse."""
        if self._popup_calendario is not None and self._popup_calendario.winfo_exists():
            self._popup_calendario.destroy()

        popup = tk.Toplevel(self)
        self._popup_calendario = popup
        popup.title("Seleccionar Fecha")
        popup.transient(self)
        popup.resizable(False, False)
        popup.configure(background="#FFFFFF")

        anio_ini, mes_ini, dia_ini = None, None, None
        texto_actual = entry_destino.get().strip()
        if texto_actual:
            try:
                dt = datetime.strptime(texto_actual, "%Y-%m-%d")
                anio_ini, mes_ini, dia_ini = dt.year, dt.month, dt.day
            except ValueError:
                pass

        cal_kwargs: dict[str, Any] = {
            "selectmode": "day",
            "date_pattern": "yyyy-mm-dd",
            "background": "#2563EB",
            "foreground": "#FFFFFF",
            "headersbackground": "#1E293B",
            "headersforeground": "#FFFFFF",
            "selectbackground": "#2563EB",
            "selectforeground": "#FFFFFF",
            "normalbackground": "#FFFFFF",
            "normalforeground": "#0F172A",
            "weekendbackground": "#F8FAFC",
            "weekendforeground": "#0F172A",
            "font": ("Segoe UI", 11),
            "borderwidth": 0,
        }
        if anio_ini:
            cal_kwargs["year"] = anio_ini
            cal_kwargs["month"] = mes_ini
            cal_kwargs["day"] = dia_ini

        calendario = Calendar(popup, **cal_kwargs)
        calendario.pack(padx=10, pady=10)

        def cerrar_popup(_event: Any = None) -> None:
            if popup.winfo_exists():
                popup.destroy()
            if self.winfo_exists():
                self.grab_set()

        def on_fecha_seleccionada(_event: Any = None) -> None:
            fecha_elegida = calendario.get_date()
            entry_destino.delete(0, "end")
            entry_destino.insert(0, fecha_elegida)
            cerrar_popup()

        calendario.bind("<<CalendarSelected>>", on_fecha_seleccionada)
        popup.bind("<Escape>", cerrar_popup)
        popup.protocol("WM_DELETE_WINDOW", cerrar_popup)

        self.update_idletasks()
        popup.update_idletasks()

        root_x = boton_invocador.winfo_rootx()
        root_y = boton_invocador.winfo_rooty() + boton_invocador.winfo_height() + 4

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pop_w = popup.winfo_reqwidth()
        pop_h = popup.winfo_reqheight()

        if root_x + pop_w > screen_w:
            root_x = screen_w - pop_w - 20
        if root_y + pop_h > screen_h:
            root_y = boton_invocador.winfo_rooty() - pop_h - 4

        popup.geometry(f"+{root_x}+{root_y}")
        popup.grab_set()

    def _crear_botones_inferiores(self) -> None:
        """Botones de acción inferiores: Cancelar y Guardar Acta."""
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))

        btn_guardar = ctk.CTkButton(
            frame_acciones,
            text="Guardar Acta",
            width=150,
            height=45,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color="#059669",
            hover_color="#047857",
            text_color="#FFFFFF",
            command=self._ejecutar_guardado,
        )
        btn_guardar.pack(side="right", padx=(10, 0))

        btn_cancelar = ctk.CTkButton(
            frame_acciones,
            text="Cancelar",
            width=120,
            height=45,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#0F172A",
            command=self.destroy,
        )
        btn_cancelar.pack(side="right")

    def _configurar_accesibilidad_focus(self) -> None:
        """Asigna anillos de foco azul (#2563EB) a todos los CTkEntry."""
        entradas = (
            self.entry_acta,
            self.entry_libro,
            self.entry_folio,
            self.entry_anio,
            self.entry_fecha_presentacion,
            self.entry_ci,
            self.entry_presentante_nombres,
            self.entry_presentado_nombres,
            self.entry_fecha_nac,
            self.entry_hora_nac,
            self.entry_estado,
            self.entry_ciudad,
            self.entry_recinto,
        )
        for entry in entradas:
            entry.bind("<FocusIn>", lambda _e, w=entry: w.configure(border_color=self.COLOR_BORDE_ACTIVO, border_width=2))
            entry.bind("<FocusOut>", lambda _e, w=entry: w.configure(border_color=self.COLOR_BORDE_INACTIVO, border_width=1))

    @staticmethod
    def _normalizar_hora(hora_raw: str) -> str:
        """
        Convierte entradas en formato 12h ('HH:MM AM/PM') a 24h ('HH:MM')
        requerido por la capa de servicio. Si ya es 24h o inválido, lo retorna tal cual
        para que la capa de negocio aplique su validación estándar.
        """
        texto = hora_raw.strip().upper()
        if not texto:
            return ""
        for fmt in ("%I:%M %p", "%I:%M%p"):
            try:
                return datetime.strptime(texto, fmt).strftime("%H:%M")
            except ValueError:
                continue
        return hora_raw.strip()

    def _construir_datos(self) -> dict[str, Any]:
        """Recolecta y empaqueta todos los datos del formulario en un diccionario."""
        datos: dict[str, Any] = {
            "numero_acta": self.entry_acta.get().strip(),
            "numero_libro": self.entry_libro.get().strip(),
            "numero_folio": self.entry_folio.get().strip(),
            "anio": self.entry_anio.get().strip(),
            "fecha_presentacion": self.entry_fecha_presentacion.get().strip(),
            "presentante_cedula": self.entry_ci.get().strip(),
            "presentante_nombres": self.entry_presentante_nombres.get().strip(),
            "presentado_nombres": self.entry_presentado_nombres.get().strip(),
            "presentado_sexo": self.combo_sexo.get().strip(),
            "presentado_fecha_nac": self.entry_fecha_nac.get().strip(),
            "presentado_hora_nac": self._normalizar_hora(self.entry_hora_nac.get()),
            "presentado_tipo_parto": self.combo_tipo_parto.get().strip(),
        }

        estado = self.entry_estado.get().strip()
        if estado:
            datos["estado"] = estado

        ciudad = self.entry_ciudad.get().strip()
        if ciudad:
            datos["ciudad"] = ciudad

        recinto = self.entry_recinto.get().strip()
        if recinto:
            datos["recinto"] = recinto

        return datos

    def _ejecutar_guardado(self) -> None:
        """Delega el guardado de los datos al controlador."""
        datos = self._construir_datos()
        if self.controlador:
            self.controlador.guardar_acta(datos)

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un cuadro modal de error manteniendo abierto el formulario."""
        messagebox.showerror("Error", mensaje, parent=self)
        if self.winfo_exists():
            self.grab_set()
