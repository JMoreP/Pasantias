"""
Módulo de Controlador de Actas de Presentación.
Capa: Control / Orquestación (Controller en MVC).

Responsabilidad:
- Recibir las acciones y eventos generados por la Vista principal y sus subvistas.
- Orquestar la navegación interna entre vistas ("Consulta", "Registro", "Detalle").
- Delegar las operaciones de búsqueda, registro y consulta a ActaServicio.
- Gestionar excepciones de negocio sin exponer SQL ni widgets directamente.
"""

from typing import Any


class ActaControlador:
    """
    Controlador para la gestión y navegación entre vistas de actas de presentación.
    """

    def __init__(self, vista: Any, servicio: Any) -> None:
        """
        Constructor que recibe la vista y el servicio (inyección de dependencias).

        :param vista: Instancia de la interfaz principal (VentanaConsulta).
        :param servicio: Instancia de la capa de negocio (ActaServicio).
        """
        self.vista = vista
        self.servicio = servicio

    def buscar(self, filtros: dict[str, Any]) -> None:
        """
        Ejecuta la búsqueda de actas aplicando los filtros indicados.
        Captura cualquier ValueError arrojado por el servicio y lo notifica a la vista.
        """
        try:
            resultados = self.servicio.buscar(filtros)
            self.vista.pintar_resultados(resultados)
        except ValueError as error:
            self.vista.mostrar_error(str(error))

    def limpiar_filtros(self) -> None:
        """Restablece el formulario de filtros y la tabla en la vista Consulta."""
        self.vista.limpiar_formulario()

    def volver_a_consulta(self) -> None:
        """Regresa a la vista de Consulta manteniendo intactos los resultados actuales."""
        self.vista.mostrar_vista("Consulta")

    def abrir_registro(self) -> None:
        """Navega a la vista de Registro."""
        self.vista.mostrar_vista("Registro")

    def guardar_acta(self, datos: dict[str, Any]) -> None:
        """
        Registra un acta mediante el servicio de negocio.
        - Si tiene éxito: muestra confirmación, limpia el formulario,
          regresa a 'Consulta' y actualiza la tabla principal.
        - Si ocurre ValueError: muestra el error y mantiene activa la vista 'Registro'.
        """
        try:
            self.servicio.registrar(datos)
            self.vista.mostrar_info("Acta registrada exitosamente.")
            self.vista.tab_registro.limpiar_formulario()
            self.vista.mostrar_vista("Consulta")
            resultados = self.servicio.listar_todas()
            self.vista.pintar_resultados(resultados)
        except ValueError as error:
            self.vista.tab_registro.mostrar_error(str(error))

    def abrir_detalle(self, id_acta: int) -> None:
        """
        Obtiene los datos completos del acta, los carga en TabDetalle
        y navega a la vista 'Detalle'.
        """
        acta = self.servicio.obtener(id_acta)
        if acta:
            self.vista.tab_detalle.cargar_datos(acta)
            self.vista.mostrar_vista("Detalle")
        else:
            self.vista.mostrar_error(f"No se encontró el acta #{id_acta}.")
