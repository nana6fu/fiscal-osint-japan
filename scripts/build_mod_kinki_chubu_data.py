import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE = Path("data/mod/kinki_chubu")
RAW = BASE / "raw"
OUT = BASE / "processed"
OUT.mkdir(parents=True, exist_ok=True)

SOURCE = RAW / "kinki_chubu_result.html"

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
    s = re.sub(r"\(PDF:[^)]+\)", "", str(v))
    return re.sub(r"\s+", " ", s).strip()

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
    if "プロポーザル" in method or "ﾌﾟﾛﾎﾟｰｻﾞﾙ" in method:
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

    if any(k in project for k in ["米軍", "基地", "駐屯地", "祝園", "舞鶴", "伊丹", "小松", "岐阜", "八尾", "明野", "笠取山", "輪島", "守山", "今津", "大津"]):
        score += 1
        reasons.append("基地・防衛施設関連")

    if "災害復旧" in project:
        score += 1
        reasons.append("災害復旧系")

    if score >= 8:
        level = "🔴 要確認度 高"
    elif score >= 5:
        level = "🟡 要確認度 中"
    else:
        level = "⚪ 通常"

    return score, level, " / ".join(reasons)

def parse_table(df, kind):
    rows = []
    for _, r in df.iterrows():
        project = clean_text(r.iloc[0])
        company = clean_text(r.iloc[1])
        amount_oku = yen_to_oku(r.iloc[3])
        planned_oku = yen_to_oku(r.iloc[4])
        rate_pct = rate_to_float(r.iloc[5])
        method = clean_text(r.iloc[8])

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
            "bureau": "近畿中部防衛局",
            "source_url": "https://www.mod.go.jp/rdb/kinchu/contract/construction/about/result/index.html"
        })
    return rows

tables = pd.read_html(SOURCE)

# 確認済み: table 1 = 令和6年度 工事, table 7 = 令和6年度 業務
all_cases = []
all_cases += parse_table(tables[1], "工事")
all_cases += parse_table(tables[7], "業務")

top30 = sorted(all_cases, key=lambda x: (x["score"], x["amount_oku"]), reverse=True)[:30]

summary_map = defaultdict(lambda: {"bureau":"近畿中部防衛局", "cases":0, "total_amount_oku":0, "high_cases":0, "mid_cases":0, "max_score":0, "rates":[]})
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
    ("kinki_chubu_all_cases.json", all_cases),
    ("kinki_chubu_top30.json", top30),
    ("kinki_chubu_summary.json", summary),
    ("kinki_chubu_company.json", companies),
]:
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2))

print("all_cases", len(all_cases))
print("top30", len(top30))
print("summary", summary)
print("company", len(companies))
print("saved to", OUT)
