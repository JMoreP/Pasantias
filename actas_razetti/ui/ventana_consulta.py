"""
Módulo de Ventana Principal con Navegación por Vistas Apiladas y Soporte Claro/Oscuro.
Capa: Presentación / Vista (View en MVC).

Diseño y UX:
- Barra superior persistente con switch "Modo Oscuro" siempre visible en todas las vistas.
- Navegación limpia por vistas apiladas (Consulta, Registro y Detalle) sin barra de pestañas.
- Paleta dinámica completa (Light/Dark) con tuplas de CustomTkinter y reestilización
  en tiempo real de ttk.Treeview e íconos vectoriales.
"""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
import customtkinter as ctk
from customtkinter.windows.widgets.core_rendering import DrawEngine
from tkcalendar import Calendar

from ui.tab_detalle import TabDetalle
from ui.tab_registro import TabRegistro
from utils.iconos import (
    crear_icono_documento_plus,
    crear_icono_limpiar,
    crear_icono_lupa,
)


class VentanaConsulta(ctk.CTk):
    """
    Ventana principal del sistema con intercambio interno de vistas y tema Claro/Oscuro.
    """

    COLOR_BORDE_INACTIVO = ("#94A3B8", "#52525B")
    COLOR_BORDE_ACTIVO = ("#2563EB", "#3B82F6")

    def __init__(self) -> None:
        super().__init__()

        # Vectorial nativo para esquinas continuas sin recortes en Linux/X11
        DrawEngine.preferred_drawing_method = "circle_shapes"
        # Modo claro por defecto al arrancar
        ctk.set_appearance_mode("light")

        self.controlador: Any = None
        self._esta_cargando: bool = False
        self._popup_calendario: tk.Toplevel | None = None
        self.vista_actual: str = "Consulta"

        # 1. Configuración de Ventana
        self.title("CONSULTA DE ACTAS DE PRESENTACION")
        self.configure(fg_color=("#EEF2F6", "#121212"))
        self._centrar_ventana(ancho=1260, alto=860)
        self.minsize(1120, 750)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 2. Barra superior persistente (Switch Modo Oscuro) + Vistas Apiladas
        self._aplicar_estilos_treeview()
        self._crear_barra_superior_global()
        self._crear_contenedor_vistas()
        self._actualizar_estilos_tabla()
        self._configurar_accesibilidad_focus()

    def _centrar_ventana(self, ancho: int, alto: int) -> None:
        """Centra la ventana principal en la pantalla del usuario."""
        pantalla_w = self.winfo_screenwidth()
        pantalla_h = self.winfo_screenheight()
        pos_x = max(0, (pantalla_w - ancho) // 2)
        pos_y = max(0, (pantalla_h - alto) // 2)
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    def _crear_barra_superior_global(self) -> None:
        """Barra superior persistente con el switch de Modo Oscuro visible en todo momento."""
        barra_top = ctk.CTkFrame(self, fg_color="transparent")
        barra_top.grid(row=0, column=0, sticky="ew", padx=24, pady=(12, 0))

        lbl_sistema = ctk.CTkLabel(
            barra_top,
            text='Hospital "Doctor Luis Razetti" — Sistema de Actas',
            font=("Segoe UI", 12, "bold"),
            text_color=("#64748B", "#94A3B8"),
            anchor="w",
        )
        lbl_sistema.pack(side="left")

        self.var_modo_oscuro = ctk.BooleanVar(value=False)
        self.switch_tema = ctk.CTkSwitch(
            barra_top,
            text="Modo Oscuro",
            variable=self.var_modo_oscuro,
            font=("Segoe UI", 13, "bold"),
            text_color=("#0F172A", "#E2E8F0"),
            fg_color=("#CBD5E1", "#475569"),
            progress_color=("#2563EB", "#3B82F6"),
            button_color=("#FFFFFF", "#F8FAFC"),
            button_hover_color=("#F1F5F9", "#E2E8F0"),
            command=self._cambiar_tema,
        )
        self.switch_tema.pack(side="right")

    def _cambiar_tema(self) -> None:
        """Alterna entre modo claro y oscuro y actualiza los estilos de la tabla."""
        if self.var_modo_oscuro.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self._actualizar_estilos_tabla()

    def _aplicar_estilos_treeview(self) -> None:
        """Inicializa el layout base del ttk.Treeview."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.layout("ActasModernas.Treeview", [
                     ("Treeview.treearea", {"sticky": "nswe"})])

    def _actualizar_estilos_tabla(self) -> None:
        """
        Detecta el modo actual ('Light' o 'Dark') y reconfigura dinámicamente
        el ttk.Treeview, sus encabezados, la selección y las filas alternas.
        """
        es_oscuro = str(ctk.get_appearance_mode()).lower() == "dark"

        if es_oscuro:
            bg_tabla = "#1E1E1E"
            bg_impar = "#2B2B2B"
            fg_texto = "#E2E8F0"
            bg_heading = "#333333"
            bg_heading_activo = "#444444"
            fg_heading = "#F8FAFC"
            bg_seleccion = "#2563EB"
            fg_seleccion = "#FFFFFF"
        else:
            bg_tabla = "#FFFFFF"
            bg_impar = "#F8FAFC"
            fg_texto = "#0F172A"
            bg_heading = "#E2E8F0"
            bg_heading_activo = "#CBD5E1"
            fg_heading = "#1E293B"
            bg_seleccion = "#2563EB"
            fg_seleccion = "#FFFFFF"

        style = ttk.Style()
        style.configure(
            "ActasModernas.Treeview.Heading",
            font=("Segoe UI", 12, "bold"),
            background=bg_heading,
            foreground=fg_heading,
            relief="flat",
            borderwidth=0,
            padding=(10, 10),
        )
        style.map(
            "ActasModernas.Treeview.Heading",
            background=[("active", bg_heading_activo)],
            foreground=[("active", fg_heading)],
        )

        style.configure(
            "ActasModernas.Treeview",
            font=("Segoe UI", 13),
            rowheight=40,
            background=bg_tabla,
            fieldbackground=bg_tabla,
            foreground=fg_texto,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "ActasModernas.Treeview",
            background=[("selected", bg_seleccion)],
            foreground=[("selected", fg_seleccion)],
        )

        if hasattr(self, "tree"):
            self.tree.tag_configure("par", background=bg_tabla, foreground=fg_texto)
            self.tree.tag_configure("impar", background=bg_impar, foreground=fg_texto)

    def _crear_contenedor_vistas(self) -> None:
        """Crea el contenedor de vistas apiladas y construye Consulta, Registro y Detalle."""
        self.contenedor_vistas = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_vistas.grid(row=1, column=0, sticky="nsew")
        self.contenedor_vistas.grid_columnconfigure(0, weight=1)
        self.contenedor_vistas.grid_rowconfigure(0, weight=1)

        # 1. Vista Consulta
        self.vista_consulta = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        self.vista_consulta.grid_columnconfigure(0, weight=1)
        self.vista_consulta.grid_rowconfigure(2, weight=1)

        self._crear_cabecera(self.vista_consulta)
        self._crear_tarjeta_filtros_y_acciones(self.vista_consulta)
        self._crear_panel_tabla(self.vista_consulta)
        self._crear_barra_estado(self.vista_consulta)

        # 2. Vista Registro
        self.tab_registro = TabRegistro(
            self.contenedor_vistas,
            controlador=self.controlador,
            on_volver=lambda: self.mostrar_vista("Consulta"),
        )

        # 3. Vista Detalle
        self.tab_detalle = TabDetalle(
            self.contenedor_vistas,
            on_volver=lambda: self.mostrar_vista("Consulta"),
        )

        self.mostrar_vista("Consulta")

    def mostrar_vista(self, nombre: str) -> None:
        """Intercambia la vista activa dentro de la ventana sin perder el estado de Consulta."""
        nombre_norm = nombre.strip().lower()
        mapa_vistas = {
            "consulta": ("Consulta", self.vista_consulta),
            "registro": ("Registro", self.tab_registro),
            "detalle": ("Detalle", self.tab_detalle),
        }
        entrada = mapa_vistas.get(nombre_norm)
        if entrada is None:
            return

        nombre_canonico, vista_objetivo = entrada
        for clave, (_, frame) in mapa_vistas.items():
            if clave != nombre_norm:
                frame.grid_forget()

        vista_objetivo.grid(row=0, column=0, sticky="nsew")
        self.vista_actual = nombre_canonico

        if nombre_norm == "registro":
            self.tab_registro.enfocar_inicio()

    def cambiar_pestana(self, nombre: str) -> None:
        """Alias de compatibilidad para navegación de vistas."""
        self.mostrar_vista(nombre)

    # -------------------------------------------------------------------------
    # Vista Consulta: Cabecera, Filtros, Botones, Tabla y Barra de Estado
    # -------------------------------------------------------------------------
    def _crear_cabecera(self, parent: Any) -> None:
        """Cabecera institucional de Consulta."""
        frame_cabecera = ctk.CTkFrame(parent, fg_color="transparent")
        frame_cabecera.grid(row=0, column=0, sticky="ew", padx=24, pady=(8, 8))

        label_titulo = ctk.CTkLabel(
            frame_cabecera,
            text="Consulta de Actas de Presentación",
            font=("Segoe UI", 26, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w",
        )
        label_titulo.pack(anchor="w")

        label_subtitulo = ctk.CTkLabel(
            frame_cabecera,
            text="CONSULTA",
            font=("Segoe UI", 13),
            text_color=("#64748B", "#94A3B8"),
            anchor="w",
        )
        label_subtitulo.pack(anchor="w", pady=(2, 0))

    def _crear_tarjeta_filtros_y_acciones(self, parent: Any) -> None:
        """Tarjeta de filtros a la izquierda y botones cuadrados a la derecha."""
        self.tarjeta_filtros = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=1,
            border_color=("#CBD5E1", "#333333"),
        )
        self.tarjeta_filtros.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))

        self.tarjeta_filtros.grid_columnconfigure(0, weight=1)
        self.tarjeta_filtros.grid_columnconfigure(1, weight=0)

        frame_formulario = ctk.CTkFrame(self.tarjeta_filtros, fg_color="transparent")
        frame_formulario.grid(row=0, column=0, sticky="nsew", padx=(18, 10), pady=16)
        frame_formulario.grid_columnconfigure(0, weight=1)

        # 1. Fila General: No. de Acta + Checkbox Todas
        frame_general = ctk.CTkFrame(frame_formulario, fg_color="transparent")
        frame_general.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 6))

        lbl_acta = ctk.CTkLabel(
            frame_general,
            text="No. de Acta:",
            font=("Segoe UI", 15, "bold"),
            text_color=("#1E293B", "#E2E8F0"),
        )
        lbl_acta.pack(side="left", padx=(0, 12))

        self.entry_acta = ctk.CTkEntry(
            frame_general,
            width=150,
            height=45,
            font=("Segoe UI", 15),
            border_width=2,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color=("#FFFFFF", "#2B2B2B"),
            text_color=("#0F172A", "#E2E8F0"),
        )
        self.entry_acta.pack(side="left", padx=(0, 16))
        self.entry_acta.bind("<KeyRelease>", self._on_escribir_acta)

        self.var_todas = ctk.BooleanVar(value=False)
        self.chk_todas = ctk.CTkCheckBox(
            frame_general,
            text="Todas",
            variable=self.var_todas,
            font=("Segoe UI", 14),
            text_color=("#334155", "#E2E8F0"),
            border_color=("#64748B", "#64748B"),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4,
            command=self._on_toggle_todas,
        )
        self.chk_todas.pack(side="left")

        # 2. Recuadro: Datos de Presentante
        box_presentante = ctk.CTkFrame(
            frame_formulario,
            corner_radius=8,
            fg_color=("#F1F5F9", "#252525"),
            border_width=1,
            border_color=("#CBD5E1", "#3A3A3A"),
        )
        box_presentante.grid(row=1, column=0, sticky="ew", padx=4, pady=6)
        box_presentante.grid_columnconfigure(0, weight=1)
        box_presentante.grid_columnconfigure(1, weight=3)

        lbl_tit_pres = ctk.CTkLabel(
            box_presentante,
            text="Datos de Presentante:",
            font=("Segoe UI", 16, "bold"),
            text_color=("#1E293B", "#E2E8F0"),
            anchor="w",
        )
        lbl_tit_pres.grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 4))

        col_ci = ctk.CTkFrame(box_presentante, fg_color="transparent")
        col_ci.grid(row=1, column=0, sticky="ew", padx=(16, 12), pady=(0, 12))

        lbl_ci = ctk.CTkLabel(
            col_ci,
            text="C.I.",
            font=("Segoe UI", 15, "bold"),
            text_color=("#475569", "#CBD5E1"),
        )
        lbl_ci.pack(anchor="w", pady=(0, 4))

        self.entry_ci = ctk.CTkEntry(
            col_ci,
            height=45,
            font=("Segoe UI", 15),
            border_width=2,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color=("#FFFFFF", "#2B2B2B"),
            text_color=("#0F172A", "#E2E8F0"),
        )
        self.entry_ci.pack(fill="x")

        col_nom_pres = ctk.CTkFrame(box_presentante, fg_color="transparent")
        col_nom_pres.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=(0, 12))

        lbl_nom_pres = ctk.CTkLabel(
            col_nom_pres,
            text="NOMBRE:",
            font=("Segoe UI", 15, "bold"),
            text_color=("#475569", "#CBD5E1"),
        )
        lbl_nom_pres.pack(anchor="w", pady=(0, 4))

        self.entry_presentante_nombres = ctk.CTkEntry(
            col_nom_pres,
            height=45,
            font=("Segoe UI", 15),
            border_width=2,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color=("#FFFFFF", "#2B2B2B"),
            text_color=("#0F172A", "#E2E8F0"),
        )
        self.entry_presentante_nombres.pack(fill="x")

        # 3. Recuadro: Datos de Presentado
        box_presentado = ctk.CTkFrame(
            frame_formulario,
            corner_radius=8,
            fg_color=("#F1F5F9", "#252525"),
            border_width=1,
            border_color=("#CBD5E1", "#3A3A3A"),
        )
        box_presentado.grid(row=2, column=0, sticky="ew", padx=4, pady=6)
        box_presentado.grid_columnconfigure(0, weight=2)
        box_presentado.grid_columnconfigure(1, weight=1)
        box_presentado.grid_columnconfigure(2, weight=1)

        lbl_tit_nino = ctk.CTkLabel(
            box_presentado,
            text="Datos de Presentado:",
            font=("Segoe UI", 16, "bold"),
            text_color=("#1E293B", "#E2E8F0"),
            anchor="w",
        )
        lbl_tit_nino.grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(10, 4))

        col_nom_nino = ctk.CTkFrame(box_presentado, fg_color="transparent")
        col_nom_nino.grid(row=1, column=0, sticky="ew", padx=(16, 12), pady=(0, 12))

        lbl_nom_nino = ctk.CTkLabel(
            col_nom_nino,
            text="NOMBRE:",
            font=("Segoe UI", 15, "bold"),
            text_color=("#475569", "#CBD5E1"),
        )
        lbl_nom_nino.pack(anchor="w", pady=(0, 4))

        self.entry_presentado_nombres = ctk.CTkEntry(
            col_nom_nino,
            height=45,
            font=("Segoe UI", 15),
            border_width=2,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color=("#FFFFFF", "#2B2B2B"),
            text_color=("#0F172A", "#E2E8F0"),
        )
        self.entry_presentado_nombres.pack(fill="x")

        col_desde = ctk.CTkFrame(box_presentado, fg_color="transparent")
        col_desde.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(0, 12))

        lbl_desde = ctk.CTkLabel(
            col_desde,
            text="Desde:",
            font=("Segoe UI", 15, "bold"),
            text_color=("#475569", "#CBD5E1"),
        )
        lbl_desde.pack(anchor="w", pady=(0, 4))

        subframe_desde, self.entry_desde, self.btn_cal_desde = self._crear_campo_fecha_moderno(col_desde)
        subframe_desde.pack(fill="x")

        col_hasta = ctk.CTkFrame(box_presentado, fg_color="transparent")
        col_hasta.grid(row=1, column=2, sticky="ew", padx=(0, 16), pady=(0, 12))

        lbl_hasta = ctk.CTkLabel(
            col_hasta,
            text="Hasta:",
            font=("Segoe UI", 15, "bold"),
            text_color=("#475569", "#CBD5E1"),
        )
        lbl_hasta.pack(anchor="w", pady=(0, 4))

        subframe_hasta, self.entry_hasta, self.btn_cal_hasta = self._crear_campo_fecha_moderno(col_hasta)
        subframe_hasta.pack(fill="x")

        # Subframe Vertical de Botones CUADRADOS (120x120)
        frame_botones = ctk.CTkFrame(self.tarjeta_filtros, fg_color="transparent")
        frame_botones.grid(row=0, column=1, sticky="ns", padx=(10, 20), pady=16)

        self.icono_buscar = crear_icono_lupa(color="#FFFFFF", size=(28, 28))
        self.btn_buscar = ctk.CTkButton(
            frame_botones,
            text="Buscar",
            image=self.icono_buscar,
            compound="top",
            font=("Segoe UI", 14, "bold"),
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#FFFFFF", "#FFFFFF"),
            width=120,
            height=120,
            corner_radius=8,
            command=self._ejecutar_busqueda,
        )
        self.btn_buscar.pack(side="top", pady=10, fill="none")

        self.icono_limpiar = crear_icono_limpiar(color=("#0F172A", "#E2E8F0"), size=(28, 28))
        self.btn_limpiar = ctk.CTkButton(
            frame_botones,
            text="Limpiar",
            image=self.icono_limpiar,
            compound="top",
            font=("Segoe UI", 14, "bold"),
            fg_color=("#E2E8F0", "#333333"),
            hover_color=("#CBD5E1", "#444444"),
            text_color=("#0F172A", "#E2E8F0"),
            width=120,
            height=120,
            corner_radius=8,
            command=self._ejecutar_limpieza,
        )
        self.btn_limpiar.pack(side="top", pady=10, fill="none")

        self.icono_registrar = crear_icono_documento_plus(color="#FFFFFF", size=(28, 28))
        self.btn_nuevo = ctk.CTkButton(
            frame_botones,
            text="Registrar",
            image=self.icono_registrar,
            compound="top",
            font=("Segoe UI", 14, "bold"),
            fg_color=("#059669", "#059669"),
            hover_color=("#047857", "#047857"),
            text_color=("#FFFFFF", "#FFFFFF"),
            width=120,
            height=120,
            corner_radius=8,
            command=self._ejecutar_nuevo,
        )
        self.btn_nuevo.pack(side="top", pady=10, fill="none")

        for entry in (
            self.entry_acta,
            self.entry_ci,
            self.entry_presentante_nombres,
            self.entry_presentado_nombres,
            self.entry_desde,
            self.entry_hasta,
        ):
            entry.bind("<Return>", lambda _event: self._ejecutar_busqueda())

    def _crear_campo_fecha_moderno(
        self, parent: Any
    ) -> tuple[ctk.CTkFrame, ctk.CTkEntry, ctk.CTkButton]:
        """Crea un control de fecha compuesto (CTkEntry + botón cuadrado 📅)."""
        frame_compuesto = ctk.CTkFrame(parent, fg_color="transparent")

        entry = ctk.CTkEntry(
            frame_compuesto,
            height=45,
            font=("Segoe UI", 15),
            border_width=2,
            corner_radius=8,
            border_color=self.COLOR_BORDE_INACTIVO,
            fg_color=("#FFFFFF", "#2B2B2B"),
            text_color=("#0F172A", "#E2E8F0"),
            placeholder_text="YYYY-MM-DD",
            placeholder_text_color=("#94A3B8", "#94A3B8"),
        )
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
            border_width=1,
            border_color=("#CBD5E1", "#444444"),
            corner_radius=8,
        )
        btn_cal.configure(command=lambda e=entry, b=btn_cal: self._abrir_calendario(e, b))
        btn_cal.pack(side="right")

        return frame_compuesto, entry, btn_cal

    def _abrir_calendario(self, entry_destino: ctk.CTkEntry, boton_invocador: ctk.CTkButton) -> None:
        """Abre el widget Calendar de tkcalendar adaptado al modo actual."""
        if self._popup_calendario is not None and self._popup_calendario.winfo_exists():
            self._popup_calendario.destroy()

        es_oscuro = str(ctk.get_appearance_mode()).lower() == "dark"
        popup = tk.Toplevel(self)
        self._popup_calendario = popup
        popup.title("Seleccionar Fecha")
        popup.transient(self)
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

    def _crear_panel_tabla(self, parent: Any) -> None:
        """Tarjeta inferior con la tabla de resultados ttk.Treeview."""
        frame_tabla = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=1,
            border_color=("#CBD5E1", "#333333"),
        )
        frame_tabla.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 10))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        columnas = (
            "id",
            "numero_acta",
            "fecha_presentacion",
            "presentado_nombres",
            "presentante_nombres",
        )
        columnas_visibles = (
            "numero_acta",
            "fecha_presentacion",
            "presentado_nombres",
            "presentante_nombres",
        )

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            displaycolumns=columnas_visibles,
            show="headings",
            selectmode="browse",
            style="ActasModernas.Treeview",
        )

        self.tree.heading("numero_acta", text="Acta", anchor="center")
        self.tree.column("numero_acta", width=90, minwidth=70, anchor="center")

        self.tree.heading("fecha_presentacion", text="Fecha P", anchor="center")
        self.tree.column("fecha_presentacion", width=130, minwidth=100, anchor="center")

        self.tree.heading("presentado_nombres", text="PRESENTADO", anchor="w")
        self.tree.column("presentado_nombres", width=360, minwidth=240, anchor="w")

        self.tree.heading("presentante_nombres", text="PRESENTANTE", anchor="w")
        self.tree.column("presentante_nombres", width=360, minwidth=240, anchor="w")

        self.scrollbar = ctk.CTkScrollbar(frame_tabla, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=12)

        self.tree.bind("<Double-1>", self._on_doble_click_fila)

    def _crear_barra_estado(self, parent: Any) -> None:
        """Barra de estado situada en la base de la vista Consulta."""
        frame_estado = ctk.CTkFrame(parent, height=28, fg_color="transparent")
        frame_estado.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 12))

        self.label_estado = ctk.CTkLabel(
            frame_estado,
            text="0 actas encontradas",
            font=("Segoe UI", 12),
            text_color=("#64748B", "#94A3B8"),
            anchor="w",
        )
        self.label_estado.pack(side="left")

    def _configurar_accesibilidad_focus(self) -> None:
        """Asigna anillos de foco azul a todos los CTkEntry de Consulta."""
        entradas = (
            self.entry_acta,
            self.entry_ci,
            self.entry_presentante_nombres,
            self.entry_presentado_nombres,
            self.entry_desde,
            self.entry_hasta,
        )
        for entry in entradas:
            entry.bind("<FocusIn>", lambda _event, w=entry: self._on_focus_in(w))
            entry.bind("<FocusOut>", lambda _event, w=entry: self._on_focus_out(w))

    def _on_focus_in(self, widget: ctk.CTkEntry) -> None:
        widget.configure(border_color=self.COLOR_BORDE_ACTIVO, border_width=2)

    def _on_focus_out(self, widget: ctk.CTkEntry) -> None:
        widget.configure(border_color=self.COLOR_BORDE_INACTIVO, border_width=2)

    def establecer_estado_cargando(self, cargando: bool) -> None:
        """Controla el feedback visual durante la búsqueda."""
        self._esta_cargando = cargando
        if cargando:
            self.btn_buscar.configure(state="disabled", text="Buscando...")
            self.configure(cursor="watch")
        else:
            self.btn_buscar.configure(state="normal", text="Buscar")
            self.configure(cursor="")
        self.update_idletasks()

    # -------------------------------------------------------------------------
    # Eventos y Delegación al Controlador
    # -------------------------------------------------------------------------
    def _on_toggle_todas(self) -> None:
        if self.var_todas.get():
            self.entry_acta.delete(0, "end")

    def _on_escribir_acta(self, _event: Any = None) -> None:
        if self.entry_acta.get().strip():
            self.var_todas.set(False)

    def _construir_filtros(self) -> dict[str, str]:
        """Recolecta los filtros del formulario aplicando la regla del checkbox."""
        texto_acta = self.entry_acta.get().strip()
        if texto_acta:
            numero_acta = texto_acta
            if self.var_todas.get():
                self.var_todas.set(False)
        else:
            numero_acta = ""

        return {
            "numero_acta": numero_acta,
            "presentante_cedula": self.entry_ci.get().strip(),
            "presentante_nombres": self.entry_presentante_nombres.get().strip(),
            "presentado_nombres": self.entry_presentado_nombres.get().strip(),
            "fecha_desde": self.entry_desde.get().strip(),
            "fecha_hasta": self.entry_hasta.get().strip(),
        }

    def _ejecutar_busqueda(self) -> None:
        if self._esta_cargando:
            return

        self.establecer_estado_cargando(True)
        filtros = self._construir_filtros()

        try:
            if self.controlador:
                self.controlador.buscar(filtros)
        finally:
            self.establecer_estado_cargando(False)

    def _ejecutar_limpieza(self) -> None:
        if self.controlador:
            self.controlador.limpiar_filtros()
        else:
            self.limpiar_formulario()

    def _ejecutar_nuevo(self) -> None:
        """Solicita al controlador navegar a la vista de Registro."""
        if self.controlador:
            self.controlador.abrir_registro()

    def _on_doble_click_fila(self, _event: Any) -> None:
        """Captura el doble clic en la tabla y navega a Detalle."""
        seleccion = self.tree.selection()
        if not seleccion:
            return

        item_id = seleccion[0]
        valores = self.tree.item(item_id, "values")
        if valores and len(valores) > 0:
            id_acta = int(valores[0])
            if self.controlador:
                self.controlador.abrir_detalle(id_acta)

    # -------------------------------------------------------------------------
    # Métodos Públicos (Consumidos por el Controlador)
    # -------------------------------------------------------------------------
    def asignar_controlador(self, controlador: Any) -> None:
        """Asigna el controlador e inicializa la tabla en estado vacío."""
        self.controlador = controlador
        self.tab_registro.asignar_controlador(controlador)
        self.pintar_resultados([])

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra cuadro modal de error asegurando el fin del estado de carga."""
        self.establecer_estado_cargando(False)
        messagebox.showerror("Error", mensaje, parent=self)

    def mostrar_info(self, mensaje: str) -> None:
        """Muestra cuadro modal informativo."""
        messagebox.showinfo("Información", mensaje, parent=self)

    def pintar_resultados(self, lista: list[dict]) -> None:
        """Puebla el Treeview con zebra striping y actualiza el conteo de resultados."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = len(lista)
        for indice, acta in enumerate(lista):
            tag_color = "par" if indice % 2 == 0 else "impar"
            valores = (
                acta.get("id", ""),
                acta.get("numero_acta", ""),
                acta.get("fecha_presentacion", ""),
                acta.get("presentado_nombres", ""),
                acta.get("presentante_nombres", ""),
            )
            self.tree.insert("", "end", values=valores, tags=(tag_color,))

        if total == 1:
            self.label_estado.configure(text="1 acta encontrada")
        else:
            self.label_estado.configure(text=f"{total} actas encontradas")

        self._actualizar_estilos_tabla()
        self.establecer_estado_cargando(False)

    def limpiar_formulario(self) -> None:
        """Restablece los inputs de Consulta, desmarca 'Todas' y vacía la tabla."""
        self.entry_acta.delete(0, "end")
        self.var_todas.set(False)
        self.entry_ci.delete(0, "end")
        self.entry_presentante_nombres.delete(0, "end")
        self.entry_presentado_nombres.delete(0, "end")
        self.entry_desde.delete(0, "end")
        self.entry_hasta.delete(0, "end")

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.label_estado.configure(text="0 actas encontradas")
        self.entry_acta.focus_set()
