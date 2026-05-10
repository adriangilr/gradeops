# src/utils/naming.py

import re

MAX_LEN_DEFAULT = 40


def limpiar_texto(texto: str) -> str:
    if not texto:
        return "sin_nombre"

    texto = texto.strip()

    reemplazos = {
        "/": "-",
        "\\": "-",
        ":": "-",
        "*": "-",
        "?": "",
        '"': "",
        "<": "(",
        ">": ")",
        "|": "-",
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    texto = re.sub(r"\s+", "_", texto)
    return texto.strip("_") or "sin_nombre"


def recortar_nombre(nombre: str, max_len: int) -> str:
    if len(nombre) <= max_len:
        return nombre
    return nombre[:max_len].rstrip("_")


def construir_nombre_portfolio(
    name: str,
    last_name: str,
    user_id: str,
    modo: str = "portfolio",
    max_len: int = MAX_LEN_DEFAULT,
) -> str:
    """
    Modos disponibles:
    - portfolio (recomendado)
    - completo (debug)
    - corto (solo nombre)
    """

    name = limpiar_texto(name)
    last_name = limpiar_texto(last_name)

    if modo == "corto":
        base = f"{last_name}_{name}"

    elif modo == "completo":
        base = f"{last_name}_{name}_{user_id}"

    else:  # portfolio
        suffix = user_id[-4:] if user_id else "0000"
        base = f"{last_name}_{name}_{suffix}"

    return recortar_nombre(base, max_len)