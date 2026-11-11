"""
Módulo de Repositorio de Actas de Presentación.
Capa: Persistencia / Acceso a Datos (Repository en MVC).

Responsabilidad:
- Encapsular todas las sentencias SQL y consultas contra la tabla actas_presentacion.
- Desacoplar la base de datos convirtiendo filas de SQLite a tipos nativos de Python (dict).
- Asegurar que todas las consultas utilicen parámetros (?) para prevenir inyecciones SQL.
"""

import sqlite3
from typing import Any

from db.conexion import conexion


class ActaRepositorio:
    """
    Repositorio que maneja las operaciones CRUD sobre la tabla 'actas_presentacion'.
    """

    COLUMNAS_PERMITIDAS = (
        "numero_acta",
        "numero_libro",
        "numero_folio",
        "anio",
        "fecha_presentacion",
        "presentado_nombres",
        "presentado_sexo",
        "presentado_fecha_nac",
        "presentado_hora_nac",
        "presentado_tipo_parto",
        "presentante_cedula",
        "presentante_nombres",
        "estado",
        "ciudad",
        "recinto",
        "observaciones",
    )

    def buscar(self, filtros: dict[str, Any] | None = None) -> list[dict]:
        """
        Construye y ejecuta dinámicamente una consulta con filtros WHERE parametrizados.

        Claves soportadas en filtros (todas opcionales):
        - numero_acta (str): igualdad exacta.
        - presentante_cedula (str): igualdad exacta.
        - presentante_nombres (str): LIKE '%valor%' (case-insensitive).
        - presentado_nombres (str): LIKE '%valor%' (case-insensitive).
        - fecha_desde (str ISO): fecha_presentacion >= ?.
        - fecha_hasta (str ISO): fecha_presentacion <= ?.

        Orden: numero_acta ASC.
        Si filtros está vacío o todos los campos son None/vacíos, retorna todas las actas.
        """
        filtros = filtros or {}
        condiciones: list[str] = []
        parametros: list[Any] = []

        # 1. Filtro por número de acta exacto
        numero_acta = filtros.get("numero_acta")
        if numero_acta is not None and str(numero_acta).strip():
            condiciones.append("numero_acta = ?")
            parametros.append(str(numero_acta).strip())

        # 2. Filtro por cédula del presentante exacta
        presentante_cedula = filtros.get("presentante_cedula")
        if presentante_cedula is not None and str(presentante_cedula).strip():
            condiciones.append("presentante_cedula = ?")
            parametros.append(str(presentante_cedula).strip())

        # 3. Filtro por nombres del presentante (parcial e insensible a mayúsculas)
        presentante_nombres = filtros.get("presentante_nombres")
        if presentante_nombres is not None and str(presentante_nombres).strip():
            condiciones.append("LOWER(presentante_nombres) LIKE LOWER(?)")
            parametros.append(f"%{str(presentante_nombres).strip()}%")

        # 4. Filtro por nombres del presentado (parcial e insensible a mayúsculas)
        presentado_nombres = filtros.get("presentado_nombres")
        if presentado_nombres is not None and str(presentado_nombres).strip():
            condiciones.append("LOWER(presentado_nombres) LIKE LOWER(?)")
            parametros.append(f"%{str(presentado_nombres).strip()}%")

        # 5. Filtro por rango de fecha_presentacion desde
        fecha_desde = filtros.get("fecha_desde")
        if fecha_desde is not None and str(fecha_desde).strip():
            condiciones.append("fecha_presentacion >= ?")
            parametros.append(str(fecha_desde).strip())

        # 6. Filtro por rango de fecha_presentacion hasta
        fecha_hasta = filtros.get("fecha_hasta")
        if fecha_hasta is not None and str(fecha_hasta).strip():
            condiciones.append("fecha_presentacion <= ?")
            parametros.append(str(fecha_hasta).strip())

        # Construcción de la consulta final
        sql = "SELECT * FROM actas_presentacion"
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)
        sql += " ORDER BY numero_acta ASC;"

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, parametros)
            filas = cursor.fetchall()
            return [dict(fila) for fila in filas]

    def obtener_por_id(self, id_acta: int) -> dict | None:
        """Obtiene un acta por su identificador primario interno."""
        sql = "SELECT * FROM actas_presentacion WHERE id = ?;"
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id_acta,))
            fila = cursor.fetchone()
            return dict(fila) if fila else None

    def obtener_por_libro_folio_anio(
        self, libro: str | int, folio: str | int, anio: int
    ) -> dict | None:
        """Obtiene un acta por su clave única natural (número de libro, folio y año)."""
        sql = """
        SELECT * FROM actas_presentacion
        WHERE numero_libro = ? AND numero_folio = ? AND anio = ?;
        """
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (str(libro), str(folio), int(anio)))
            fila = cursor.fetchone()
            return dict(fila) if fila else None

    def insertar(self, datos: dict) -> int:
        """
        Inserta un nuevo registro en actas_presentacion.
        Retorna el id generado.

        Maneja IntegrityError por colisión con el índice único (numero_libro, numero_folio, anio)
        y lo relanza como ValueError en español.
        """
        columnas_a_insertar = [
            col for col in self.COLUMNAS_PERMITIDAS if col in datos
        ]

        if not columnas_a_insertar:
            raise ValueError("No se proporcionaron campos válidos para insertar el acta")

        placeholders = ", ".join(["?"] * len(columnas_a_insertar))
        nombres_columnas = ", ".join(columnas_a_insertar)
        valores = [datos[col] for col in columnas_a_insertar]

        sql = f"""
        INSERT INTO actas_presentacion ({nombres_columnas})
        VALUES ({placeholders});
        """

        try:
            with conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, valores)
                return cursor.lastrowid  # type: ignore
        except sqlite3.IntegrityError as error:
            error_msg = str(error)
            if "idx_libro_folio_anio" in error_msg or "UNIQUE" in error_msg.upper():
                raise ValueError("Ya existe un acta con el mismo libro, folio y año") from error
            raise

    def actualizar(self, id_acta: int, datos: dict) -> bool:
        """
        Actualiza los campos de un acta existente por su id.
        Establece automáticamente fecha_actualizacion = CURRENT_TIMESTAMP.
        Retorna True si afectó alguna fila, False en caso contrario.
        """
        columnas_a_actualizar = [
            col for col in self.COLUMNAS_PERMITIDAS if col in datos
        ]

        if not columnas_a_actualizar:
            return False

        asignaciones = [f"{col} = ?" for col in columnas_a_actualizar]
        asignaciones.append("fecha_actualizacion = CURRENT_TIMESTAMP")
        clausula_set = ", ".join(asignaciones)

        valores = [datos[col] for col in columnas_a_actualizar]
        valores.append(id_acta)

        sql = f"UPDATE actas_presentacion SET {clausula_set} WHERE id = ?;"

        try:
            with conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, valores)
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as error:
            error_msg = str(error)
            if "idx_libro_folio_anio" in error_msg or "UNIQUE" in error_msg.upper():
                raise ValueError("Ya existe un acta con el mismo libro, folio y año") from error
            raise

    def eliminar(self, id_acta: int) -> bool:
        """
        Elimina un acta por su id.
        Retorna True si eliminó el registro, False si no existía.
        """
        sql = "DELETE FROM actas_presentacion WHERE id = ?;"
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id_acta,))
            return cursor.rowcount > 0

    def contar(self) -> int:
        """Retorna el número total de actas registradas en la base de datos."""
        sql = "SELECT COUNT(*) AS total FROM actas_presentacion;"
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            resultado = cursor.fetchone()
            return int(resultado["total"]) if resultado else 0
