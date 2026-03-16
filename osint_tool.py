#!/usr/bin/env python3
"""CLI OSINT/SOCMINT ética con ejecución automática de consultas públicas."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


@dataclass
class Hallazgo:
    fuente: str
    url: str
    fecha: str
    dato: str
    confiabilidad: float


@dataclass
class Reporte:
    nombre_objetivo: str
    apellido_objetivo: str
    caso: str
    fecha_generacion: str
    autorizado: bool
    modo: str
    ejecucion_automatica: bool
    hallazgos: list[Hallazgo]
    score_promedio: float
    advertencia: str


PANAMA_FUENTES_PUBLICAS = [
    {
        "fuente": "Gaceta Oficial de Panamá (búsqueda)",
        "url_template": "https://www.gacetaoficial.gob.pa/buscar-gacetas/?q={query}",
        "confiabilidad": 0.8,
    },
    {
        "fuente": "Órgano Judicial de Panamá (búsqueda web)",
        "url_template": "https://www.organojudicial.gob.pa/?s={query}",
        "confiabilidad": 0.6,
    },
    {
        "fuente": "Datos Abiertos Panamá (catálogo)",
        "url_template": "https://www.datosabiertos.gob.pa/search?query={query}",
        "confiabilidad": 0.7,
    },
]


_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _extraer_titulo(html: str) -> str:
    match = _TITLE_RE.search(html)
    if not match:
        return "Sin título detectable"
    return re.sub(r"\s+", " ", match.group(1)).strip()[:180]


def _resumen_html(html: str) -> str:
    texto = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    texto = re.sub(r"<style[\s\S]*?</style>", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:260] if texto else "Sin resumen de contenido"


def _consultar_url(url: str, timeout_s: int) -> tuple[bool, str]:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 OSINT-Tool/1.0"})
    try:
        with urlopen(req, timeout=timeout_s) as response:
            body = response.read(150_000).decode("utf-8", errors="replace")
            titulo = _extraer_titulo(body)
            resumen = _resumen_html(body)
            return True, f"OK | Título: {titulo} | Resumen: {resumen}"
    except Exception as exc:
        return False, f"ERROR al consultar fuente: {exc}"


def _cargar_hallazgos(path: Path | None) -> list[Hallazgo]:
    if path is None:
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    hallazgos: list[Hallazgo] = []
    for item in raw:
        hallazgos.append(
            Hallazgo(
                fuente=item.get("fuente", "desconocida"),
                url=item.get("url", ""),
                fecha=item.get("fecha", ""),
                dato=item.get("dato", ""),
                confiabilidad=float(item.get("confiabilidad", 0.0)),
            )
        )
    return hallazgos


def _hallazgos_automaticos(
    nombre: str,
    apellido: str,
    ejecutar_busqueda: bool,
    timeout_s: int,
) -> list[Hallazgo]:
    query = quote_plus(f'"{nombre} {apellido}"')
    now = datetime.now(tz=timezone.utc).date().isoformat()
    hallazgos: list[Hallazgo] = []

    for fuente in PANAMA_FUENTES_PUBLICAS:
        url = fuente["url_template"].format(query=query)
        if ejecutar_busqueda:
            ok, detalle = _consultar_url(url, timeout_s=timeout_s)
            dato = (
                "Consulta automática ejecutada. " + detalle
                if ok
                else "Consulta automática con fallo. " + detalle
            )
        else:
            dato = "Consulta preparada (modo solo links)."

        hallazgos.append(
            Hallazgo(
                fuente=fuente["fuente"],
                url=url,
                fecha=now,
                dato=dato,
                confiabilidad=float(fuente["confiabilidad"]),
            )
        )
    return hallazgos


def _score_promedio(hallazgos: list[Hallazgo]) -> float:
    if not hallazgos:
        return 0.0
    return round(sum(h.confiabilidad for h in hallazgos) / len(hallazgos), 3)


def generar_reporte(
    nombre: str,
    apellido: str,
    caso: str,
    autorizado: bool,
    modo: str,
    ejecucion_automatica: bool,
    hallazgos: list[Hallazgo],
) -> Reporte:
    if not autorizado:
        raise ValueError(
            "Debes confirmar autorización explícita para procesar datos personales."
        )

    return Reporte(
        nombre_objetivo=nombre,
        apellido_objetivo=apellido,
        caso=caso,
        fecha_generacion=datetime.now(tz=timezone.utc).isoformat(),
        autorizado=autorizado,
        modo=modo,
        ejecucion_automatica=ejecucion_automatica,
        hallazgos=hallazgos,
        score_promedio=_score_promedio(hallazgos),
        advertencia=(
            "Uso restringido a fines legítimos y conforme a ley aplicable "
            "(protección de datos, TOS y proporcionalidad). No usar para vigilancia masiva."
        ),
    )


def _to_json(reporte: Reporte) -> dict[str, Any]:
    data = asdict(reporte)
    data["hallazgos"] = [asdict(h) for h in reporte.hallazgos]
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera un reporte OSINT/SOCMINT ético con ejecución automática"
    )
    parser.add_argument("--nombre", required=True, help="Nombre de la persona")
    parser.add_argument("--apellido", required=True, help="Apellido de la persona")
    parser.add_argument("--caso", required=True, help="Motivo/caso legítimo")
    parser.add_argument(
        "--autorizado",
        action="store_true",
        help="Confirma autorización legal/organizacional para el procesamiento",
    )
    parser.add_argument(
        "--modo",
        choices=["manual", "auto"],
        default="auto",
        help="manual=usa --input; auto=consulta fuentes públicas automáticamente",
    )
    parser.add_argument(
        "--solo-links",
        action="store_true",
        help="En modo auto, no consulta fuentes; solo prepara URLs",
    )
    parser.add_argument(
        "--timeout", type=int, default=12, help="Timeout por fuente en segundos"
    )
    parser.add_argument(
        "--input", type=Path, default=None, help="JSON opcional de hallazgos"
    )
    parser.add_argument(
        "--output", type=Path, default=Path("reporte_osint.json"), help="Salida JSON"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ejecucion_automatica = args.modo == "auto" and not args.solo_links
    hallazgos = (
        _hallazgos_automaticos(
            args.nombre,
            args.apellido,
            ejecutar_busqueda=ejecucion_automatica,
            timeout_s=args.timeout,
        )
        if args.modo == "auto"
        else _cargar_hallazgos(args.input)
    )

    reporte = generar_reporte(
        nombre=args.nombre,
        apellido=args.apellido,
        caso=args.caso,
        autorizado=args.autorizado,
        modo=args.modo,
        ejecucion_automatica=ejecucion_automatica,
        hallazgos=hallazgos,
    )
    args.output.write_text(
        json.dumps(_to_json(reporte), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Reporte generado: {args.output}")


if __name__ == "__main__":
    main()
