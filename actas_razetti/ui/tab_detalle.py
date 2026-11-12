"""
Módulo de Vista de Detalle / Ficha de Acta de Presentación.
Capa: Presentación / Vista (View en MVC).

Diseño y UX:
- Barra superior con botón "← Volver", título del acta y botón "Copiar Ficha".
- Encabezado Hero destacado con los 4 identificadores clave sobresaliendo arriba:
  [ NO. DE ACTA ]  [ NO. DE LIBRO ]  [ NO. DE FOLIO ]  [ AÑO ]
- Cuerpo espacioso y equilibrado en el mismo orden de llenado de datos:
  1. Datos del Presentante (Declarante) + Fecha de Presentación
  2. Datos del Presentado (Niño/Niña)
  3. Lugar de Nacimiento
- Paleta dinámica adaptable a Modo Claro / Modo Oscuro.
"""

from datetime import datetime
from typing import Any, Callable
import customtkinter as ctk

from utils.iconos import crear_icono_copiar


class TabDetalle(ctk.CTkFrame):
    """
    Vista de solo lectura tipo ficha hospitalaria para visualizar el detalle de un acta.
    """

    def __init__(
        self,
        master: Any,
        on_volver: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self._on_volver = on_volver
        self._datos_actuales: dict[str, Any] = {}
        self._labels_valores: dict[str, ctk.CTkLabel] = {}
        self._labels_hero: dict[str, ctk.CTkLabel] = {}
        self._after_copia_id: str | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._crear_cabecera()
        self._crear_tarjeta_principal()

    def _crear_cabecera(self) -> None:
        """Barra superior con '← Volver', título dinámico y botón de copia rápida."""
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
            border_width=1,
            border_color=("#CBD5E1", "#444444"),
            cursor="hand2",
            command=self._ejecutar_volver,
        )
        self.btn_volver.pack(side="left")

        self.lbl_titulo_acta = ctk.CTkLabel(
            frame_cabecera,
            text="Detalle del Acta",
            font=("Segoe UI", 24, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w",
        )
        self.lbl_titulo_acta.pack(side="left", padx=(16, 0))

        self.icono_copiar = crear_icono_copiar(color=("#1E293B", "#F1F5F9"), size=(18, 18))
        self.btn_copiar = ctk.CTkButton(
            frame_cabecera,
            text="Copiar Ficha",
            image=self.icono_copiar,
            compound="left",
            width=142,
            height=38,
            corner_radius=8,
            font=("Segoe UI", 13, "bold"),
            fg_color=("#F1F5F9", "#2B2B2B"),
            hover_color=("#E2E8F0", "#3A3A3A"),
            text_color=("#1E293B", "#F1F5F9"),
            border_width=2,
            border_color=("#CBD5E1", "#444444"),
            cursor="hand2",
            command=self._copiar_ficha,
        )

    def _crear_tarjeta_principal(self) -> None:
        """Crea la tarjeta principal que alterna entre estado vacío y la ficha completa."""
        self.tarjeta = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=1,
            border_color=("#CBD5E1", "#333333"),
        )
        self.tarjeta.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        self.tarjeta.grid_columnconfigure(0, weight=1)
        self.tarjeta.grid_rowconfigure(0, weight=1)

        # Vista 1: Estado inicial vacío
        self.frame_vacio = ctk.CTkFrame(self.tarjeta, fg_color="transparent")
        self.frame_vacio.grid(row=0, column=0, sticky="nsew")
        self.frame_vacio.grid_columnconfigure(0, weight=1)
        self.frame_vacio.grid_rowconfigure(0, weight=1)

        lbl_vacio = ctk.CTkLabel(
            self.frame_vacio,
            text="Seleccione un acta en la Consulta para ver sus detalles",
            font=("Segoe UI", 16),
            text_color=("#64748B", "#94A3B8"),
        )
        lbl_vacio.grid(row=0, column=0)

        # Vista 2: Ficha completa con espaciado amplio
        self.frame_contenido = ctk.CTkFrame(self.tarjeta, fg_color="transparent")
        self.frame_contenido.grid_columnconfigure(0, weight=1)

        # =====================================================================
        # 1. ZONA SUPERIOR DESTACADA: No. de Acta, No. de Libro, No. de Folio, Año
        # =====================================================================
        frame_hero = ctk.CTkFrame(self.frame_contenido, fg_color="transparent")
        frame_hero.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 6))
        for col in range(4):
            frame_hero.grid_columnconfigure(col, weight=1, uniform="hero_kpi")

        kpis = [
            ("numero_acta", "NO. DE ACTA", True),
            ("numero_libro", "NO. DE LIBRO", False),
            ("numero_folio", "NO. DE FOLIO", False),
            ("anio", "AÑO", False),
        ]
        for idx, (clave, titulo, es_principal) in enumerate(kpis):
            caja = ctk.CTkFrame(
                frame_hero,
                corner_radius=10,
                fg_color=("#1E3A8A", "#1E3A8A") if es_principal else ("#1E293B", "#0F172A"),
                border_width=2,
                border_color=("#2563EB", "#3B82F6") if es_principal else ("#334155", "#334155"),
            )
            caja.grid(row=0, column=idx, sticky="ew", padx=6)

            lbl_kpi_tit = ctk.CTkLabel(
                caja,
                text=titulo,
                font=("Segoe UI", 12, "bold"),
                text_color=("#BFDBFE", "#93C5FD") if es_principal else ("#94A3B8", "#94A3B8"),
                anchor="center",
            )
            lbl_kpi_tit.pack(pady=(7, 0))

            lbl_kpi_val = ctk.CTkLabel(
                caja,
                text="--",
                font=("Segoe UI", 26, "bold"),
                text_color=("#FFFFFF", "#FFFFFF"),
                anchor="center",
            )
            lbl_kpi_val.pack(pady=(0, 7))
            self._labels_hero[clave] = lbl_kpi_val

        # =====================================================================
        # 2. SECCIÓN: Datos del Presentante (Declarante) + Fecha Presentación
        # =====================================================================
        sec_pres = self._crear_seccion(
            self.frame_contenido,
            "Datos del Presentante (Declarante)",
            fila=1,
            weights=(1, 2, 1),
        )
        self._agregar_campo(sec_pres, "presentante_cedula", "C.I.", fila=1, col=0)
        self._agregar_campo(sec_pres, "presentante_nombres", "Nombres y Apellidos", fila=1, col=1)
        self._agregar_campo(sec_pres, "fecha_presentacion", "Fecha de Presentación", fila=1, col=2)

        # =====================================================================
        # 3. SECCIÓN: Datos del Presentado (Niño/Niña)
        # =====================================================================
        sec_nino = self._crear_seccion(
            self.frame_contenido,
            "Datos del Presentado (Niño/Niña)",
            fila=2,
            weights=(1, 1, 1),
        )
        self._agregar_campo(
            sec_nino,
            "presentado_nombres",
            "Nombres y Apellidos",
            fila=1,
            col=0,
            colspan=2,
            pady_bottom=8,
        )
        self._agregar_campo(
            sec_nino,
            "presentado_sexo",
            "Sexo",
            fila=1,
            col=2,
            pady_bottom=8,
        )
        self._agregar_campo(sec_nino, "presentado_fecha_nac", "Fecha de Nacimiento", fila=2, col=0)
        self._agregar_campo(sec_nino, "presentado_hora_nac", "Hora de Nacimiento", fila=2, col=1)
        self._agregar_campo(sec_nino, "presentado_tipo_parto", "Tipo de Parto", fila=2, col=2)

        # =====================================================================
        # 4. SECCIÓN: Lugar de Nacimiento
        # =====================================================================
        sec_lugar = self._crear_seccion(
            self.frame_contenido,
            "Lugar de Nacimiento",
            fila=3,
            weights=(1, 1, 2),
            pady_outer=(6, 10),
        )
        self._agregar_campo(sec_lugar, "estado", "Estado", fila=1, col=0)
        self._agregar_campo(sec_lugar, "ciudad", "Ciudad", fila=1, col=1)
        self._agregar_campo(sec_lugar, "recinto", "Recinto", fila=1, col=2)

    def _crear_seccion(
        self,
        parent: Any,
        titulo: str,
        fila: int,
        weights: tuple[int, ...],
        pady_outer: tuple[int, int] = (6, 6),
    ) -> ctk.CTkFrame:
        """Crea una sección con fondo suave, rejilla uniforme y amplio respiro visual."""
        seccion = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color=("#F1F5F9", "#252525"),
            border_width=1,
            border_color=("#CBD5E1", "#3A3A3A"),
        )
        seccion.grid(row=fila, column=0, sticky="ew", padx=22, pady=pady_outer)

        for col_idx, w in enumerate(weights):
            seccion.grid_columnconfigure(col_idx, weight=w, uniform=f"sec_{fila}_col")

        lbl_titulo = ctk.CTkLabel(
            seccion,
            text=titulo,
            font=("Segoe UI", 15, "bold"),
            text_color=("#1E293B", "#E2E8F0"),
            anchor="w",
        )
        lbl_titulo.grid(row=0, column=0, columnspan=len(weights), sticky="w", padx=16, pady=(8, 4))
        return seccion

    def _agregar_campo(
        self,
        seccion: ctk.CTkFrame,
        clave: str,
        etiqueta: str,
        fila: int,
        col: int,
        colspan: int = 1,
        pady_bottom: int = 9,
    ) -> None:
        """Agrega un campo tipo tarjeta (etiqueta arriba, caja amplia con valor abajo)."""
        contenedor = ctk.CTkFrame(seccion, fg_color="transparent")
        pad_left = 16 if col == 0 else 10
        pad_right = 16 if (col + colspan) >= 3 else 10
        contenedor.grid(
            row=fila,
            column=col,
            columnspan=colspan,
            sticky="ew",
            padx=(pad_left, pad_right),
            pady=(0, pady_bottom),
        )

        lbl_etq = ctk.CTkLabel(
            contenedor,
            text=f"{etiqueta}:",
            font=("Segoe UI", 12, "bold"),
            text_color=("#475569", "#94A3B8"),
            anchor="w",
        )
        lbl_etq.pack(anchor="w", pady=(0, 3))

        caja_valor = ctk.CTkFrame(
            contenedor,
            height=42,
            corner_radius=8,
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=2,
            border_color=("#94A3B8", "#475569"),
        )
        caja_valor.pack(fill="x")
        caja_valor.pack_propagate(False)

        lbl_val = ctk.CTkLabel(
            caja_valor,
            text="--",
            font=("Segoe UI", 15, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w",
        )
        lbl_val.pack(side="left", padx=12, pady=3, fill="both", expand=True)
        self._labels_valores[clave] = lbl_val

    # -------------------------------------------------------------------------
    # Formateo y Carga de Datos
    # -------------------------------------------------------------------------
    @staticmethod
    def _formatear_valor(datos: dict[str, Any], clave: str, defecto: str = "No especificado") -> str:
        val = datos.get(clave)
        if val is None or str(val).strip() == "":
            return defecto
        return str(val).strip()

    @staticmethod
    def _formatear_fecha(valor: str) -> str:
        if valor in ("No especificado", "--", ""):
            return valor
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(valor, fmt)
                return dt.strftime("%d/%m/%Y %I:%M %p") if " " in fmt else dt.strftime("%d/%m/%Y")
            except ValueError:
                continue
        return valor

    @staticmethod
    def _formatear_hora(valor: str) -> str:
        if valor in ("No especificado", "--", ""):
            return valor
        try:
            return datetime.strptime(valor, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            return valor

    def cargar_datos(self, datos: dict[str, Any]) -> None:
        """
        Actualiza el encabezado destacado (Acta, Libro, Folio, Año) y todos los
        bloques de información respetando el orden natural de llenado.
        """
        if not datos:
            self.limpiar()
            return

        self._datos_actuales = dict(datos)

        for clave, lbl in self._labels_hero.items():
            lbl.configure(text=self._formatear_valor(datos, clave, "--"))

        for clave, lbl in self._labels_valores.items():
            if clave == "presentante_cedula":
                valor_fmt = self._formatear_valor(datos, clave, "S/C")
            elif clave in ("fecha_presentacion", "presentado_fecha_nac"):
                valor_fmt = self._formatear_fecha(self._formatear_valor(datos, clave))
            elif clave == "presentado_hora_nac":
                valor_fmt = self._formatear_hora(self._formatear_valor(datos, clave))
            else:
                valor_fmt = self._formatear_valor(datos, clave)
            lbl.configure(text=valor_fmt)

        self.frame_vacio.grid_forget()
        self.frame_contenido.grid(row=0, column=0, sticky="nsew")
        self.btn_copiar.pack(side="right")

    def limpiar(self) -> None:
        """Restaura el estado inicial vacío de la vista Detalle."""
        self._datos_actuales = {}
        self.lbl_titulo_acta.configure(text="Detalle del Acta")
        self.btn_copiar.pack_forget()
        self.frame_contenido.grid_forget()
        self.frame_vacio.grid(row=0, column=0, sticky="nsew")

    def _ejecutar_volver(self) -> None:
        if self._on_volver:
            self._on_volver()

    def _copiar_ficha(self) -> None:
        """Copia un resumen legible del acta al portapapeles."""
        if not self._datos_actuales:
            return

        d = self._datos_actuales
        resumen = (
            f"ACTA DE PRESENTACIÓN Nº {self._formatear_valor(d, 'numero_acta')} ({self._formatear_valor(d, 'anio')})\n"
            f"Libro: {self._formatear_valor(d, 'numero_libro')} | Folio: {self._formatear_valor(d, 'numero_folio')} | "
            f"Fecha Presentación: {self._formatear_fecha(self._formatear_valor(d, 'fecha_presentacion'))}\n"
            f"Presentante: {self._formatear_valor(d, 'presentante_nombres')} "
            f"(C.I.: {self._formatear_valor(d, 'presentante_cedula', 'S/C')})\n"
            f"Presentado: {self._formatear_valor(d, 'presentado_nombres')} "
            f"({self._formatear_valor(d, 'presentado_sexo')}, Parto {self._formatear_valor(d, 'presentado_tipo_parto')})\n"
            f"Nacimiento: {self._formatear_fecha(self._formatear_valor(d, 'presentado_fecha_nac'))} "
            f"a las {self._formatear_hora(self._formatear_valor(d, 'presentado_hora_nac'))}\n"
            f"Lugar: {self._formatear_valor(d, 'recinto')}, {self._formatear_valor(d, 'ciudad')}, "
            f"{self._formatear_valor(d, 'estado')}"
        )

        self.clipboard_clear()
        self.clipboard_append(resumen)
        self.update_idletasks()

        if self._after_copia_id is not None:
            self.after_cancel(self._after_copia_id)
        self.btn_copiar.configure(text="✓ Copiado")
        self._after_copia_id = self.after(1800, self._restaurar_texto_copiar)

    def _restaurar_texto_copiar(self) -> None:
        self._after_copia_id = None
        if self.winfo_exists():
            self.btn_copiar.configure(text="Copiar Ficha")
