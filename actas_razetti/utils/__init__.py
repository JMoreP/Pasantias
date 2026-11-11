"""
Paquete de utilidades generales para el sistema de actas.
"""

from .cedula import es_cedula_valida, normalizar_cedula
from .iconos import crear_icono_documento_plus, crear_icono_limpiar, crear_icono_lupa

__all__ = [
    "normalizar_cedula",
    "es_cedula_valida",
    "crear_icono_lupa",
    "crear_icono_limpiar",
    "crear_icono_documento_plus",
]
