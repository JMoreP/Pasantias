
---

## 📄 Documento 2: Arquitectura de Software (`ARCHITECTURE.md`)

```markdown
# Arquitectura del Sistema - Actas de Presentación

## Patrón Arquitectónico: MVC + Repository

Se utiliza el patrón **Modelo-Vista-Controlador (MVC)** por ser el estándar para aplicaciones de escritorio en Python. La capa de acceso a datos se delega a un **Repositorio** para mantener el Modelo limpio de SQL.

### Capas y Responsabilidades

| Capa | Componente | Responsabilidad Principal |
| :--- | :--- | :--- |
| **Presentación** | `ui/` (View) | Construir la interfaz con CustomTkinter. Mostrar datos y capturar eventos del usuario. **Nunca** contiene lógica de negocio ni SQL. |
| **Control** | `controladores/` (Controller) | Orquestar la interacción: recibe eventos de la Vista, llama al Servicio/Modelo, y actualiza la Vista. **Nunca** manipula widgets directamente ni escribe SQL. |
| **Negocio** | `servicios/` (Service) | Contiene la lógica de negocio: validaciones, normalización (ej. cédula), reglas del dominio. |
| **Datos** | `repositorios/` (Repository) | Encapsula todo el acceso a SQLite. El resto del sistema no sabe que existe una base de datos. |
| **Persistencia** | `db/` | Módulo de conexión a SQLite y el archivo `.db`. |

### Estructura de Directorios

```text
actas_razetti/
├── main.py                     # Punto de entrada (arranca el Controller)
├── db/
│   ├── conexion.py             # Context manager para SQLite
│   └── actas.db                # Archivo de base de datos (generado)
├── repositorios/
│   └── acta_repositorio.py     # SQL puro (CRUD)
├── servicios/
│   └── acta_servicio.py        # Validaciones y reglas de negocio
├── controladores/
│   └── acta_controlador.py     # Une Vista, Servicio y Repositorio
├── ui/
│   ├── ventana_consulta.py     # Pantalla de búsqueda
│   └── formulario_acta.py      # Pantalla de registro/detalle
└── utils/
    └── cedula.py               # Normalización de C.I.