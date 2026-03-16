# OSINT/SOCMINT Ético por nombre y apellido (Panamá)

Herramienta OSINT/SOCMINT para casos legítimos (compliance, KYC, due diligence, investigación autorizada) que permite ejecutar consultas automáticas sobre fuentes públicas.

> ⚠️ **Límite importante:** no se diseñó para vigilancia masiva, doxxing, acoso ni para perfilar a "todos los ciudadanos".

## Incluye

- CLI en Python (`osint_tool.py`).
- Interfaz gráfica local (`osint_gui.py`).
- Script todo-en-uno (`setup_and_run.sh`) para instalar y ejecutar.
- Modo automático que **sí ejecuta** la consulta por fuente y guarda resumen básico por cada resultado.
- Exportación de reporte a JSON.
- Confirmación obligatoria de autorización con `--autorizado`.

## Ejecución automática (CLI)

```bash
python3 osint_tool.py --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
```

Ese comando consulta las fuentes configuradas automáticamente y genera `reporte_osint.json`.

### Opcional

- Solo generar URLs sin consultar: `--solo-links`
- Ajustar timeout por fuente: `--timeout 20`

## Ejecución automática (GUI)

```bash
python3 osint_gui.py
```

Pasos:
1. Completa nombre, apellido y caso.
2. Ajusta timeout (si quieres).
3. Marca autorización legal/organizacional.
4. Pulsa **Ejecutar búsqueda automática**.

## Script único (instalar y correr)

GUI:

```bash
./setup_and_run.sh --gui
```

CLI:

```bash
./setup_and_run.sh --cli --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
```

## Fuentes públicas configuradas

- Gaceta Oficial de Panamá
- Órgano Judicial de Panamá
- Datos Abiertos Panamá

## Recomendaciones de cumplimiento

1. Base legal y propósito documentado.
2. Minimización de datos personales.
3. Verificación humana de coincidencias.
4. Retención y borrado definidos.
5. Respeto a TOS y normativa de protección de datos.
