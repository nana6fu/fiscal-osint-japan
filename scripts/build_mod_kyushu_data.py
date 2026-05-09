import re
import json
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/mod/kyushu/raw")
OUT_DIR = Path("data/mod/kyushu/processed")

kouji_file = RAW_DIR / "kyushu_kouji.html"
gyoumu_file = RAW_DIR / "kyushu_gyoumu.html"

OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/index.html"

def clean_amount(v):
    s = str(v).replace(",", "").replace("¥", "").replace("円", "")
    nums = re.findall(r"[\d.]+", s)
    if not nums:
        return 0
    return float(nums[0]) / 100000000

def clean_rate(v):
    s = str(v).replace("%", "")
    nums = re.findall(r"[\d.]+", s)
    return float(nums[0]) if nums else 0

def clean_project(v):
    return re.sub(r"\(PDF:[^)]+\)", "", str(v)).strip()

def score_case(row):
    score = 0
    reasons = []

    rate = row["rate_pct"]
    method = row["method"]

    if rate >= 99:
        score += 5
        reasons.append("落札率99%以上")
    elif rate >= 98:
        score += 3
        reasons.append("落札率98%以上")

    if row["planned_oku"] and row["amount_oku"] and abs(row["planned_oku"] - row["amount_oku"]) <= 0.1:
        score += 2
        reasons.append("予定価格との差1000万円以内")

    if "随意" in method:
        score += 4
        reasons.append("随意契約")

    if "プロポーザル" in method:
        score += 3
        reasons.append("プロポーザル方式")

    if row["amount_oku"] >= 10:
        score += 2
        reasons.append("10億円以上")
    elif row["amount_oku"] >= 1:
        score += 1
        reasons.append("1億円以上")

    if any(k in row["project"] for k in ["基地","庁舎","隊舎","火薬庫","格納庫","滑走路","通信","訓練","弾薬","築城","佐世保","芦屋","大村","春日"]):
        score += 1
        reasons.append("基地・防衛施設関連")

    if score >= 8:
        level = "🔴 要確認度 高"
    elif score >= 5:
        level = "🟡 要確認度 中"
    else:
        level = "⚪ 通常"

    row["score"] = score
    row["level"] = level
    row["reason"] = " / ".join(reasons)

    return row

all_cases = []

def load_tables(path, kind):
    tables = pd.read_html(path)

    for df in tables:
        cols = [str(c) for c in df.columns]

        if "工事名" not in cols:
            continue

        for _, r in df.iterrows():
            project = clean_project(r.get("工事名", ""))

            if not project or "該当案件なし" in project:
                continue

            amount = clean_amount(r.get("落札金額等", r.get("契約金額", 0)))
            planned = clean_amount(r.get("予定価格", 0))
            rate = clean_rate(r.get("落札率", 0))

            if amount == 0:
                continue

            row = {
                "kind": kind,
                "project": project,
                "company": str(r.get("業者名", "")).strip(),
                "company_clean": "",
                "method": str(r.get("入札方法等", "")).strip(),
                "amount_oku": round(amount, 2),
                "planned_oku": round(planned, 2),
                "rate_pct": round(rate, 2),
                "note": "",
                "bureau": "九州防衛局",
                "source_url": BASE_URL
            }

            row = score_case(row)
            all_cases.append(row)

load_tables(kouji_file, "工事")
load_tables(gyoumu_file, "業務")

all_cases = sorted(all_cases, key=lambda x: (x["score"], x["amount_oku"]), reverse=True)
top30 = all_cases[:30]

company_map = {}

for x in all_cases:
    c = x["company"]

    if c not in company_map:
        company_map[c] = {
            "company": c,
            "cases": 0,
            "total_amount_oku": 0,
            "max_score": 0,
            "high_cases": 0,
            "methods": set(),
            "sample_project": x["project"],
            "avg_rate_pct": []
        }

    d = company_map[c]
    d["cases"] += 1
    d["total_amount_oku"] += x["amount_oku"]
    d["max_score"] = max(d["max_score"], x["score"])

    if "高" in x["level"]:
        d["high_cases"] += 1

    d["methods"].add(x["method"])
    d["avg_rate_pct"].append(x["rate_pct"])

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
    "bureau": "九州防衛局",
    "cases": len(all_cases),
    "total_amount_oku": round(sum(x["amount_oku"] for x in all_cases), 2),
    "high_cases": sum(1 for x in all_cases if "高" in x["level"]),
    "mid_cases": sum(1 for x in all_cases if "中" in x["level"]),
    "max_score": max(x["score"] for x in all_cases) if all_cases else 0,
    "kind": "工事・業務",
    "avg_rate_pct": round(sum(x["rate_pct"] for x in all_cases) / len(all_cases), 2) if all_cases else 0
}]

(OUT_DIR / "kyushu_all_cases.json").write_text(json.dumps(all_cases, ensure_ascii=False, indent=2))
(OUT_DIR / "kyushu_top30.json").write_text(json.dumps(top30, ensure_ascii=False, indent=2))
(OUT_DIR / "kyushu_company.json").write_text(json.dumps(company_list, ensure_ascii=False, indent=2))
(OUT_DIR / "kyushu_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))

print("all_cases", len(all_cases))
print("top30", len(top30))
print("company", len(company_list))
print("summary", summary)
print("saved to", OUT_DIR)
