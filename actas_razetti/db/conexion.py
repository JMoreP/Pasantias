"""
Módulo de conexión y gestión de base de datos SQLite.
Provee un context manager para manejar transacciones y cierres de conexión de forma segura.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

# Ruta base donde se aloja el archivo actas.db (carpeta db/)
DB_DIR = Path(__file__).resolve().parent
DB_FILE = DB_DIR / "actas.db"


def obtener_ruta_db() -> Path:
    """
    Retorna la ruta absoluta del archivo SQLite.
    Garantiza que el directorio contenedor exista.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_FILE


@contextmanager
def conexion() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager para interactuar con la base de datos SQLite.

    Comportamiento:
    - Asegura la creación del directorio db/ si no existe.
    - Activa PRAGMA foreign_keys = ON en cada sesión.
    - Configura row_factory = sqlite3.Row para acceso asociativo a columnas.
    - Realiza commit automático si el bloque finaliza sin errores.
    - Realiza rollback automático si ocurre una excepción no controlada.
    - Cierra siempre la conexión al salir del contexto.

    Uso:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
    ruta = obtener_ruta_db()
    conn = sqlite3.connect(str(ruta))
    conn.row_factory = sqlite3.Row

    try:
        # Activar soporte de claves foráneas
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
