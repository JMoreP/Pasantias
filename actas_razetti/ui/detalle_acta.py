"""
Módulo de Ventana Modal para Visualización de Detalle de Acta.
Capa: Presentación / Vista (View en MVC).

Diseño y UX:
- Ventana modal CTkToplevel (800x600) centrada con grab_set().
- Encabezado grande: "Acta Nº {numero_acta} - {anio}".
- Secciones visuales en tarjeta blanca con etiquetas ("Campo:") a la izquierda
  y valores en negrita a la derecha.
- Botón inferior "Cerrar" (width=120, height=45).
"""

from typing import Any
import customtkinter as ctk


class DetalleActa(ctk.CTkToplevel):
    """
    Ventana modal de solo lectura que muestra toda la información de un acta.
    """

    def __init__(self, datos_acta: dict[str, Any], parent: Any = None) -> None:
        super().__init__(master=parent)

        self.datos_acta = datos_acta or {}

        # 1. Configuración de la ventana modal
        self.title("Detalle del Acta")
        self.configure(fg_color="#F0F2F5")
        self._centrar_ventana(ancho=800, alto=600)
        self.resizable(False, False)

        if parent is not None:
            self.transient(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 2. Construcción del layout
        self._crear_cabecera()
        self._crear_tarjeta_detalle()
        self._crear_boton_cerrar()

        # 3. Modalidad y accesibilidad
        self.bind("<Escape>", lambda _e: self.destroy())
        self.update_idletasks()
        self.grab_set()
        self.focus_set()

    def _centrar_ventana(self, ancho: int, alto: int) -> None:
        """Centra la ventana modal en la pantalla."""
        pantalla_w = self.winfo_screenwidth()
        pantalla_h = self.winfo_screenheight()
        pos_x = max(0, (pantalla_w - ancho) // 2)
        pos_y = max(0, (pantalla_h - alto) // 2)
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    def _valor(self, clave: str, defecto: str = "No especificado") -> str:
        """Obtiene el valor formateado del diccionario evitando None o cadenas vacías."""
        val = self.datos_acta.get(clave)
        if val is None or str(val).strip() == "":
            return defecto
        return str(val).strip()

    def _crear_cabecera(self) -> None:
        """Título grande con formato 'Acta Nº {numero_acta} - {anio}'."""
        frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        frame_cabecera.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))

        numero_acta = self._valor("numero_acta", "S/N")
        anio = self._valor("anio", "----")

        lbl_titulo = ctk.CTkLabel(
            frame_cabecera,
            text=f"Acta Nº {numero_acta} - {anio}",
            font=("Segoe UI", 24, "bold"),
            text_color="#0F172A",
            anchor="w",
        )
        lbl_titulo.pack(anchor="w")

    def _crear_seccion(
        self,
        parent: Any,
        titulo: str,
        fila: int,
        campos: list[tuple[str, str]],
    ) -> None:
        """
        Crea una sección visual con borde sutil y renderiza cada campo
        como Label('Campo:') a la izquierda y Label('Valor') en negrita a la derecha
        en pares de 2 columnas para mantener lectura cómoda y compacta.
        """
        seccion = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color="#F8FAFC",
            border_width=1,
            border_color="#E2E8F0",
        )
        seccion.grid(row=fila, column=0, sticky="ew", padx=16, pady=6)
        seccion.grid_columnconfigure(0, weight=1)
        seccion.grid_columnconfigure(1, weight=1)

        lbl_titulo = ctk.CTkLabel(
            seccion,
            text=titulo,
            font=("Segoe UI", 15, "bold"),
            text_color="#1E293B",
            anchor="w",
        )
        lbl_titulo.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 4))

        for idx, (etiqueta, valor) in enumerate(campos):
            fila_campo = (idx // 2) + 1
            col_campo = idx % 2

            contenedor_par = ctk.CTkFrame(seccion, fg_color="transparent")
            pad_x = (14, 10) if col_campo == 0 else (10, 14)
            pad_bottom = 8 if idx >= len(campos) - 2 else 3
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
                text_color="#475569",
                anchor="w",
            )
            lbl_campo.grid(row=0, column=0, sticky="w", padx=(0, 8))

            lbl_valor = ctk.CTkLabel(
                contenedor_par,
                text=valor,
                font=("Segoe UI", 14, "bold"),
                text_color="#0F172A",
                anchor="w",
            )
            lbl_valor.grid(row=0, column=1, sticky="w")

    def _crear_tarjeta_detalle(self) -> None:
        """Construye la tarjeta blanca con todas las secciones de datos del acta."""
        tarjeta = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E2E8F0",
        )
        tarjeta.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        tarjeta.grid_columnconfigure(0, weight=1)

        # 1. Datos del Libro
        self._crear_seccion(
            tarjeta,
            "Datos del Libro",
            fila=0,
            campos=[
                ("Libro", self._valor("numero_libro")),
                ("Folio", self._valor("numero_folio")),
                ("Fecha de Presentación", self._valor("fecha_presentacion")),
            ],
        )

        # 2. Datos del Presentante
        self._crear_seccion(
            tarjeta,
            "Datos del Presentante",
            fila=1,
            campos=[
                ("C.I.", self._valor("presentante_cedula", "S/C")),
                ("Nombres", self._valor("presentante_nombres")),
            ],
        )

        # 3. Datos del Presentado
        self._crear_seccion(
            tarjeta,
            "Datos del Presentado",
            fila=2,
            campos=[
                ("Nombres", self._valor("presentado_nombres")),
                ("Sexo", self._valor("presentado_sexo")),
                ("Fecha Nac.", self._valor("presentado_fecha_nac")),
                ("Hora Nac.", self._valor("presentado_hora_nac")),
                ("Tipo Parto", self._valor("presentado_tipo_parto")),
            ],
        )

        # 4. Lugar de Nacimiento
        self._crear_seccion(
            tarjeta,
            "Lugar de Nacimiento",
            fila=3,
            campos=[
                ("Estado", self._valor("estado")),
                ("Ciudad", self._valor("ciudad")),
                ("Recinto", self._valor("recinto")),
            ],
        )

    def _crear_boton_cerrar(self) -> None:
        """Botón inferior para cerrar la ventana de detalle."""
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))

        btn_cerrar = ctk.CTkButton(
            frame_acciones,
            text="Cerrar",
            width=120,
            height=45,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#0F172A",
            command=self.destroy,
        )
        btn_cerrar.pack(side="right")
