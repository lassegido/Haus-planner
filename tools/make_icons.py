#!/usr/bin/env python3
"""Erzeugt die App-Symbole in planner/icons/ (benötigt Playwright mit Chromium)."""
import os
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "planner", "icons")
os.makedirs(OUT, exist_ok=True)
SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="#2D6786"/>'
       '<g transform="translate(88 88) scale(14)" fill="none" stroke="#F5F3EB" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">'
       '<path d="M3.5 11 12 4l8.5 7"/><path d="M5.5 9.8V20h13V9.8"/><path d="M10 20v-5.5h4V20" fill="#FDAF54" stroke="#FDAF54"/></g></svg>')
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, size in (("icon-512", 512), ("icon-192", 192), ("apple-touch-icon", 180)):
        pg = b.new_page(viewport={"width": size, "height": size})
        pg.set_content('<body style="margin:0">' + SVG.replace("<svg ", '<svg width="%d" height="%d" ' % (size, size)) + "</body>")
        pg.screenshot(path=os.path.join(OUT, name + ".png"))
        pg.close()
    b.close()
print("Symbole erzeugt in", OUT)
