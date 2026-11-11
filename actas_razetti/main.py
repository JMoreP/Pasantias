import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from controladores.acta_controlador import ActaControlador
from repositorios.acta_repositorio import ActaRepositorio
from servicios.acta_servicio import ActaServicio
from ui.ventana_consulta import VentanaConsulta

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    repo = ActaRepositorio()
    servicio = ActaServicio(repo)
    vista = VentanaConsulta()
    controlador = ActaControlador(vista, servicio)
    vista.asignar_controlador(controlador)
    vista.mainloop()
