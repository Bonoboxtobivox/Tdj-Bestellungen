#!/usr/bin/env python3
"""Füllt das TdJ-Bestellformular Zusatzangebote aus einer JSON-Bestellliste.

Aufruf: python3 fill_bestellformular.py bestellungen.json leer.pdf ausgabe.pdf
"""
import io
import json
import sys

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
PAGE_H = 841.92
# Rastermaße des Formulars (pt, von oben gemessen)
COLS = [71.0, 131.5, 223.5, 402.0, 459.0, 538.5]
ROW_TOP, ROW_H, MAX_ROWS = 261.0, 30.75, 17
SIZE, PAD = 9, 4


def main(data_path, template, out):
    data = json.load(open(data_path, encoding="utf-8"))
    rows = data["bestellungen"]
    if len(rows) > MAX_ROWS:
        sys.exit(f"Zu viele Zeilen ({len(rows)} > {MAX_ROWS}) – zweites Formular nötig.")

    pdfmetrics.registerFont(TTFont("F", FONT))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595.32, PAGE_H))
    c.setFont("F", 11)
    c.drawString(76, PAGE_H - 197, data["kulturreferent"])
    c.drawString(357, PAGE_H - 197, data["schulnummer"])

    c.setFont("F", SIZE)
    for i, r in enumerate(rows):
        top = ROW_TOP + i * ROW_H
        l1, l2 = PAGE_H - (top + 12), PAGE_H - (top + 24)
        cells = [
            (r["datum"], ""),
            (r["theater"], ""),
            (r["stueck"], f"({r['name']})"),
            (str(r["anzahl"]), ""),
            (r["preis"], r.get("preis2", "")),
        ]
        for col, (a, b) in enumerate(cells):
            width = COLS[col + 1] - COLS[col] - 2 * PAD
            for text, y in ((a, l1), (b, l2)):
                if not text:
                    continue
                if pdfmetrics.stringWidth(text, "F", SIZE) > width:
                    sys.exit(f"Text passt nicht in Spalte {col + 1}: {text!r}")
                c.drawString(COLS[col] + PAD, y, text)
    c.save()

    page = PdfReader(template).pages[0]
    page.merge_page(PdfReader(buf).pages[0])
    w = PdfWriter()
    w.add_page(page)
    with open(out, "wb") as f:
        w.write(f)


if __name__ == "__main__":
    main(*sys.argv[1:4])
