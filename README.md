# OSINT/SOCMINT Ético por nombre y apellido (Panamá)

Esta herramienta permite generar un reporte base de investigación OSINT/SOCMINT para casos legítimos (compliance, KYC, due diligence, investigación autorizada).

> ⚠️ **Límite importante:** no se diseñó para vigilancia masiva, doxxing, acoso ni para perfilar a "todos los ciudadanos".

## Incluye

- CLI en Python (`osint_tool.py`).
- Interfaz gráfica local (`osint_gui.py`) con generación automática de enlaces de consulta.
- Script todo-en-uno para bajar/instalar/correr (`setup_and_run.sh`).
- Modo automático (`--modo auto`) con fuentes públicas permitidas en Panamá.
- Exportación de reporte a JSON.
- Confirmación obligatoria de autorización con `--autorizado`.

## Opción rápida: script único (descargar, instalar y correr)

### 1) Si ya estás dentro del proyecto

GUI:

```bash
./setup_and_run.sh --gui
```

CLI:

```bash
./setup_and_run.sh --cli --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
```

### 2) Si quieres que también lo descargue (clone)

```bash
./setup_and_run.sh --download "https://github.com/USUARIO/REPO.git" --dir "osint-panama" --gui
```

> El script crea un entorno virtual (`.venv`), actualiza `pip` y ejecuta GUI o CLI.

## Instalación y ejecución en Kali (paso a paso)

Si te aparece:

```bash
zsh: no such file or directory: ./setup_and_run.sh
```

significa que **no estás en la carpeta del proyecto**.

### Opción A: clonar y ejecutar

```bash
git clone https://github.com/USUARIO/REPO.git osint-panama
cd osint-panama
chmod +x setup_and_run.sh
./setup_and_run.sh --gui
```

### Opción B: si ya lo descargaste

```bash
cd /ruta/donde/esta/el/proyecto
chmod +x setup_and_run.sh
./setup_and_run.sh --gui
```

### Ejecutar por CLI (ejemplo)

```bash
./setup_and_run.sh --cli --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
```

## Uso CLI directo

```bash
python3 osint_tool.py --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
```

Salida por defecto: `reporte_osint.json`.

### Modo manual con hallazgos JSON

```bash
python3 osint_tool.py --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo manual --input hallazgos.json --output reporte.json
```

## Uso GUI directo

```bash
python3 osint_gui.py
```

Luego:
1. Completa nombre, apellido y caso.
2. Marca autorización legal/organizacional.
3. Pulsa **Generar reporte automático**.

## Fuentes automáticas (plantillas de consulta)

- Gaceta Oficial de Panamá (búsqueda)
- Órgano Judicial de Panamá (búsqueda web)
- Datos Abiertos Panamá (catálogo)
- Google restringido a `.pa`

Estas consultas deben revisarse manualmente para validar identidad (homónimos) y contexto.

## Recomendaciones de cumplimiento

1. Base legal y propósito documentado.
2. Minimización de datos personales.
3. Verificación humana de coincidencias.
4. Retención y borrado definidos.
5. Respeto a TOS y normativa de protección de datos.
