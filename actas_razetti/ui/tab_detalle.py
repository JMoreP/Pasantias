"""
Módulo de Vista de Detalle de Acta de Presentación.
Capa: Presentación / Vista (View en MVC).

Diseño y UX:
- Componente CTkFrame integrado en la ventana principal (navegación por vistas apiladas).
- Paleta 100% adaptable a Modo Claro / Modo Oscuro mediante tuplas dinámicas de CustomTkinter.
- Barra superior con botón de retroceso "← Volver" arriba a la izquierda y el título
  dinámico "Acta Nº {numero_acta} - {anio}".
- Tarjeta con 4 secciones visuales, etiquetas ("Campo:") a la izquierda
  y valores en negrita a la derecha.
"""

from typing import Any, Callable
import customtkinter as ctk


class TabDetalle(ctk.CTkFrame):
    """
    Vista de solo lectura para visualizar los detalles completos de un acta.
    """

    def __init__(
        self,
        master: Any,
        on_volver: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self._on_volver = on_volver
        self._labels_valores: dict[str, ctk.CTkLabel] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._crear_cabecera()
        self._crear_tarjeta_principal()

    def _crear_cabecera(self) -> None:
        """Barra superior con botón de retroceso arriba a la izquierda y título del acta."""
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

        self.lbl_titulo_acta = ctk.CTkLabel(
            frame_cabecera,
            text="Detalle del Acta",
            font=("Segoe UI", 24, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w",
        )
        self.lbl_titulo_acta.pack(side="left", padx=(16, 0))

    def _crear_tarjeta_principal(self) -> None:
        """Crea la tarjeta principal que alterna entre estado vacío y el detalle del acta."""
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

        # Vista 2: Contenido completo del acta (oculta inicialmente)
        self.frame_contenido = ctk.CTkFrame(self.tarjeta, fg_color="transparent")
        self.frame_contenido.grid_columnconfigure(0, weight=1)

        # 1. Datos del Libro
        self._crear_seccion(
            self.frame_contenido,
            "Datos del Libro",
            fila=0,
            campos=[
                ("numero_libro", "Libro"),
                ("numero_folio", "Folio"),
                ("fecha_presentacion", "Fecha de Presentación"),
            ],
        )

        # 2. Datos del Presentante
        self._crear_seccion(
            self.frame_contenido,
            "Datos del Presentante",
            fila=1,
            campos=[
                ("presentante_cedula", "C.I."),
                ("presentante_nombres", "Nombres"),
            ],
        )

        # 3. Datos del Presentado
        self._crear_seccion(
            self.frame_contenido,
            "Datos del Presentado",
            fila=2,
            campos=[
                ("presentado_nombres", "Nombres"),
                ("presentado_sexo", "Sexo"),
                ("presentado_fecha_nac", "Fecha Nac."),
                ("presentado_hora_nac", "Hora Nac."),
                ("presentado_tipo_parto", "Tipo Parto"),
            ],
        )

        # 4. Lugar de Nacimiento
        self._crear_seccion(
            self.frame_contenido,
            "Lugar de Nacimiento",
            fila=3,
            campos=[
                ("estado", "Estado"),
                ("ciudad", "Ciudad"),
                ("recinto", "Recinto"),
            ],
        )

    def _crear_seccion(
        self,
        parent: Any,
        titulo: str,
        fila: int,
        campos: list[tuple[str, str]],
    ) -> None:
        """
        Crea una sección visual con borde sutil y registra las etiquetas de valor
        para actualizaciones dinámicas sin reconstruir widgets.
        """
        seccion = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=("#F1F5F9", "#252525"),
            border_width=1,
            border_color=("#CBD5E1", "#3A3A3A"),
        )
        pad_top = 18 if fila == 0 else 7
        seccion.grid(row=fila, column=0, sticky="ew", padx=18, pady=(pad_top, 7))
        seccion.grid_columnconfigure(0, weight=1)
        seccion.grid_columnconfigure(1, weight=1)

        lbl_titulo = ctk.CTkLabel(
            seccion,
            text=titulo,
            font=("Segoe UI", 15, "bold"),
            text_color=("#1E293B", "#E2E8F0"),
            anchor="w",
        )
        lbl_titulo.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 6))

        for idx, (clave, etiqueta) in enumerate(campos):
            fila_campo = (idx // 2) + 1
            col_campo = idx % 2

            contenedor_par = ctk.CTkFrame(seccion, fg_color="transparent")
            pad_x = (14, 10) if col_campo == 0 else (10, 14)
            pad_bottom = 12 if idx >= len(campos) - 2 else 4
            contenedor_par.grid(
                row=fila_campo,
                column=col_campo,
                sticky="ew",
                padx=pad_x,
                pady=(2, pad_bottom),
            )
            contenedor_par.grid_columnconfigure(0, weight=0)
            contenedor_par.grid_columnconfigure(1, weight=1)

            lbl_campo = ctk.CTkLabel(
                contenedor_par,
                text=f"{etiqueta}:",
                font=("Segoe UI", 14),
                text_color=("#475569", "#CBD5E1"),
                anchor="w",
            )
            lbl_campo.grid(row=0, column=0, sticky="w", padx=(0, 8))

            lbl_valor = ctk.CTkLabel(
                contenedor_par,
                text="--",
                font=("Segoe UI", 14, "bold"),
                text_color=("#0F172A", "#F8FAFC"),
                anchor="w",
            )
            lbl_valor.grid(row=0, column=1, sticky="w")
            self._labels_valores[clave] = lbl_valor

    def _ejecutar_volver(self) -> None:
        """Regresa a la vista de Consulta."""
        if self._on_volver:
            self._on_volver()

    @staticmethod
    def _formatear_valor(datos: dict[str, Any], clave: str, defecto: str = "No especificado") -> str:
        """Formatea el valor del diccionario evitando None o cadenas vacías."""
        val = datos.get(clave)
        if val is None or str(val).strip() == "":
            return defecto
        return str(val).strip()

    def cargar_datos(self, datos: dict[str, Any]) -> None:
        """
        Actualiza el título y todas las etiquetas con la información del acta
        y muestra la vista de detalle.
        """
        if not datos:
            self.limpiar()
            return

        numero_acta = self._formatear_valor(datos, "numero_acta", "S/N")
        anio = self._formatear_valor(datos, "anio", "----")
        self.lbl_titulo_acta.configure(text=f"Acta Nº {numero_acta} - {anio}")

        for clave, lbl in self._labels_valores.items():
            defecto = "S/C" if clave == "presentante_cedula" else "No especificado"
            lbl.configure(text=self._formatear_valor(datos, clave, defecto))

        self.frame_vacio.grid_forget()
        self.frame_contenido.grid(row=0, column=0, sticky="nsew")

    def limpiar(self) -> None:
        """Restaura el estado inicial vacío de la vista Detalle."""
        self.lbl_titulo_acta.configure(text="Detalle del Acta")
        self.frame_contenido.grid_forget()
        self.frame_vacio.grid(row=0, column=0, sticky="nsew")
