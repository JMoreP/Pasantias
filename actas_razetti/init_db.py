"""
Script de inicialización de la base de datos para Actas de Presentación.
Hospital "Doctor Luis Razetti" (Barinas, Venezuela).

Crea la tabla actas_presentacion, sus índices correspondientes y
siembra datos de prueba de forma idempotente.
"""

from pathlib import Path
import sys

# Permitir ejecución directa del script independientemente del directorio actual
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db.conexion import conexion, obtener_ruta_db
from utils.cedula import normalizar_cedula

DDL_TABLA_ACTAS = """
CREATE TABLE IF NOT EXISTS actas_presentacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_acta TEXT NOT NULL,
    numero_libro TEXT NOT NULL,
    numero_folio TEXT NOT NULL,
    anio INTEGER NOT NULL,
    fecha_presentacion TEXT NOT NULL,
    presentado_nombres TEXT NOT NULL,
    presentado_sexo TEXT CHECK(presentado_sexo IN ('niño', 'niña')),
    presentado_fecha_nac TEXT,
    presentado_hora_nac TEXT,
    presentado_tipo_parto TEXT,
    presentante_cedula TEXT,
    presentante_nombres TEXT NOT NULL,
    estado TEXT DEFAULT 'Barinas',
    ciudad TEXT DEFAULT 'Barinas',
    recinto TEXT DEFAULT 'Hospital "Doctor Luis Razetti"',
    observaciones TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME
);
"""

DDL_INDICES = [
    "CREATE INDEX IF NOT EXISTS idx_acta ON actas_presentacion(numero_acta);",
    "CREATE INDEX IF NOT EXISTS idx_presentado_nombres ON actas_presentacion(presentado_nombres);",
    "CREATE INDEX IF NOT EXISTS idx_presentante_nombres ON actas_presentacion(presentante_nombres);",
    "CREATE INDEX IF NOT EXISTS idx_presentante_cedula ON actas_presentacion(presentante_cedula);",
    "CREATE INDEX IF NOT EXISTS idx_fecha_presentacion ON actas_presentacion(fecha_presentacion);",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_libro_folio_anio ON actas_presentacion(numero_libro, numero_folio, anio);",
]

# Datos iniciales para sembrar la base de datos
DATOS_SEMILLA = [
    {
        "numero_acta": "990",
        "numero_libro": "4",
        "numero_folio": "240",
        "anio": 2016,
        "fecha_presentacion": "2016-02-22",
        "presentado_nombres": "María Pérez",
        "presentado_sexo": "niña",
        "presentado_fecha_nac": "2016-02-22",
        "presentado_hora_nac": "06:15",
        "presentado_tipo_parto": "Único",
        "presentante_cedula": normalizar_cedula("12345678"),
        "presentante_nombres": "José Pérez",
        "observaciones": "Acta inicial de prueba transcrita del libro físico.",
    },
    {
        "numero_acta": "991",
        "numero_libro": "4",
        "numero_folio": "241",
        "anio": 2016,
        "fecha_presentacion": "2016-02-23",
        "presentado_nombres": "Carlos Gómez",
        "presentado_sexo": "niño",
        "presentado_fecha_nac": "2016-02-23",
        "presentado_hora_nac": "08:30",
        "presentado_tipo_parto": "Único",
        "presentante_cedula": normalizar_cedula("18765432"),
        "presentante_nombres": "Rosa Gómez",
        "observaciones": "Presentación oportuna. Libro físico en buen estado.",
    },
]


def vaciar_bd() -> int:
    """
    Elimina todas las actas de la base de datos, resetea el contador
    autoincremental a 1 y compacta el archivo SQLite (VACUUM).
    Retorna la cantidad de registros eliminados.
    """
    ruta_db = obtener_ruta_db()
    print(f"[+] Conectando a la base de datos SQLite en:\n    {ruta_db}")
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM actas_presentacion;")
        total = cursor.fetchone()[0]
        cursor.execute("DELETE FROM actas_presentacion;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'actas_presentacion';")
        conn.commit()
        cursor.execute("VACUUM;")
        print(f"[✔] Base de datos vaciada con éxito. Se eliminaron {total} registros y se reseteó el contador a 1.")
        return total


def inicializar_bd(sembrar: bool = False) -> None:
    """
    Crea las tablas y los índices si no existen.
    Si sembrar=True, siembra los registros de ejemplo de forma idempotente.
    """
    ruta_db = obtener_ruta_db()
    print(f"[+] Conectando a la base de datos SQLite en:\n    {ruta_db}")

    with conexion() as conn:
        cursor = conn.cursor()

        # 1. Crear tabla principal
        print("[+] Creando tabla 'actas_presentacion' si no existe...")
        cursor.execute(DDL_TABLA_ACTAS)

        # 2. Crear índices
        print("[+] Creando índices e índice único compuesto (numero_libro, numero_folio, anio)...")
        for sql_idx in DDL_INDICES:
            cursor.execute(sql_idx)

        # 3. Sembrar datos de prueba si se solicita explícitamente
        filas_insertadas = 0
        if sembrar:
            print("[+] Sembrando registros iniciales de prueba...")
            for acta in DATOS_SEMILLA:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO actas_presentacion (
                        numero_acta,
                        numero_libro,
                        numero_folio,
                        anio,
                        fecha_presentacion,
                        presentado_nombres,
                        presentado_sexo,
                        presentado_fecha_nac,
                        presentado_hora_nac,
                        presentado_tipo_parto,
                        presentante_cedula,
                        presentante_nombres,
                        observaciones
                    ) VALUES (
                        :numero_acta,
                        :numero_libro,
                        :numero_folio,
                        :anio,
                        :fecha_presentacion,
                        :presentado_nombres,
                        :presentado_sexo,
                        :presentado_fecha_nac,
                        :presentado_hora_nac,
                        :presentado_tipo_parto,
                        :presentante_cedula,
                        :presentante_nombres,
                        :observaciones
                    );
                    """,
                    acta,
                )
                if cursor.rowcount > 0:
                    filas_insertadas += 1
            print(f"[✔] Nuevas filas insertadas: {filas_insertadas}.")

        print("[✔] Estructura e índices de base de datos listos.")


if __name__ == "__main__":
    if "--limpiar" in sys.argv or "--vaciar" in sys.argv:
        vaciar_bd()
    elif "--semilla" in sys.argv or "--sembrar" in sys.argv:
        inicializar_bd(sembrar=True)
    else:
        inicializar_bd(sembrar=False)
