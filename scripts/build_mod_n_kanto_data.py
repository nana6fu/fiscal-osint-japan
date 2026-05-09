import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE = Path("data/mod/n_kanto")
RAW = BASE / "raw"
OUT = BASE / "processed"
OUT.mkdir(parents=True, exist_ok=True)

def yen_to_oku(v):
    if pd.isna(v):
        return 0
    s = str(v).replace(",", "").replace("円", "").strip()
    try:
        return round(float(s) / 100_000_000, 2)
    except Exception:
        return 0

def rate_to_float(v):
    if pd.isna(v):
        return 0
    s = str(v).replace("%", "").strip()
    try:
        return round(float(s), 2)
    except Exception:
        return 0

def clean_text(v):
    if pd.isna(v):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()

def score_case(kind, project, company, method, amount_oku, planned_oku, rate_pct):
    score = 0
    reasons = []

    if rate_pct >= 99:
        score += 5
        reasons.append("落札率99%以上")
    elif rate_pct >= 98:
        score += 3
        reasons.append("落札率98%以上")
    elif rate_pct >= 97:
        score += 2
        reasons.append("落札率97%以上")

    if planned_oku and amount_oku:
        diff_oku = planned_oku - amount_oku
        if 0 <= diff_oku <= 0.1:
            score += 2
            reasons.append("予定価格との差1000万円以内")

    if "随意" in method:
        score += 3
        reasons.append("随意契約")
    if "プロポーザル" in method:
        score += 3
        reasons.append("プロポーザル方式")

    if any(k in company for k in ["共同体", "JV", "建設共同企業体"]):
        score += 2
        reasons.append("共同企業体・JV")

    if amount_oku >= 10:
        score += 2
        reasons.append("10億円以上")
    elif amount_oku >= 1:
        score += 1
        reasons.append("1億円以上")

    if any(k in project for k in ["米軍", "基地", "駐屯地", "防医大", "横田", "市ヶ谷", "三宿", "練馬", "立川", "木更津", "宇都宮", "百里", "新潟", "館山"]):
        score += 1
        reasons.append("基地・防衛施設関連")

    if score >= 8:
        level = "🔴 要確認度 高"
    elif score >= 5:
        level = "🟡 要確認度 中"
    else:
        level = "⚪ 通常"

    return score, level, " / ".join(reasons)

def parse_file(path, kind):
    df = pd.read_html(path)[0]
    df = df.iloc[5:].copy()

    rows = []
    for _, r in df.iterrows():
        project = clean_text(r.iloc[1])
        company = clean_text(r.iloc[2])
        amount_oku = yen_to_oku(r.iloc[4])
        planned_oku = yen_to_oku(r.iloc[5])
        rate_pct = rate_to_float(r.iloc[6])
        method = clean_text(r.iloc[9])

        if not project or amount_oku == 0:
            continue

        score, level, reason = score_case(kind, project, company, method, amount_oku, planned_oku, rate_pct)

        rows.append({
            "level": level,
            "score": score,
            "kind": kind,
            "project": project,
            "company": company,
            "company_clean": "",
            "method": method,
            "amount_oku": amount_oku,
            "planned_oku": planned_oku,
            "rate_pct": rate_pct,
            "reason": reason,
            "note": "",
            "bureau": "北関東防衛局",
            "source_url": "https://www.mod.go.jp/rdb/n-kanto/nyusatsu-keiyaku/kensetu/2024kekka/"
        })
    return rows

all_cases = []
all_cases += parse_file(RAW / "n_kanto_kouji.html", "工事")
all_cases += parse_file(RAW / "n_kanto_gyoumu.html", "業務")

top30 = sorted(all_cases, key=lambda x: (x["score"], x["amount_oku"]), reverse=True)[:30]

summary_map = defaultdict(lambda: {"bureau":"北関東防衛局", "cases":0, "total_amount_oku":0, "high_cases":0, "mid_cases":0, "max_score":0, "rates":[]})
for x in all_cases:
    s = summary_map[x["kind"]]
    s["kind"] = x["kind"]
    s["cases"] += 1
    s["total_amount_oku"] += x["amount_oku"]
    s["max_score"] = max(s["max_score"], x["score"])
    s["rates"].append(x["rate_pct"])
    if "高" in x["level"]:
        s["high_cases"] += 1
    elif "中" in x["level"]:
        s["mid_cases"] += 1

summary = []
for s in summary_map.values():
    rates = [r for r in s.pop("rates") if r]
    s["total_amount_oku"] = round(s["total_amount_oku"], 2)
    s["avg_rate_pct"] = round(sum(rates) / len(rates), 2) if rates else 0
    summary.append(s)

company_map = defaultdict(lambda: {"cases":0, "total_amount_oku":0, "max_score":0, "rates":[], "high_cases":0, "methods":set(), "sample_project":""})
for x in all_cases:
    c = company_map[x["company"]]
    c["company"] = x["company"]
    c["cases"] += 1
    c["total_amount_oku"] += x["amount_oku"]
    c["max_score"] = max(c["max_score"], x["score"])
    c["rates"].append(x["rate_pct"])
    if "高" in x["level"]:
        c["high_cases"] += 1
    if x["method"]:
        c["methods"].add(x["method"])
    if not c["sample_project"]:
        c["sample_project"] = x["project"]

companies = []
for c in company_map.values():
    rates = [r for r in c.pop("rates") if r]
    c["total_amount_oku"] = round(c["total_amount_oku"], 2)
    c["avg_rate_pct"] = round(sum(rates) / len(rates), 2) if rates else 0
    c["methods"] = " / ".join(sorted(c["methods"]))
    companies.append(c)

companies = sorted(companies, key=lambda x: (x["max_score"], x["total_amount_oku"]), reverse=True)[:20]

for name, data in [
    ("n_kanto_all_cases.json", all_cases),
    ("n_kanto_top30.json", top30),
    ("n_kanto_summary.json", summary),
    ("n_kanto_company.json", companies),
]:
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2))

print("all_cases", len(all_cases))
print("top30", len(top30))
print("summary", summary)
print("company", len(companies))
print("saved to", OUT)
