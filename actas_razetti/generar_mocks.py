"""
Script de generación masiva de datos de prueba (10,000 actas) y benchmark de rendimiento.
Uso:
    python3 generar_mocks.py            # Inserta 10,000 registros y mide tiempos de consulta
    python3 generar_mocks.py --limpiar  # Elimina los registros de prueba generados
"""

import argparse
from datetime import date, timedelta
from pathlib import Path
import random
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db.conexion import conexion
from servicios.acta_servicio import ActaServicio

NOMBRES_M = ("Carlos", "José", "Luis", "Miguel", "Juan", "Pedro", "Andrés", "Diego", "Mateo", "Gabriel")
NOMBRES_F = ("María", "Ana", "Sofía", "Valentina", "Camila", "Lucía", "Rosa", "Elena", "Paula", "Isabel")
APELLIDOS = ("Pérez", "Gómez", "Rodríguez", "González", "Silva", "Quintero", "Mendoza", "Rojas", "Torres", "Díaz")
TIPOS_PARTO = ("Único", "Único", "Único", "Único", "Gemelos", "Mellizos")


def generar_lote_mocks(cantidad: int = 10_000) -> list[tuple]:
    """Construye en memoria un lote de tuplas válidas respetando (numero_libro, numero_folio, anio)."""
    rng = random.Random(42)
    fecha_base = date(2015, 1, 1)
    filas: list[tuple] = []

    for i in range(1, cantidad + 1):
        es_nina = (i % 2 == 0)
        sexo = "niña" if es_nina else "niño"
        nombre_nino = rng.choice(NOMBRES_F if es_nina else NOMBRES_M)
        apellido_1 = rng.choice(APELLIDOS)
        apellido_2 = rng.choice(APELLIDOS)
        presentado = f"{nombre_nino} {apellido_1} {apellido_2}"

        nombre_pres = rng.choice(NOMBRES_M if i % 3 else NOMBRES_F)
        presentante = f"{nombre_pres} {apellido_1} {rng.choice(APELLIDOS)}"
        cedula = f"{10_000_000 + (i * 7919) % 20_000_000:08d}"

        fecha_dt = fecha_base + timedelta(days=(i % 3650))
        fecha_iso = fecha_dt.isoformat()
        anio = fecha_dt.year
        libro = str(100 + (i // 250))
        folio = str(1 + (i % 250))
        numero_acta = f"{10_000 + i}"

        filas.append(
            (
                numero_acta,
                libro,
                folio,
                anio,
                fecha_iso,
                presentado,
                sexo,
                fecha_iso,
                f"{6 + (i % 12):02d}:{(i * 7) % 60:02d}",
                rng.choice(TIPOS_PARTO),
                cedula,
                presentante,
                "Barinas",
                "Barinas",
                'Hospital "Doctor Luis Razetti"',
                "[MOCK_BENCHMARK]",
            )
        )
    return filas


def poblar_y_medir(cantidad: int = 10_000) -> None:
    """Inserta los 10,000 registros en una única transacción WAL y mide consultas paginadas."""
    print(f"[+] Generando {cantidad:,} registros sintéticos en memoria...")
    t0 = time.perf_counter()
    filas = generar_lote_mocks(cantidad)

    sql = """
    INSERT OR IGNORE INTO actas_presentacion (
        numero_acta, numero_libro, numero_folio, anio, fecha_presentacion,
        presentado_nombres, presentado_sexo, presentado_fecha_nac,
        presentado_hora_nac, presentado_tipo_parto, presentante_cedula,
        presentante_nombres, estado, ciudad, recinto, observaciones
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    with conexion() as conn:
        cursor = conn.cursor()
        cursor.executemany(sql, filas)
        insertados = cursor.rowcount

    t_insert = (time.perf_counter() - t0) * 1000
    print(f"[✔] Inserción completada en {t_insert:.2f} ms (filas afectadas: {insertados:,}).")

    # Benchmark de consultas paginadas (50 por página)
    servicio = ActaServicio()
    consultas = [
        ("Página 1 (sin filtros)", {}, 1),
        ("Página 100 (OFFSET 4,950)", {}, 100),
        ("Por C.I. exacta (idx_presentante_cedula)", {"presentante_cedula": "10007919"}, 1),
        ("Por No. de Acta (idx_acta)", {"numero_acta": "15000"}, 1),
        ("Por rango de fechas (idx_fecha_presentacion)", {"fecha_desde": "2020-01-01", "fecha_hasta": "2020-12-31"}, 1),
        ("Por nombre presentado (LIKE)", {"presentado_nombres": "Sofía"}, 1),
    ]

    print("\n[+] Benchmark de consultas paginadas (LIMIT 50):")
    for etiqueta, filtros, pagina in consultas:
        t_ini = time.perf_counter()
        res = servicio.buscar_paginado(filtros, pagina=pagina, por_pagina=50)
        elapsed_ms = (time.perf_counter() - t_ini) * 1000
        print(
            f"  - {etiqueta:46s}: {len(res['resultados']):2d} filas "
            f"(total={res['total']:,}, págs={res['total_paginas']:,}) en {elapsed_ms:.2f} ms"
        )


def limpiar_mocks() -> None:
    """Elimina únicamente los registros de prueba marcados con '[MOCK_BENCHMARK]'."""
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM actas_presentacion WHERE observaciones = '[MOCK_BENCHMARK]';")
        eliminados = cursor.rowcount
    print(f"[✔] Se eliminaron {eliminados:,} registros de prueba.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de mocks y benchmark de escalabilidad.")
    parser.add_argument("--limpiar", action="store_true", help="Elimina los registros de prueba.")
    args = parser.parse_args()

    if args.limpiar:
        limpiar_mocks()
    else:
        poblar_y_medir(10_000)
