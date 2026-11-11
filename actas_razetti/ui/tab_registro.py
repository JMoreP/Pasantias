"""
Módulo de Vista de Registro de Actas de Presentación.
Capa: Presentación / Vista (View en MVC).

Diseño y UX:
- Componente CTkFrame integrado en la ventana principal (navegación por vistas apiladas).
- Paleta 100% adaptable a Modo Claro / Modo Oscuro mediante tuplas dinámicas de CustomTkinter.
- Barra superior con botón de retroceso "← Volver" arriba a la izquierda y título grande.
- Tarjeta principal dividida en 4 secciones visuales con bordes sutiles:
  1. Datos del Libro
  2. Datos del Presentante (Declarante)
  3. Datos del Presentado (Niño/Niña)
  4. Lugar de Nacimiento
- Inputs con height=45, fuentes 14-15px, corner_radius=8 y focus rings interactivos.
"""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable
import customtkinter as ctk
from tkcalendar import Calendar


class TabRegistro(ctk.CTkFrame):
    """
    Vista para capturar y validar el registro de una nueva acta de presentación.
    """

    COLOR_BORDE_INACTIVO = ("#CBD5E1", "#444444")
    COLOR_BORDE_ACTIVO = ("#2563EB", "#3B82F6")

    def __init__(
        self,
        master: Any,
        controlador: Any = None,
        on_volver: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.controlador = controlador
        self._on_volver = on_volver
        self._popup_calendario: tk.Toplevel | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._crear_cabecera()
        self._crear_tarjeta_formulario()
        self._crear_boton_guardar()
        self._configurar_accesibilidad_focus()

    def asignar_controlador(self, controlador: Any) -> None:
        """Asigna el controlador del patrón MVC."""
        self.controlador = controlador

    def enfocar_inicio(self) -> None:
        """Coloca el foco en el campo 'No. Acta' al mostrar esta vista."""
        self.entry_acta.focus_set()

    def _crear_cabecera(self) -> None:
        """Barra superior con botón de retroceso arriba a la izquierda y título."""
        frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        frame_cabecera.grid(row=0, column=0, sticky="ew", padx=24, pady=(8, 10))

        self.btn_volver = ctk.CTkButton(
            frame_cabecera,
            text="← Volver",
            width=110,
            height=38,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color=("#E2E8F0", "#333333"),
            hover_color=("#CBD5E1", "#444444"),
            text_color=("#0F172A", "#E2E8F0"),
            command=self._ejecutar_volver,
        )
        self.btn_volver.pack(side="left")

        lbl_titulo = ctk.CTkLabel(
            frame_cabecera,
            text="Registrar Nueva Acta de Presentación",
            font=("Segoe UI", 22, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w",
        )
        lbl_titulo.pack(side="left", padx=(16, 0))

    def _crear_seccion(self, parent: Any, titulo: str, fila: int) -> ctk.CTkFrame:
        """Crea una sección visual con borde sutil y encabezado homogéneo."""
        seccion = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=("#F8FAFC", "#252525"),
            border_width=1,
            border_color=("#E2E8F0", "#333333"),
        )
        seccion.grid(row=fila, column=0, sticky="ew", padx=18, pady=7)

        lbl_seccion = ctk.CTkLabel(
            seccion,
            text=titulo,
            font=("Segoe UI", 15, "bold"),
            text_color=("#1E293B", "#E2E8F0"),
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
        """Crea un CTkEntry estándar con altura de 45px y colores adaptativos."""
        kwargs: dict[str, Any] = {
            "height": 45,
            "font": ("Segoe UI", 14),
            "border_width": 1,
            "corner_radius": 8,
            "border_color": self.COLOR_BORDE_INACTIVO,
            "fg_color": ("#FFFFFF", "#2B2B2B"),
            "text_color": ("#0F172A", "#E2E8F0"),
            "placeholder_text_color": ("#94A3B8", "#94A3B8"),
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
            text_color=("#475569", "#CBD5E1"),
            anchor="w",
        )

    def _crear_combobox(self, parent: Any, values: list[str]) -> ctk.CTkComboBox:
        """Crea un CTkComboBox adaptado a modo claro y oscuro."""
        combo = ctk.CTkComboBox(
            parent,
            values=values,
            height=45,
            font=("Segoe UI", 14),
            dropdown_font=("Segoe UI", 14),
            border_width=1,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color=("#FFFFFF", "#2B2B2B"),
            button_color=("#E2E8F0", "#333333"),
            button_hover_color=("#CBD5E1", "#444444"),
            text_color=("#0F172A", "#E2E8F0"),
            dropdown_fg_color=("#FFFFFF", "#2B2B2B"),
            dropdown_text_color=("#0F172A", "#E2E8F0"),
            dropdown_hover_color=("#E2E8F0", "#3B3B3B"),
            state="readonly",
        )
        combo.set("")
        return combo

    def _crear_tarjeta_formulario(self) -> None:
        """Construye la tarjeta principal con las secciones del acta."""
        tarjeta = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=1,
            border_color=("#E2E8F0", "#333333"),
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

        col_acta = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_acta.grid(row=1, column=0, sticky="w", padx=(14, 10), pady=(0, 12))
        self._crear_etiqueta(col_acta, "No. Acta:").pack(anchor="w", pady=(0, 4))
        self.entry_acta = self._crear_entry(col_acta, width=100)
        self.entry_acta.pack()

        col_libro = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_libro.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 12))
        self._crear_etiqueta(col_libro, "Libro:").pack(anchor="w", pady=(0, 4))
        self.entry_libro = self._crear_entry(col_libro, width=80)
        self.entry_libro.pack()

        col_folio = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_folio.grid(row=1, column=2, sticky="w", padx=(0, 10), pady=(0, 12))
        self._crear_etiqueta(col_folio, "Folio:").pack(anchor="w", pady=(0, 4))
        self.entry_folio = self._crear_entry(col_folio, width=80)
        self.entry_folio.pack()

        col_anio = ctk.CTkFrame(sec_libro, fg_color="transparent")
        col_anio.grid(row=1, column=3, sticky="w", padx=(0, 14), pady=(0, 12))
        self._crear_etiqueta(col_anio, "Año:").pack(anchor="w", pady=(0, 4))
        self.entry_anio = self._crear_entry(col_anio, width=80)
        self.entry_anio.pack()

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

        col_ci = ctk.CTkFrame(sec_pres, fg_color="transparent")
        col_ci.grid(row=1, column=0, sticky="w", padx=(14, 12), pady=(0, 12))
        self._crear_etiqueta(col_ci, "C.I.:").pack(anchor="w", pady=(0, 4))
        self.entry_ci = self._crear_entry(col_ci, width=150)
        self.entry_ci.pack()

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

        col_nom_nino = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_nom_nino.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(14, 12), pady=(0, 10))
        self._crear_etiqueta(col_nom_nino, "Nombres y Apellidos:").pack(anchor="w", pady=(0, 4))
        self.entry_presentado_nombres = self._crear_entry(col_nom_nino)
        self.entry_presentado_nombres.pack(fill="x")

        col_sexo = ctk.CTkFrame(sec_nino, fg_color="transparent")
        col_sexo.grid(row=1, column=2, sticky="ew", padx=(0, 14), pady=(0, 10))
        self._crear_etiqueta(col_sexo, "Sexo:").pack(anchor="w", pady=(0, 4))
        self.combo_sexo = self._crear_combobox(col_sexo, ["niño", "niña"])
        self.combo_sexo.pack(fill="x")

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
        self.combo_tipo_parto = self._crear_combobox(col_parto, ["Único", "Gemelos", "Mellizos", "Múltiple"])
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
            fg_color=("#E2E8F0", "#333333"),
            hover_color=("#CBD5E1", "#444444"),
            text_color=("#1E293B", "#F8FAFC"),
            corner_radius=8,
        )
        btn_cal.configure(command=lambda e=entry, b=btn_cal: self._abrir_calendario(e, b))
        btn_cal.pack(side="right")

        return frame_compuesto, entry

    def _abrir_calendario(self, entry_destino: ctk.CTkEntry, boton_invocador: ctk.CTkButton) -> None:
        """Abre el selector flotante tkcalendar inmediatamente debajo del botón."""
        if self._popup_calendario is not None and self._popup_calendario.winfo_exists():
            self._popup_calendario.destroy()

        es_oscuro = str(ctk.get_appearance_mode()).lower() == "dark"
        root_win = self.winfo_toplevel()
        popup = tk.Toplevel(root_win)
        self._popup_calendario = popup
        popup.title("Seleccionar Fecha")
        popup.transient(root_win)
        popup.resizable(False, False)
        popup.configure(background="#1E1E1E" if es_oscuro else "#FFFFFF")

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
            "headersbackground": "#333333" if es_oscuro else "#1E293B",
            "headersforeground": "#FFFFFF",
            "selectbackground": "#2563EB",
            "selectforeground": "#FFFFFF",
            "normalbackground": "#1E1E1E" if es_oscuro else "#FFFFFF",
            "normalforeground": "#E2E8F0" if es_oscuro else "#0F172A",
            "weekendbackground": "#2B2B2B" if es_oscuro else "#F8FAFC",
            "weekendforeground": "#E2E8F0" if es_oscuro else "#0F172A",
            "font": ("Segoe UI", 11),
            "borderwidth": 0,
        }
        if anio_ini:
            cal_kwargs["year"] = anio_ini
            cal_kwargs["month"] = mes_ini
            cal_kwargs["day"] = dia_ini

        calendario = Calendar(popup, **cal_kwargs)
        calendario.pack(padx=10, pady=10)

        def on_fecha_seleccionada(_event: Any = None) -> None:
            fecha_elegida = calendario.get_date()
            entry_destino.delete(0, "end")
            entry_destino.insert(0, fecha_elegida)
            popup.destroy()

        calendario.bind("<<CalendarSelected>>", on_fecha_seleccionada)
        popup.bind("<Escape>", lambda _e: popup.destroy())

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

    def _crear_boton_guardar(self) -> None:
        """Botón inferior principal para guardar el acta."""
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 18))

        btn_guardar = ctk.CTkButton(
            frame_acciones,
            text="Guardar Acta",
            width=160,
            height=45,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color=("#059669", "#059669"),
            hover_color=("#047857", "#047857"),
            text_color=("#FFFFFF", "#FFFFFF"),
            command=self._ejecutar_guardado,
        )
        btn_guardar.pack(side="right")

    def _configurar_accesibilidad_focus(self) -> None:
        """Asigna anillos de foco azul a todos los CTkEntry."""
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
        requerido por la capa de servicio.
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

    def _ejecutar_volver(self) -> None:
        """Regresa a la vista de Consulta."""
        if self._on_volver:
            self._on_volver()

    def limpiar_formulario(self) -> None:
        """Limpia todos los campos y restablece los selectores."""
        for entry in (
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
        ):
            entry.delete(0, "end")

        self.combo_sexo.set("")
        self.combo_tipo_parto.set("")

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un cuadro modal de error manteniendo la vista activa."""
        messagebox.showerror("Error", mensaje, parent=self.winfo_toplevel())
