from pathlib import Path
import json, subprocess, re

list_path = Path("data/mlit_r5_confirmed/kanto_r5_kouji_pdf_list.json")
pdf_dir = Path("data/mlit_r5_confirmed/kanto_r5_kouji_pdfs")
out_path = Path("data/mlit_r5_confirmed/kanto_r5_kouji_contracts.json")

items = json.loads(list_path.read_text(encoding="utf-8"))

def normalize(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def clean_money(s):
    s = normalize(s)
    s = s.replace("¥", "").replace("\\", "")
    s = s.replace("＋", "+")
    s = re.sub(r"^\+\s*", "", s)
    return s

def money_candidates(text):
    patterns = [
        r"[０-９0-9][０-９0-9，,]{3,}\s*円(?:（税込み）|\(税込み\))?",
        r"[¥\\][\s０-９0-9，,]{5,}(?:（税込み）|\(税込み\))?",
        r"[０-９0-9][０-９0-9，,]{3,}\s*(?:（税込み）|\(税込み\))",
    ]
    found = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            val = clean_money(m.group(0))
            # 小さい数量や日付っぽいものを避ける
            digits = re.sub(r"\D", "", val)
            if len(digits) >= 7:
                found.append((m.start(), val))
    return found

def extract_near_money(text, labels):
    best = []
    for label in labels:
        pos = text.find(label)
        if pos >= 0:
            window = text[pos:pos+500]
            cands = money_candidates(window)
            if cands:
                best.extend(cands)
    if best:
        return best[0][1]
    return ""

def extract_after_label_line(text, label):
    lines = [normalize(x) for x in text.splitlines()]
    for i, line in enumerate(lines):
        if line == label or label in line:
            for j in range(i+1, min(i+8, len(lines))):
                v = lines[j]
                if v and v not in ["契約業者の住所", "工事の名称", "工事場所", "工事種別"]:
                    return v
    return ""

records = []

for i, item in enumerate(items, 1):
    pdf = pdf_dir / f"{i:03d}.pdf"
    try:
        text = subprocess.check_output(
            ["pdftotext", str(pdf), "-"],
            text=True,
            errors="ignore"
        )
    except Exception as e:
        text = ""
        error = str(e)
    else:
        error = ""

    contractor = extract_after_label_line(text, "契約業者名")
    contractor_address = extract_after_label_line(text, "契約業者の住所")
    project_name = extract_after_label_line(text, "工事の名称")
    project_location = extract_after_label_line(text, "工事場所")
    work_type = extract_after_label_line(text, "工事種別")

    contract_amount = extract_near_money(text, [
        "変更後の契約金額",
        "契約金額",
        "変更前の契約金額",
    ])

    change_amount = extract_near_money(text, [
        "変更金額",
    ])

    records.append({
        "bureau": "関東地方整備局",
        "fiscal_year": "R5",
        "category": "工事",
        "source_type": "pdf",
        "index": i,
        "title_from_page": item.get("title", ""),
        "pdf_url": item.get("pdf_url", ""),
        "pdf_file": str(pdf),
        "contractor": contractor,
        "contractor_address": contractor_address,
        "project_name": project_name,
        "project_location": project_location,
        "work_type": work_type,
        "contract_amount": contract_amount,
        "change_amount": change_amount,
        "raw_text_head": normalize(text[:2000]),
        "extract_error": error,
    })

out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"saved: {out_path}")
print(f"count: {len(records)}")
