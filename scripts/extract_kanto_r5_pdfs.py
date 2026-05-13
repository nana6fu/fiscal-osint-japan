from pathlib import Path
import re, json, html
from urllib.parse import urljoin

base = "https://www.ktr.mlit.go.jp"
src = Path("data/mlit_r5_confirmed/kanto_r5_kouji_page.html")
out = Path("data/mlit_r5_confirmed/kanto_r5_kouji_pdf_list.json")

text = src.read_text(errors="ignore")

items = []
for m in re.finditer(r'<a href="([^"]+\.pdf)">([^<]+)\[PDF:([^\]]+)\]', text):
    href, title, size = m.groups()
    title = html.unescape(title).strip()
    if "Ｒ５" in title or "R5" in title or "（２３）" in title or "(23)" in title:
        items.append({
            "bureau": "関東地方整備局",
            "fiscal_year": "R5",
            "category": "工事",
            "source_type": "pdf",
            "title": title,
            "pdf_url": urljoin(base, href),
            "file_size": size,
        })

out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"saved: {out}")
print(f"count: {len(items)}")
