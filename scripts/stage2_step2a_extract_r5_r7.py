#!/usr/bin/env python3
"""Stage 2 Step 2-A: index.html から R5/R7 の3社受注を抽出"""
import re, json
from pathlib import Path
from collections import defaultdict

HTML = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html")
OUT_DIR = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/data/stage2")
content = HTML.read_text(encoding="utf-8")

TARGET_COMPANIES = {
    "東洋建設": {"id": "toyo", "name": "東洋建設株式会社"},
    "いであ":   {"id": "idea", "name": "いであ株式会社"},
    "オオバ":   {"id": "ooba", "name": "株式会社オオバ"},
}

# index.htmlで grep済の局名（9局）
BUREAUS = ["HOKKAIDO", "TOHOKU", "N_KANTO", "S_KANTO", "KINKI_CHUBU",
           "CHUGOKU_SHIKOKU", "KYUSHU", "OKINAWA", "KUMAMOTO"]

# 局名の日本語表記マッピング
BUREAU_JP = {
    "HOKKAIDO": "北海道防衛局", "TOHOKU": "東北防衛局",
    "N_KANTO": "北関東防衛局", "S_KANTO": "南関東防衛局",
    "KINKI_CHUBU": "近畿中部防衛局", "CHUGOKU_SHIKOKU": "中国四国防衛局",
    "KYUSHU": "九州防衛局", "OKINAWA": "沖縄防衛局",
    "KUMAMOTO": "熊本防衛局",
}

results = {
    target["id"]: {
        "company_name": target["name"],
        "by_year": {"R5": {}, "R7": {}},  # 局別の詳細
        "year_totals": {"R5": {"cases": 0, "amount_oku": 0.0}, 
                        "R7": {"cases": 0, "amount_oku": 0.0}},
        "matched_records": []
    } for kw, target in TARGET_COMPANIES.items()
}

records_found = 0

for year in ["R5", "R7"]:
    for bureau in BUREAUS:
        var_name = f"MOD_{bureau}_{year}_COMPANY"
        pattern = rf'const\s+{var_name}\s*=\s*(\[.*?\])\s*;'
        m = re.search(pattern, content, re.DOTALL)
        if not m:
            continue
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON parse error: {var_name} ({e})")
            continue

        for rec in data:
            company_name = rec.get("company", "")
            for target_kw, target in TARGET_COMPANIES.items():
                if target_kw in company_name:
                    tid = target["id"]
                    detail = {
                        "matched_name": company_name,
                        "cases": rec.get("cases", 0),
                        "total_amount_oku": rec.get("total_amount_oku", 0),
                        "methods": rec.get("methods", ""),
                        "kinds": rec.get("kinds", ""),
                        "max_score": rec.get("max_score", 0),
                        "high_cases": rec.get("high_cases", 0),
                        "avg_rate_pct": rec.get("avg_rate_pct", 0),
                        "sample_project": rec.get("sample_project", ""),
                        "corp_number": rec.get("corp_number", ""),
                        "bureau": BUREAU_JP[bureau],
                        "year": year,
                    }
                    results[tid]["by_year"][year].setdefault(bureau, []).append(detail)
                    results[tid]["year_totals"][year]["cases"] += rec.get("cases", 0)
                    results[tid]["year_totals"][year]["amount_oku"] += rec.get("total_amount_oku", 0)
                    results[tid]["matched_records"].append(detail)
                    records_found += 1

# 出力
print("=" * 70)
print(f"Stage 2 Step 2-A: R5/R7 集計結果（{records_found}レコードヒット）")
print("=" * 70)

for tid, d in results.items():
    print(f"\n■ {d['company_name']} [{tid}]")
    print(f"  R5: {d['year_totals']['R5']['cases']}件 / ¥{d['year_totals']['R5']['amount_oku']:.2f}億")
    print(f"  R7: {d['year_totals']['R7']['cases']}件 / ¥{d['year_totals']['R7']['amount_oku']:.2f}億")
    
    delta_oku = d['year_totals']['R7']['amount_oku'] - d['year_totals']['R5']['amount_oku']
    if d['year_totals']['R5']['amount_oku'] > 0:
        pct = delta_oku / d['year_totals']['R5']['amount_oku'] * 100
        print(f"  Δ(R5→R7): ¥{delta_oku:+.2f}億 ({pct:+.1f}%)")
    
    for year in ["R5", "R7"]:
        for bureau, recs in d['by_year'][year].items():
            for r in recs:
                ratemarker = "🔴" if r['avg_rate_pct'] >= 99 else " "
                print(f"    [{year}] {ratemarker} {BUREAU_JP[bureau]:10} {r['cases']}件 ¥{r['total_amount_oku']:6.2f}億 ({r['avg_rate_pct']:.1f}% / {r['methods'][:15]} / {r['kinds']}) | {r['matched_name'][:35]}")

# JSON出力
OUT = OUT_DIR / "company_yearly_r5_r7.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n✓ JSON出力: {OUT}")

# R6 の所在確認（参考表示）
print(f"\n--- R6 データ確認 ---")
for path in [
    "/Volumes/SN0W8ALL/tokubetsu-kaikei/data/mod_2024/raw",
    "/Volumes/SN0W8ALL/tokubetsu-kaikei/data/防衛省/2023",
    "/Volumes/SN0W8ALL/tokubetsu-kaikei/data/mod",
    "/Volumes/SN0W8ALL/tokubetsu-kaikei/data/defense",
]:
    p = Path(path)
    if p.exists():
        print(f"\n  {path}:")
        for f in sorted(p.iterdir())[:15]:
            print(f"    {f.name}")
