from pathlib import Path

p = Path("scripts/extract_kanto_r5_pdf_details.py")
s = p.read_text()

old = r'''m = re.search(r"([０-９0-9，,]+円(?:（税込み）|\(税込み\))?)", window)'''

new = r'''m = re.search(
            r"([¥\\＋+]?[\s０-９0-9，,]+(?:円)?(?:（税込み）|\\(税込み\\))?)",
            window
        )'''

s = s.replace(old, new)

p.write_text(s)
print("patched")
