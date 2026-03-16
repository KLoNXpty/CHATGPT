#!/usr/bin/env python3
"""Interfaz gráfica simple para generar reportes OSINT éticos."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from osint_tool import _to_json, generar_reporte, _hallazgos_automaticos


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("OSINT/SOCMINT Ético - Panamá")
        self.geometry("760x480")

        self.nombre = tk.StringVar()
        self.apellido = tk.StringVar()
        self.caso = tk.StringVar(value="Due diligence")
        self.autorizado = tk.BooleanVar(value=False)
        self.output = tk.StringVar(value="reporte_osint_gui.json")
        self.timeout = tk.IntVar(value=12)

        self._build()

    def _build(self) -> None:
        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.nombre, width=46).grid(row=0, column=1, sticky="ew")

        ttk.Label(frm, text="Apellido").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.apellido, width=46).grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Caso legítimo").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.caso, width=46).grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Archivo de salida").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.output, width=46).grid(row=3, column=1, sticky="ew")

        ttk.Label(frm, text="Timeout por fuente (s)").grid(row=4, column=0, sticky="w")
        ttk.Spinbox(frm, from_=3, to=60, textvariable=self.timeout, width=8).grid(
            row=4, column=1, sticky="w"
        )

        ttk.Checkbutton(
            frm,
            text="Confirmo autorización legal/organizacional",
            variable=self.autorizado,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 8))

        ttk.Button(frm, text="Ejecutar búsqueda automática", command=self.generar).grid(
            row=6, column=0, columnspan=2, pady=(10, 8)
        )

        self.log = tk.Text(frm, height=14)
        self.log.grid(row=7, column=0, columnspan=2, sticky="nsew")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(7, weight=1)

    def generar(self) -> None:
        try:
            nombre = self.nombre.get().strip()
            apellido = self.apellido.get().strip()
            caso = self.caso.get().strip()
            output = Path(self.output.get().strip())

            if not nombre or not apellido or not caso:
                raise ValueError("Completa nombre, apellido y caso.")

            hallazgos = _hallazgos_automaticos(
                nombre,
                apellido,
                ejecutar_busqueda=True,
                timeout_s=int(self.timeout.get()),
            )
            reporte = generar_reporte(
                nombre=nombre,
                apellido=apellido,
                caso=caso,
                autorizado=self.autorizado.get(),
                modo="auto",
                ejecucion_automatica=True,
                hallazgos=hallazgos,
            )

            output.write_text(
                json.dumps(_to_json(reporte), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            self.log.delete("1.0", tk.END)
            self.log.insert(
                tk.END,
                "Búsqueda automática ejecutada.\n\n"
                f"Archivo: {output}\n\n"
                + "\n".join(f"- {h.fuente}: {h.dato}" for h in hallazgos),
            )
            messagebox.showinfo("OK", f"Reporte generado en: {output}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    App().mainloop()
