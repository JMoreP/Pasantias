"""
Módulo de Servicio de Actas de Presentación.
Capa: Lógica de Negocio (Service en MVC).

Responsabilidad:
- Aplicar reglas del negocio, validaciones de integridad y normalización de datos.
- Desacoplar la vista y el controlador del acceso directo a la base de datos.
- Interactuar con ActaRepositorio mediante inyección de dependencias.
"""

from datetime import datetime
from typing import Any

from repositorios.acta_repositorio import ActaRepositorio
from utils.cedula import normalizar_cedula


class ActaServicio:
    """
    Servicio que implementa la lógica de negocio para la gestión de actas de presentación.
    """

    SEXOS_PERMITIDOS = {"niño", "niña"}
    TIPOS_PARTO_PERMITIDOS = {"Único", "Gemelos", "Mellizos", "Múltiple"}

    def __init__(self, repositorio: ActaRepositorio | None = None) -> None:
        """
        Constructor con inyección de dependencia del repositorio.
        """
        self.repositorio = repositorio or ActaRepositorio()

    def buscar(self, filtros: dict[str, Any] | None = None) -> list[dict]:
        """
        Aplica validaciones de negocio y normalizaciones a los filtros antes de buscar.

        Reglas:
        - Si viene 'presentante_cedula', se normaliza mediante utils.cedula.normalizar_cedula.
        - Valida que fecha_desde <= fecha_hasta si ambas están presentes.
        - Descarta filtros con valor vacío o None para realizar búsqueda amplia.
        """
        filtros_originales = filtros or {}
        filtros_limpios: dict[str, Any] = {}

        for clave, valor in filtros_originales.items():
            if valor is None:
                continue
            if isinstance(valor, str):
                valor_str = valor.strip()
                if valor_str:
                    filtros_limpios[clave] = valor_str
            else:
                filtros_limpios[clave] = valor

        # Normalizar cédula del presentante si viene en los filtros
        if "presentante_cedula" in filtros_limpios:
            cedula_cruda = str(filtros_limpios["presentante_cedula"])
            filtros_limpios["presentante_cedula"] = normalizar_cedula(cedula_cruda)

        # Validar coherencia de rango de fechas
        fecha_desde = filtros_limpios.get("fecha_desde")
        fecha_hasta = filtros_limpios.get("fecha_hasta")

        if fecha_desde and fecha_hasta:
            try:
                f_desde = datetime.strptime(str(fecha_desde), "%Y-%m-%d")
            except ValueError as error:
                raise ValueError("La fecha 'Desde' debe tener formato YYYY-MM-DD") from error

            try:
                f_hasta = datetime.strptime(str(fecha_hasta), "%Y-%m-%d")
            except ValueError as error:
                raise ValueError("La fecha 'Hasta' debe tener formato YYYY-MM-DD") from error

            if f_desde > f_hasta:
                raise ValueError("La fecha 'Desde' no puede ser posterior a 'Hasta'")

        return self.repositorio.buscar(filtros_limpios)

    def _validar_y_limpiar_datos(self, datos: dict[str, Any]) -> dict[str, Any]:
        """
        Valida exhaustivamente los datos del acta y aplica trim a todas las cadenas.
        Lanza ValueError con mensajes claros en caso de fallo.
        """
        if not isinstance(datos, dict):
            raise ValueError("Los datos del acta deben suministrarse en un diccionario")

        # 1. Limpieza y trim de todas las cadenas de texto
        datos_limpios: dict[str, Any] = {}
        for clave, valor in datos.items():
            if isinstance(valor, str):
                datos_limpios[clave] = valor.strip()
            else:
                datos_limpios[clave] = valor

        # 2. Validación de campos obligatorios
        for campo, nombre_legible in [
            ("numero_acta", "Número de acta"),
            ("numero_libro", "Número de libro"),
            ("numero_folio", "Número de folio"),
            ("anio", "Año"),
            ("fecha_presentacion", "Fecha de presentación"),
            ("presentado_nombres", "Nombres del presentado"),
            ("presentante_nombres", "Nombres del presentante"),
        ]:
            val = datos_limpios.get(campo)
            if val is None or (isinstance(val, str) and not val):
                raise ValueError(f"El campo '{nombre_legible}' es obligatorio y no puede estar vacío")

        # 3. Validación de año
        try:
            anio = int(datos_limpios["anio"])
            datos_limpios["anio"] = anio
        except (ValueError, TypeError) as error:
            raise ValueError("El año debe ser un número entero válido") from error

        anio_maximo = datetime.now().year + 1
        if not (1900 <= anio <= anio_maximo):
            raise ValueError(f"El año debe estar comprendido entre 1900 y {anio_maximo}")

        # 4. Validación de fecha_presentacion (formato ISO YYYY-MM-DD)
        fecha_pres_str = str(datos_limpios["fecha_presentacion"])
        try:
            datetime.strptime(fecha_pres_str, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError("La fecha de presentación debe tener formato válido YYYY-MM-DD") from error

        # 5. Validación de sexo del presentado (opcional, pero si viene debe ser 'niño' o 'niña')
        sexo = datos_limpios.get("presentado_sexo")
        if sexo:
            if sexo not in self.SEXOS_PERMITIDOS:
                raise ValueError("El sexo del presentado debe ser 'niño' o 'niña'")
        else:
            datos_limpios["presentado_sexo"] = None

        # 6. Validación de tipo de parto (opcional, pero restringido al conjunto)
        tipo_parto = datos_limpios.get("presentado_tipo_parto")
        if tipo_parto:
            if tipo_parto not in self.TIPOS_PARTO_PERMITIDOS:
                raise ValueError(
                    f"El tipo de parto debe ser uno de: {', '.join(sorted(self.TIPOS_PARTO_PERMITIDOS))}"
                )
        else:
            datos_limpios["presentado_tipo_parto"] = None

        # 7. Normalización y validación de la cédula del presentante
        cedula_raw = datos_limpios.get("presentante_cedula")
        if cedula_raw is not None and str(cedula_raw).strip():
            datos_limpios["presentante_cedula"] = normalizar_cedula(str(cedula_raw))
        else:
            datos_limpios["presentante_cedula"] = None

        # 8. Opcionales con formato (fecha y hora de nacimiento)
        fecha_nac = datos_limpios.get("presentado_fecha_nac")
        if fecha_nac:
            try:
                datetime.strptime(str(fecha_nac), "%Y-%m-%d")
            except ValueError as error:
                raise ValueError("La fecha de nacimiento del presentado debe tener formato YYYY-MM-DD") from error
        else:
            datos_limpios["presentado_fecha_nac"] = None

        hora_nac = datos_limpios.get("presentado_hora_nac")
        if hora_nac:
            try:
                datetime.strptime(str(hora_nac), "%H:%M")
            except ValueError as error:
                raise ValueError("La hora de nacimiento del presentado debe tener formato HH:MM") from error
        else:
            datos_limpios["presentado_hora_nac"] = None

        return datos_limpios

    def registrar(self, datos: dict[str, Any]) -> int:
        """
        Valida, normaliza y registra un acta en el sistema.
        Retorna el id del nuevo registro insertado.
        """
        datos_validados = self._validar_y_limpiar_datos(datos)
        return self.repositorio.insertar(datos_validados)

    def actualizar(self, id_acta: int, datos: dict[str, Any]) -> bool:
        """
        Valida, normaliza y actualiza un acta existente.
        """
        if not id_acta or int(id_acta) <= 0:
            raise ValueError("El ID del acta a actualizar debe ser un número entero positivo")

        datos_validados = self._validar_y_limpiar_datos(datos)
        return self.repositorio.actualizar(int(id_acta), datos_validados)

    def eliminar(self, id_acta: int) -> bool:
        """
        Elimina un acta por su identificador único.
        """
        if not id_acta or int(id_acta) <= 0:
            raise ValueError("El ID del acta a eliminar debe ser un número entero positivo")
        return self.repositorio.eliminar(int(id_acta))

    def obtener(self, id_acta: int) -> dict | None:
        """
        Obtiene un acta por su ID.
        """
        if not id_acta or int(id_acta) <= 0:
            return None
        return self.repositorio.obtener_por_id(int(id_acta))

    def listar_todas(self) -> list[dict]:
        """
        Retorna la lista de todas las actas registradas en el sistema.
        """
        return self.repositorio.buscar({})
