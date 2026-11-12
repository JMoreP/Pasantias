"""
Módulo de generación dinámica de íconos vectoriales de alta precisión.
Utiliza PyCairo (vectorial con antialiasing subpíxel, LINE_CAP_ROUND y LINE_JOIN_ROUND)
y Pillow para generar CTkImage duales adaptados a Modo Claro y Modo Oscuro.
"""

import math
from typing import Callable
import cairo
import customtkinter as ctk
from PIL import Image

ColorParam = str | tuple[str, str] | None


def _hex_a_rgba(color_hex: str) -> tuple[float, float, float, float]:
    """Convierte un color hexadecimal '#RRGGBB' a tupla RGBA normalizada (0.0 - 1.0)."""
    hex_limpio = color_hex.strip().lstrip("#")
    if len(hex_limpio) == 3:
        hex_limpio = "".join(c * 2 for c in hex_limpio)
    r = int(hex_limpio[0:2], 16) / 255.0
    g = int(hex_limpio[2:4], 16) / 255.0
    b = int(hex_limpio[4:6], 16) / 255.0
    return (r, g, b, 1.0)


def _resolver_par_colores(color: ColorParam) -> tuple[str, str]:
    """
    Convierte un parámetro de color en la tupla (color_light, color_dark).
    - Si es tuple: retorna sus dos componentes.
    - Si es str: usa el mismo color en ambos modos.
    - Si es None: retorna contraste adaptativo estándar.
    """
    if isinstance(color, tuple) and len(color) == 2:
        return str(color[0]), str(color[1])
    if isinstance(color, str) and color.strip():
        return color, color

    modo_actual = str(ctk.get_appearance_mode()).lower()
    if modo_actual == "dark":
        return "#F1F5F9", "#F1F5F9"
    return "#1E293B", "#F1F5F9"


def _renderizar_cairo(
    dibujante: Callable[[cairo.Context], None],
    color_hex: str,
    size: tuple[int, int],
) -> Image.Image:
    """
    Renderiza un ícono vectorial sobre un viewBox estándar 24x24 usando PyCairo
    con supersampling 4x y resampleo LANCZOS hacia el tamaño final.
    """
    scale_factor = 4
    render_w = max(96, size[0] * scale_factor)
    render_h = max(96, size[1] * scale_factor)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, render_w, render_h)
    ctx = cairo.Context(surface)

    ctx.scale(render_w / 24.0, render_h / 24.0)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(2.0)

    r, g, b, a = _hex_a_rgba(color_hex)
    ctx.set_source_rgba(r, g, b, a)

    dibujante(ctx)

    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (render_w, render_h), buf, "raw", "BGRA", 0, 1).copy()
    return img.resize(size, Image.Resampling.LANCZOS)


def _generar_ctk_image_dual(
    dibujante: Callable[[cairo.Context], None],
    color: ColorParam,
    size: tuple[int, int],
) -> ctk.CTkImage:
    """Genera CTkImage con variantes light y dark renderizadas en vector."""
    color_light, color_dark = _resolver_par_colores(color)

    img_light = _renderizar_cairo(dibujante, color_light, size)
    if color_dark == color_light:
        img_dark = img_light
    else:
        img_dark = _renderizar_cairo(dibujante, color_dark, size)

    return ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=size)


def crear_icono_lupa(
    color: ColorParam = "#FFFFFF",
    size: tuple[int, int] = (28, 28),
) -> ctk.CTkImage:
    """Genera un ícono vectorial estilo Lucide 'search'."""
    def _dibujar(ctx: cairo.Context) -> None:
        ctx.new_sub_path()
        ctx.arc(10.5, 10.5, 7.5, 0, 2 * math.pi)
        ctx.stroke()

        ctx.move_to(21.0, 21.0)
        ctx.line_to(15.8, 15.8)
        ctx.stroke()

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_limpiar(
    color: ColorParam = ("#1E293B", "#F1F5F9"),
    size: tuple[int, int] = (28, 28),
) -> ctk.CTkImage:
    """Genera un ícono vectorial estilo Lucide 'eraser' para limpieza de filtros."""
    def _dibujar(ctx: cairo.Context) -> None:
        # Línea base horizontal (superficie)
        ctx.move_to(7.5, 20.5)
        ctx.line_to(21.5, 20.5)
        ctx.stroke()

        # Cuerpo del borrador inclinado a -45 grados con esquinas redondeadas
        ctx.save()
        ctx.translate(12.2, 12.2)
        ctx.rotate(-math.pi / 4.0)

        w, h, r = 15.0, 8.2, 2.0
        x0, y0 = -w / 2.0, -h / 2.0
        x1, y1 = w / 2.0, h / 2.0

        ctx.new_sub_path()
        ctx.arc(x1 - r, y0 + r, r, -math.pi / 2.0, 0.0)
        ctx.arc(x1 - r, y1 - r, r, 0.0, math.pi / 2.0)
        ctx.arc(x0 + r, y1 - r, r, math.pi / 2.0, math.pi)
        ctx.arc(x0 + r, y0 + r, r, math.pi, 3.0 * math.pi / 2.0)
        ctx.close_path()
        ctx.stroke()

        # Línea divisoria de la goma
        ctx.move_to(-1.2, y0)
        ctx.line_to(-1.2, y1)
        ctx.stroke()
        ctx.restore()

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_documento_plus(
    color: ColorParam = "#FFFFFF",
    size: tuple[int, int] = (28, 28),
) -> ctk.CTkImage:
    """Genera un ícono vectorial estilo Lucide 'file-plus-2' para registro."""
    def _dibujar(ctx: cairo.Context) -> None:
        # Contorno de documento con esquina superior derecha doblada
        ctx.move_to(4.5, 21.5)
        ctx.line_to(18.0, 21.5)
        ctx.arc_negative(18.0, 19.5, 2.0, math.pi / 2.0, 0.0)
        ctx.line_to(20.0, 7.5)
        ctx.line_to(14.5, 2.0)
        ctx.line_to(6.5, 2.0)
        ctx.arc_negative(6.5, 4.0, 2.0, 3.0 * math.pi / 2.0, math.pi)
        ctx.line_to(4.5, 9.0)
        ctx.stroke()

        # Doblez superior derecho
        ctx.move_to(14.5, 2.0)
        ctx.line_to(14.5, 6.0)
        ctx.arc_negative(16.0, 6.0, 1.5, math.pi, math.pi / 2.0)
        ctx.line_to(20.0, 7.5)
        ctx.stroke()

        # Símbolo '+' limpio en la esquina inferior izquierda
        ctx.move_to(2.5, 15.0)
        ctx.line_to(9.5, 15.0)
        ctx.stroke()

        ctx.move_to(6.0, 11.5)
        ctx.line_to(6.0, 18.5)
        ctx.stroke()

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_editar(
    color: ColorParam = "#FFFFFF",
    size: tuple[int, int] = (18, 18),
) -> ctk.CTkImage:
    """Genera un ícono vectorial estilo Lucide 'pencil' para edición."""
    def _dibujar(ctx: cairo.Context) -> None:
        # Cuerpo del lápiz inclinado
        ctx.move_to(17.5, 3.5)
        ctx.arc(19.0, 5.0, 2.1, -3 * math.pi / 4.0, math.pi / 4.0)
        ctx.line_to(7.5, 19.5)
        ctx.line_to(3.0, 21.0)
        ctx.line_to(4.5, 16.5)
        ctx.close_path()
        ctx.stroke()

        # Línea de la punta del lápiz
        ctx.move_to(14.5, 6.5)
        ctx.line_to(17.5, 9.5)
        ctx.stroke()

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_eliminar(
    color: ColorParam = "#FFFFFF",
    size: tuple[int, int] = (18, 18),
) -> ctk.CTkImage:
    """Genera un ícono vectorial estilo Lucide 'trash-2' para eliminación."""
    def _dibujar(ctx: cairo.Context) -> None:
        # Tapa superior
        ctx.move_to(3.5, 6.0)
        ctx.line_to(20.5, 6.0)
        ctx.stroke()

        # Asa de la tapa
        ctx.move_to(9.0, 6.0)
        ctx.line_to(9.0, 3.5)
        ctx.line_to(15.0, 3.5)
        ctx.line_to(15.0, 6.0)
        ctx.stroke()

        # Cuerpo de la papelera
        ctx.move_to(5.5, 6.0)
        ctx.line_to(6.5, 19.5)
        ctx.arc_negative(8.5, 19.5, 2.0, math.pi, math.pi / 2.0)
        ctx.line_to(15.5, 21.5)
        ctx.arc_negative(15.5, 19.5, 2.0, math.pi / 2.0, 0.0)
        ctx.line_to(18.5, 6.0)
        ctx.stroke()

        # Líneas interiores
        ctx.move_to(10.0, 10.5)
        ctx.line_to(10.0, 17.0)
        ctx.stroke()

        ctx.move_to(14.0, 10.5)
        ctx.line_to(14.0, 17.0)
        ctx.stroke()

    return _generar_ctk_image_dual(_dibujar, color, size)


def crear_icono_copiar(
    color: ColorParam = ("#1E293B", "#F1F5F9"),
    size: tuple[int, int] = (18, 18),
) -> ctk.CTkImage:
    """Genera un ícono vectorial estilo Lucide 'copy' para copiar ficha."""
    def _dibujar(ctx: cairo.Context) -> None:
        # Cuadro frontal (abajo derecha)
        r = 1.8
        x0, y0, x1, y1 = 8.5, 8.5, 20.5, 20.5
        ctx.new_sub_path()
        ctx.arc(x1 - r, y0 + r, r, -math.pi / 2.0, 0.0)
        ctx.arc(x1 - r, y1 - r, r, 0.0, math.pi / 2.0)
        ctx.arc(x0 + r, y1 - r, r, math.pi / 2.0, math.pi)
        ctx.arc(x0 + r, y0 + r, r, math.pi, 3.0 * math.pi / 2.0)
        ctx.close_path()
        ctx.stroke()

        # Cuadro trasero (arriba izquierda)
        ctx.move_to(5.0, 15.5)
        ctx.arc(5.5, 14.0, 1.5, math.pi / 2.0, math.pi)
        ctx.line_to(4.0, 5.5)
        ctx.arc(5.5, 5.5, 1.5, math.pi, 3.0 * math.pi / 2.0)
        ctx.line_to(14.0, 4.0)
        ctx.arc(14.0, 5.5, 1.5, 3.0 * math.pi / 2.0, 0.0)
        ctx.stroke()

    return _generar_ctk_image_dual(_dibujar, color, size)
