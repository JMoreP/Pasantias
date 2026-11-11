# Esquema de Base de Datos - Sistema de Actas de Presentación
**Motor:** SQLite 3
**Archivo:** `db/actas.db`

## Tabla: `actas_presentacion`

Almacena los datos de cada Acta de Presentación de Hijo Natural digitada desde los libros físicos del Hospital "Doctor Luis Razetti".

| Columna | Tipo | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK AUTOINCREMENT | Identificador interno único |
| `numero_acta` | TEXT | NOT NULL | Número de acta del libro físico |
| `numero_libro` | TEXT | NOT NULL | Número de libro |
| `numero_folio` | TEXT | NOT NULL | Número de folio |
| `anio` | INTEGER | NOT NULL | Año del acta |
| `fecha_presentacion` | TEXT | NOT NULL | Fecha de presentación (formato ISO `YYYY-MM-DD`) |
| `presentado_nombres` | TEXT | NOT NULL | Nombre completo del niño/niña presentado |
| `presentado_sexo` | TEXT | CHECK(`sexo` IN ('niño', 'niña')) | Sexo del presentado |
| `presentado_fecha_nac` | TEXT | | Fecha de nacimiento (formato ISO `YYYY-MM-DD`) |
| `presentado_hora_nac` | TEXT | | Hora de nacimiento (formato `HH:MM`) |
| `presentado_tipo_parto` | TEXT | | 'Único', 'Gemelos', 'Mellizos', 'Múltiple' |
| `presentante_cedula` | TEXT | | C.I. del presentante (solo dígitos, sin prefijo V-) |
| `presentante_nombres` | TEXT | NOT NULL | Nombre completo del presentante |
| `estado` | TEXT | DEFAULT 'Barinas' | Estado de ubicación |
| `ciudad` | TEXT | DEFAULT 'Barinas' | Ciudad de ubicación |
| `recinto` | TEXT | DEFAULT 'Hospital "Doctor Luis Razetti"' | Recinto donde se registra |
| `observaciones` | TEXT | | Notas adicionales |
| `fecha_registro` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Fecha de digitación en el sistema |
| `fecha_actualizacion` | DATETIME | | Última modificación |

### Índices
- `idx_acta` -> `numero_acta`
- `idx_presentado_nombres` -> `presentado_nombres`
- `idx_presentante_nombres` -> `presentante_nombres`
- `idx_presentante_cedula` -> `presentante_cedula`
- `idx_fecha_presentacion` -> `fecha_presentacion`
- **Único compuesto** `idx_libro_folio_anio` -> `(numero_libro, numero_folio, anio)` (Evita duplicados por error de digitación)

### Script de Creación (SQL)

```sql
CREATE TABLE IF NOT EXISTS actas_presentacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_acta TEXT NOT NULL,
    numero_libro TEXT NOT NULL,
    numero_folio TEXT NOT NULL,
    anio INTEGER NOT NULL,
    fecha_presentacion TEXT NOT NULL,
    presentado_nombres TEXT NOT NULL,
    presentado_sexo TEXT CHECK(presentado_sexo IN ('niño', 'niña')),
    presentado_fecha_nac TEXT,
    presentado_hora_nac TEXT,
    presentado_tipo_parto TEXT,
    presentante_cedula TEXT,
    presentante_nombres TEXT NOT NULL,
    estado TEXT DEFAULT 'Barinas',
    ciudad TEXT DEFAULT 'Barinas',
    recinto TEXT DEFAULT 'Hospital "Doctor Luis Razetti"',
    observaciones TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME
);

CREATE INDEX IF NOT EXISTS idx_acta ON actas_presentacion(numero_acta);
CREATE INDEX IF NOT EXISTS idx_presentado_nombres ON actas_presentacion(presentado_nombres);
CREATE INDEX IF NOT EXISTS idx_presentante_nombres ON actas_presentacion(presentante_nombres);
CREATE INDEX IF NOT EXISTS idx_presentante_cedula ON actas_presentacion(presentante_cedula);
CREATE INDEX IF NOT EXISTS idx_fecha_presentacion ON actas_presentacion(fecha_presentacion);

CREATE UNIQUE INDEX IF NOT EXISTS idx_libro_folio_anio 
ON actas_presentacion(numero_libro, numero_folio, anio);