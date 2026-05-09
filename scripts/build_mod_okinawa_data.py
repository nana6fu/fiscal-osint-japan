from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import json
import re

RAW_DIR = Path("data/mod/okinawa/raw")
OUT_DIR = Path("data/mod/okinawa/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    ("工事", RAW_DIR / "okinawa_kouji.html"),
    ("業務", RAW_DIR / "okinawa_gyoumu.html"),
]

all_cases = []

def clean_money(v):
    if not v:
        return 0
    v = str(v).replace(",", "").replace("円", "").strip()
    try:
        return int(v)
    except:
        return 0

def score_case(row):
    score = 0
    reasons = []

    rate = row["rate_pct"]

    if rate >= 99:
        score += 4
        reasons.append("落札率99%以上")

    diff = abs(row["planned_oku"] - row["amount_oku"])
    if diff <= 0.1:
        score += 3
        reasons.append("予定価格との差1000万円以内")

    if "随意" in row["method"]:
        score += 4
        reasons.append("随意契約")

    if row["amount_oku"] >= 10:
        score += 2
        reasons.append("10億円以上")

    if any(k in row["project"] for k in [
        "基地","弾薬","火薬","滑走路","通信","管制","庁舎","宿舎","施設最適化"
    ]):
        score += 1
        reasons.append("基地・防衛施設関連")

    if score >= 8:
        level = "🔴 要確認度 高"
    elif score >= 5:
        level = "🟠 要確認度 中"
    else:
        level = "⚪ 通常"

    return score, level, " / ".join(reasons)

for kind, fp in FILES:
    html = fp.read_text(errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")

        if len(rows) <= 1:
            continue

        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th","td"])]

        body = []

        for tr in rows[1:]:
            cols = [td.get_text(" ", strip=True) for td in tr.find_all("td")]

            if len(cols) != len(headers):
                continue

            if "該当案件なし" in "".join(cols):
                continue

            body.append(cols)

        if not body:
            continue

        df = pd.DataFrame(body, columns=headers)

        for _, r in df.iterrows():

            project = r.iloc[1]
            company = r.iloc[2]
            corp = r.iloc[3]
            amount = clean_money(r.iloc[4])
            planned = clean_money(r.iloc[5])

            try:
                rate = float(str(r.iloc[6]).replace("%",""))
            except:
                rate = 0

            start = r.iloc[7]
            end = r.iloc[8]
            method = r.iloc[9]

            item = {
                "kind": kind,
                "project": re.sub(r"\(PDF.*?\)", "", project).strip(),
                "company": company,
                "company_clean": "",
                "method": method,
                "amount_oku": round(amount / 100000000, 2),
                "planned_oku": round(planned / 100000000, 2),
                "rate_pct": round(rate, 2),
                "note": "",
                "bureau": "沖縄防衛局",
                "source_url": "https://www.mod.go.jp/rdb/okinawa/contract/construction/index.html",
                "start": start,
                "end": end
            }

            score, level, reason = score_case(item)

            item["score"] = score
            item["level"] = level
            item["reason"] = reason

            all_cases.append(item)

top30 = sorted(
    all_cases,
    key=lambda x: (x["score"], x["amount_oku"]),
    reverse=True
)[:30]

company_map = {}

for x in all_cases:
    k = x["company"]

    if k not in company_map:
        company_map[k] = {
            "company": k,
            "cases": 0,
            "total_amount_oku": 0,
            "max_score": 0,
            "high_cases": 0,
            "methods": set(),
            "sample_project": x["project"],
            "avg_rate_pct": []
        }

    v = company_map[k]

    v["cases"] += 1
    v["total_amount_oku"] += x["amount_oku"]
    v["max_score"] = max(v["max_score"], x["score"])

    if "高" in x["level"]:
        v["high_cases"] += 1

    v["methods"].add(x["method"])
    v["avg_rate_pct"].append(x["rate_pct"])

company_list = []

for v in company_map.values():
    company_list.append({
        "company": v["company"],
        "cases": v["cases"],
        "total_amount_oku": round(v["total_amount_oku"], 2),
        "max_score": v["max_score"],
        "high_cases": v["high_cases"],
        "methods": " / ".join(sorted(v["methods"])),
        "sample_project": v["sample_project"],
        "avg_rate_pct": round(sum(v["avg_rate_pct"]) / len(v["avg_rate_pct"]), 2)
    })

company_list = sorted(
    company_list,
    key=lambda x: (x["max_score"], x["total_amount_oku"]),
    reverse=True
)[:20]

summary = [{
    "bureau": "沖縄防衛局",
    "cases": len(all_cases),
    "total_amount_oku": round(sum(x["amount_oku"] for x in all_cases), 2),
    "high_cases": sum(1 for x in all_cases if "高" in x["level"]),
    "mid_cases": sum(1 for x in all_cases if "中" in x["level"]),
    "max_score": max(x["score"] for x in all_cases) if all_cases else 0,
    "kind": "工事・業務",
    "avg_rate_pct": round(sum(x["rate_pct"] for x in all_cases) / len(all_cases), 2)
}]

(OUT_DIR / "okinawa_all_cases.json").write_text(json.dumps(all_cases, ensure_ascii=False, indent=2))
(OUT_DIR / "okinawa_top30.json").write_text(json.dumps(top30, ensure_ascii=False, indent=2))
(OUT_DIR / "okinawa_company.json").write_text(json.dumps(company_list, ensure_ascii=False, indent=2))
(OUT_DIR / "okinawa_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))

print("all_cases", len(all_cases))
print("top30", len(top30))
print("company", len(company_list))
print("summary", summary)
print("saved to", OUT_DIR)
