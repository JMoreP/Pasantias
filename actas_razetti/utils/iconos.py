"""
Módulo de generación dinámica de íconos vectoriales en tiempo de ejecución.
Utiliza Pillow (PIL) para dibujar gráficos limpios y nítidos con antialiasing
adaptados automáticamente al Modo Claro y Modo Oscuro de CustomTkinter.
"""

from typing import Callable
import customtkinter as ctk
from PIL import Image, ImageDraw

ColorParam = str | tuple[str, str] | None


def _crear_canvas_base(dimension_render: int = 80) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Crea una imagen RGBA transparente con resolución aumentada para supersampling."""
    img = Image.new("RGBA", (dimension_render, dimension_render), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw


def _resolver_par_colores(color: ColorParam) -> tuple[str, str]:
    """
    Convierte un parámetro de color en la tupla (color_light, color_dark).
    - Si es tuple: retorna sus dos componentes.
    - Si es str: usa el mismo color en ambos modos.
    - Si es None: detecta el modo actual o retorna contraste adaptativo.
    """
    if isinstance(color, tuple) and len(color) == 2:
        return str(color[0]), str(color[1])
    if isinstance(color, str) and color.strip():
        return color, color

    modo_actual = str(ctk.get_appearance_mode()).lower()
    if modo_actual == "dark":
        return "#E2E8F0", "#E2E8F0"
    return "#0F172A", "#E2E8F0"


def _generar_ctk_image_dual(
    dibujante: Callable[[ImageDraw.ImageDraw, str], None],
    color: ColorParam,
    size: tuple[int, int],
) -> ctk.CTkImage:
    """Renderiza variantes light y dark con supersampling LANCZOS para CTkImage."""
    color_light, color_dark = _resolver_par_colores(color)
    render_size = 80

    img_light, draw_light = _crear_canvas_base(render_size)
    dibujante(draw_light, color_light)
    light_final = img_light.resize(size, Image.Resampling.LANCZOS)

    if color_dark == color_light:
        dark_final = light_final
    else:
        img_dark, draw_dark = _crear_canvas_base(render_size)
        dibujante(draw_dark, color_dark)
        dark_final = img_dark.resize(size, Image.Resampling.LANCZOS)

    return ctk.CTkImage(light_image=light_final, dark_image=dark_final, size=size)


def crear_icono_lupa(
    color: ColorParam = "#FFFFFF",
    size: tuple[int, int] = (20, 20),
) -> ctk.CTkImage:
    """Genera un ícono de lupa (búsqueda) adaptable a modo claro y oscuro."""
    def _dibujar(draw: ImageDraw.ImageDraw, col: str) -> None:
        draw.ellipse([14, 14, 50, 50], outline=col, width=7)
        draw.line([44, 44, 68, 68], fill=col, width=8)

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_limpiar(
    color: ColorParam = ("#0F172A", "#E2E8F0"),
    size: tuple[int, int] = (20, 20),
) -> ctk.CTkImage:
    """Genera un ícono de escoba para limpieza adaptable a modo claro y oscuro."""
    def _dibujar(draw: ImageDraw.ImageDraw, col: str) -> None:
        draw.line([58, 12, 38, 42], fill=col, width=7)
        draw.polygon([(26, 42), (50, 42), (62, 68), (14, 68)], outline=col, fill=None, width=5)
        draw.line([(31, 46), (28, 64)], fill=col, width=4)
        draw.line([(45, 46), (48, 64)], fill=col, width=4)

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_documento_plus(
    color: ColorParam = "#FFFFFF",
    size: tuple[int, int] = (20, 20),
) -> ctk.CTkImage:
    """Genera un ícono de documento con símbolo '+' para registro de nueva acta."""
    def _dibujar(draw: ImageDraw.ImageDraw, col: str) -> None:
        draw.rectangle([14, 12, 52, 68], outline=col, width=6)
        draw.line([22, 25, 44, 25], fill=col, width=5)
        draw.line([22, 37, 44, 37], fill=col, width=5)
        draw.ellipse([42, 42, 70, 70], fill=col, outline=None)
        draw.line([56, 48, 56, 64], fill="#059669", width=4)
        draw.line([48, 56, 64, 56], fill="#059669", width=4)

    return _generar_ctk_image_dual(_dibujar, color, size)
