"""Estrategias de exportación del historial clínico de emergencia.

Patrón Strategy: un renderizador por formato. El contenido se construye en el
servidor a partir de los registros del propio usuario y se sanea antes de
serializar.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Protocol

from app.models.enums import ExportFormat


def _flatten(prefix: str, value: Any, rows: list[tuple[str, Any]]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            _flatten(path, item, rows)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _flatten(f"{prefix}[{index}]", item, rows)
    else:
        rows.append((prefix, "" if value is None else value))


class ExportStrategy(Protocol):
    name: str
    version: str
    media_type: str

    def render(self, data: dict[str, Any]) -> bytes: ...


class JsonExportStrategy:
    name = "json_medical"
    version = "1"
    media_type = "application/json"

    def render(self, data: dict[str, Any]) -> bytes:
        return json.dumps(
            data, ensure_ascii=False, indent=2, default=str
        ).encode("utf-8")


class CsvExportStrategy:
    name = "csv_insurer"
    version = "1"
    media_type = "text/csv"

    def render(self, data: dict[str, Any]) -> bytes:
        rows: list[tuple[str, Any]] = []
        _flatten("", data, rows)
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(["campo", "valor"])
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8")


EXPORT_STRATEGIES: dict[ExportFormat, ExportStrategy] = {
    ExportFormat.JSON: JsonExportStrategy(),
    ExportFormat.CSV: CsvExportStrategy(),
}


__all__ = ["CsvExportStrategy", "EXPORT_STRATEGIES", "ExportStrategy", "JsonExportStrategy"]
