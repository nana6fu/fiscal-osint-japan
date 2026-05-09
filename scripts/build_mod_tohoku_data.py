import json
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

RAW_DIR = Path("data/mod/tohoku/raw")
OUT_DIR = Path("data/mod/tohoku/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_FILES = [
    ("総務部", RAW_DIR / "tohoku_soumu.html"),
    ("企画部", RAW_DIR / "tohoku_kikaku.html"),
    ("調達部", RAW_DIR / "tohoku_choutatsu.html"),
]

SOURCE_URL = "https://www.mod.go.jp/rdb/tohoku/contract/result/R6/"


def clean_text(v):
    if v is None:
        return ""
    s = str(v)
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u3000", " ")
    s = re.sub(r"\(PDF:[^)]+\)", "", s)
    s = re.sub(r"（PDF:[^）]+）", "", s)
    return s.strip()


def clean_money(v):
    s = clean_text(v)
    s = s.replace(",", "").replace("円", "").replace("税込み", "")
    s = re.sub(r"[^\d.]", "", s)
    if not s:
        return 0.0
    try:
        return round(float(s) / 100000000, 2)
    except Exception:
        return 0.0


def clean_rate(v):
    s = clean_text(v).replace("%", "")
    s = re.sub(r"[^\d.]", "", s)
    try:
        return round(float(s), 2)
    except Exception:
        return 0.0


def classify_score(x):
    score = 0
    reasons = []

    project = x["project"]
    company = x["company"]
    method = x["method"]
    amount = x["amount_oku"]
    planned = x["planned_oku"]
    rate = x["rate_pct"]

    diff = abs(planned - amount)

    if rate >= 99.9:
        score += 4
        reasons.append("落札率99.9%以上")
    elif rate >= 99:
        score += 3
        reasons.append("落札率99%以上")
    elif rate >= 98:
        score += 2
        reasons.append("落札率98%以上")

    if planned and diff <= 0.01:
        score += 3
        reasons.append("予定価格との差100万円以内")
    elif planned and diff <= 0.1:
        score += 2
        reasons.append("予定価格との差1000万円以内")

    if "随意" in method:
        score += 4
        reasons.append("随意契約")

    if "プロポーザル" in method or "企画競争" in method:
        score += 3
        reasons.append("プロポーザル・企画競争")

    if any(k in company for k in ["共同体", "JV", "ＪＶ", "共同企業体"]):
        score += 2
        reasons.append("共同企業体・JV")

    if amount >= 10:
        score += 3
        reasons.append("10億円以上")
    elif amount >= 1:
        score += 1
        reasons.append("1億円以上")

    if any(k in project for k in ["施設最適化", "庁舎", "隊舎", "宿舎", "格納庫", "滑走路", "弾薬", "火薬庫", "通信", "飛行場", "基地"]):
        score += 1
        reasons.append("基地・防衛施設関連")

    if "追加工事" in project or "変更" in project:
        score += 2
        reasons.append("追加工事・変更契約")

    if score >= 8:
        level = "🔴 要確認度 高"
    elif score >= 5:
        level = "🟠 要確認度 中"
    else:
        level = "⚪ 通常"

    return score, level, " / ".join(reasons)


def infer_kind(table_title, fallback):
    t = clean_text(table_title)
    if "業務" in t:
        return "業務"
    if "工事" in t:
        return "工事"
    return fallback


def parse_file(section, path):
    if not path.exists():
        print("missing", path)
        return []

    try:
        dfs = pd.read_html(str(path))
    except Exception as e:
        print("read_html error", path, e)
        return []

    cases = []

    for df in dfs:
        if df.empty:
            continue

        cols = [clean_text(c) for c in df.columns]
        df.columns = cols
        joined = " ".join(cols)

        if "工事名" in joined:
            kind = "工事"
            name_col = "工事名"
        elif "業務名" in joined:
            kind = "業務"
            name_col = "業務名"
        elif "件名" in joined:
            kind = "工事・業務"
            name_col = "件名"
        else:
            continue

        required = ["業者名", "契約金額", "予定価格", "落札率", "入札方式"]
        if not all(any(req in c for c in cols) for req in required):
            continue

        def col_contains(key):
            for c in cols:
                if key in c:
                    return c
            return None

        company_col = col_contains("業者名")
        amount_col = col_contains("契約金額")
        planned_col = col_contains("予定価格")
        rate_col = col_contains("落札率")
        start_col = col_contains("工期始")
        end_col = col_contains("工期終")
        method_col = col_contains("入札方式")

        for _, r in df.iterrows():
            project = clean_text(r.get(name_col, ""))
            company = clean_text(r.get(company_col, ""))
            amount = clean_money(r.get(amount_col, ""))
            planned = clean_money(r.get(planned_col, ""))
            rate = clean_rate(r.get(rate_col, ""))
            start = clean_text(r.get(start_col, ""))
            end = clean_text(r.get(end_col, ""))
            method = clean_text(r.get(method_col, ""))

            if not project or amount <= 0:
                continue

            row = {
                "kind": kind,
                "project": project,
                "company": company,
                "company_clean": "",
                "method": method,
                "amount_oku": amount,
                "planned_oku": planned,
                "rate_pct": rate,
                "note": section,
                "bureau": "東北防衛局",
                "source_url": SOURCE_URL,
                "start": start,
                "end": end,
            }

            score, level, reason = classify_score(row)
            row["score"] = score
            row["level"] = level
            row["reason"] = reason

            cases.append(row)

    return cases

all_cases = []
for section, path in SOURCE_FILES:
    parsed = parse_file(section, path)
    print(section, len(parsed))
    all_cases.extend(parsed)

# 重複除去
seen = set()
unique = []
for x in all_cases:
    key = (x["project"], x["company"], x["amount_oku"], x["planned_oku"])
    if key in seen:
        continue
    seen.add(key)
    unique.append(x)

all_cases = unique

top30 = sorted(
    all_cases,
    key=lambda x: (x["score"], x["amount_oku"], x["rate_pct"]),
    reverse=True
)[:30]

company_map = {}
for x in all_cases:
    k = x["company"] or "不明"
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
    if x["method"]:
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
        "avg_rate_pct": round(sum(v["avg_rate_pct"]) / len(v["avg_rate_pct"]), 2) if v["avg_rate_pct"] else 0
    })

company_list = sorted(
    company_list,
    key=lambda x: (x["max_score"], x["total_amount_oku"]),
    reverse=True
)[:20]

summary = [{
    "bureau": "東北防衛局",
    "cases": len(all_cases),
    "total_amount_oku": round(sum(x["amount_oku"] for x in all_cases), 2),
    "high_cases": sum(1 for x in all_cases if "高" in x["level"]),
    "mid_cases": sum(1 for x in all_cases if "中" in x["level"]),
    "max_score": max([x["score"] for x in all_cases], default=0),
    "kind": "工事・業務",
    "avg_rate_pct": round(sum(x["rate_pct"] for x in all_cases) / len(all_cases), 2) if all_cases else 0
}]

(OUT_DIR / "tohoku_all_cases.json").write_text(json.dumps(all_cases, ensure_ascii=False, indent=2))
(OUT_DIR / "tohoku_top30.json").write_text(json.dumps(top30, ensure_ascii=False, indent=2))
(OUT_DIR / "tohoku_company.json").write_text(json.dumps(company_list, ensure_ascii=False, indent=2))
(OUT_DIR / "tohoku_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))

print("all_cases", len(all_cases))
print("top30", len(top30))
print("company", len(company_list))
print("summary", summary)
print("saved to", OUT_DIR)
