"""
Módulo de utilidades para validación y normalización de Cédulas de Identidad (C.I.).
Contexto: Hospital "Doctor Luis Razetti" (Barinas, Venezuela).

Reglas del negocio:
- La cédula se almacena como TEXT para preservar ceros a la izquierda.
- Se omiten prefijos de nacionalidad (V-, E-), puntos, guiones y espacios.
- Longitud válida: entre 6 y 9 dígitos numéricos.
"""

import re


def normalizar_cedula(valor: str | None) -> str:
    """
    Normaliza el valor de una Cédula de Identidad venezolana.

    Reglas:
    1. Si valor es None o cadena vacía/espacios -> devuelve "".
    2. Quita TODO lo que no sea dígito (puntos, espacios, guiones,
       prefijos 'V-'/'v-'/'E-' si aparecen, etc.).
    3. Devuelve solo los dígitos (preservando ceros a la izquierda).
    4. Si el resultado tiene dígitos pero no está entre 6 y 9 dígitos,
       lanza ValueError("La cédula debe tener entre 6 y 9 dígitos").

    :param valor: Cadena con el valor de la cédula ingresado.
    :return: Cadena con solo dígitos o cadena vacía.
    :raises ValueError: Si contiene dígitos pero su longitud no está en el rango [6, 9].
    """
    if valor is None:
        return ""

    texto = str(valor).strip()
    if not texto:
        return ""

    # Extrae únicamente los caracteres numéricos
    digitos = re.sub(r"\D", "", texto)

    # Si se encontraron dígitos pero la cantidad no está entre 6 y 9 dígitos
    if digitos and not (6 <= len(digitos) <= 9):
        raise ValueError("La cédula debe tener entre 6 y 9 dígitos")

    return digitos


def es_cedula_valida(valor: str | None) -> bool:
    """
    Verifica si el valor corresponde a una cédula válida o vacía permitida.
    Retorna True si normalizar_cedula no lanza excepción, False en caso contrario.

    :param valor: Cadena a validar.
    :return: True si no lanza excepción, False si lanza ValueError.
    """
    try:
        normalizar_cedula(valor)
        return True
    except ValueError:
        return False
