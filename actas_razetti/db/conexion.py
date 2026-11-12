"""
Módulo de conexión y gestión de base de datos SQLite.
Provee un context manager seguro con modo WAL, timeouts de concurrencia
y control estricto de transacciones (commit/rollback/close).
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
    - Activa PRAGMA journal_mode = WAL y synchronous = NORMAL para alta
      concurrencia y velocidad de lectura/escritura.
    - Configura busy_timeout = 5000 ms para evitar bloqueos transitorios.
    - Activa PRAGMA foreign_keys = ON y row_factory = sqlite3.Row.
    - Ejecuta commit() únicamente si hay una transacción pendiente.
    - Ejecuta rollback() ante cualquier excepción y cierra siempre la conexión.
    """
    ruta = obtener_ruta_db()
    conn = sqlite3.connect(str(ruta), timeout=5.0)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        if conn.in_transaction:
            conn.commit()
    except Exception:
        if conn.in_transaction:
            conn.rollback()
        raise
    finally:
        conn.close()
