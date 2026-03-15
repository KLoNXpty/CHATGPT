#!/usr/bin/env python3
"""CLI OSINT/SOCMINT ética con soporte de fuentes públicas permitidas."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


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
    {
        "fuente": "Google (consulta abierta)",
        "url_template": "https://www.google.com/search?q={query}+site:.pa",
        "confiabilidad": 0.4,
    },
]


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


def _hallazgos_automaticos(nombre: str, apellido: str) -> list[Hallazgo]:
    query = quote_plus(f'"{nombre} {apellido}"')
    now = datetime.now(tz=timezone.utc).date().isoformat()
    hallazgos: list[Hallazgo] = []

    for fuente in PANAMA_FUENTES_PUBLICAS:
        hallazgos.append(
            Hallazgo(
                fuente=fuente["fuente"],
                url=fuente["url_template"].format(query=query),
                fecha=now,
                dato="Consulta automática generada para revisión manual y verificación de identidad.",
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
        description="Genera un reporte OSINT/SOCMINT ético con fuentes públicas permitidas"
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
        help="manual=usa --input; auto=crea consultas en fuentes públicas",
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

    hallazgos = (
        _hallazgos_automaticos(args.nombre, args.apellido)
        if args.modo == "auto"
        else _cargar_hallazgos(args.input)
    )

    reporte = generar_reporte(
        nombre=args.nombre,
        apellido=args.apellido,
        caso=args.caso,
        autorizado=args.autorizado,
        modo=args.modo,
        hallazgos=hallazgos,
    )
    args.output.write_text(
        json.dumps(_to_json(reporte), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Reporte generado: {args.output}")


if __name__ == "__main__":
    main()
