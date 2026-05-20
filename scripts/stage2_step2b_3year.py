#!/usr/bin/env python3
"""Stage 2 Step 2-B: R5/R6/R7 完全3年比較（3社×9局）"""
import re, json
from pathlib import Path

HTML = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html")
OUT_DIR = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/data/stage2")
content = HTML.read_text(encoding="utf-8")

TARGET_COMPANIES = {
    "東洋建設": {"id": "toyo", "name": "東洋建設株式会社"},
    "いであ":   {"id": "idea", "name": "いであ株式会社"},
    "オオバ":   {"id": "ooba", "name": "株式会社オオバ"},
}

BUREAUS = ["HOKKAIDO", "TOHOKU", "N_KANTO", "S_KANTO", "KINKI_CHUBU",
           "CHUGOKU_SHIKOKU", "KYUSHU", "OKINAWA", "KUMAMOTO"]
BUREAU_JP = {"HOKKAIDO": "北海道", "TOHOKU": "東北", "N_KANTO": "北関東",
             "S_KANTO": "南関東", "KINKI_CHUBU": "近畿中部",
             "CHUGOKU_SHIKOKU": "中国四国", "KYUSHU": "九州",
             "OKINAWA": "沖縄", "KUMAMOTO": "熊本"}

# 年度→変数名パターン（R6は「年度なし」が正解）
VAR_PATTERN = {
    "R5": "MOD_{bureau}_R5_COMPANY",
    "R6": "MOD_{bureau}_COMPANY",
    "R7": "MOD_{bureau}_R7_COMPANY",
}

results = {
    target["id"]: {
        "company_name": target["name"],
        "by_year": {y: {} for y in ["R5", "R6", "R7"]},
        "year_totals": {y: {"cases": 0, "amount_oku": 0.0} for y in ["R5", "R6", "R7"]},
        "matched_records": []
    } for kw, target in TARGET_COMPANIES.items()
}

for year in ["R5", "R6", "R7"]:
    for bureau in BUREAUS:
        var_name = VAR_PATTERN[year].format(bureau=bureau)
        pattern = rf'const\s+{var_name}\s*=\s*(\[.*?\])\s*;'
        m = re.search(pattern, content, re.DOTALL)
        if not m:
            continue
        try:
            data = json.loads(m.group(1))
        except:
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
                        "avg_rate_pct": rec.get("avg_rate_pct", 0),
                        "sample_project": rec.get("sample_project", ""),
                        "bureau": BUREAU_JP[bureau],
                        "year": year,
                    }
                    results[tid]["by_year"][year].setdefault(bureau, []).append(detail)
                    results[tid]["year_totals"][year]["cases"] += rec.get("cases", 0)
                    results[tid]["year_totals"][year]["amount_oku"] += rec.get("total_amount_oku", 0)
                    results[tid]["matched_records"].append(detail)

# 出力
print("=" * 78)
print("Stage 2 Step 2-B: R5/R6/R7 完全3年比較")
print("=" * 78)
print(f"\nOB入社タイムライン:")
print(f"  落合健    2023-02-21 → いであ（R4末・R5年度開始直前）")
print(f"  坪倉幹男  2023-06-01 → オオバ（R5年度途中）")
print(f"  石倉三良  2023-11-01 → 東洋建設（R5年度途中）")

for tid, d in results.items():
    print(f"\n{'─'*78}")
    print(f"■ {d['company_name']} [{tid}]")
    print(f"{'─'*78}")
    yt = d['year_totals']
    print(f"  R5: {yt['R5']['cases']:3}件 / ¥{yt['R5']['amount_oku']:8.2f}億   (OB入社年度・途中入社)")
    print(f"  R6: {yt['R6']['cases']:3}件 / ¥{yt['R6']['amount_oku']:8.2f}億   (OB入社後 フル稼働1年目)")
    print(f"  R7: {yt['R7']['cases']:3}件 / ¥{yt['R7']['amount_oku']:8.2f}億   (OB入社後 フル稼働2年目)")
    
    if yt['R5']['amount_oku'] > 0:
        pct_56 = (yt['R6']['amount_oku'] - yt['R5']['amount_oku']) / yt['R5']['amount_oku'] * 100
        print(f"  Δ(R5→R6): {pct_56:+.1f}%")
    if yt['R5']['amount_oku'] > 0:
        pct_57 = (yt['R7']['amount_oku'] - yt['R5']['amount_oku']) / yt['R5']['amount_oku'] * 100
        print(f"  Δ(R5→R7): {pct_57:+.1f}%")
    
    print(f"\n  局別詳細:")
    for year in ["R5", "R6", "R7"]:
        for bureau, recs in sorted(d['by_year'][year].items()):
            for r in recs:
                marker = "🔴" if r['avg_rate_pct'] >= 99 else "  "
                print(f"    [{year}] {marker} {BUREAU_JP[bureau]:6} {r['cases']:2}件 ¥{r['total_amount_oku']:7.2f}億 ({r['avg_rate_pct']:5.1f}%) | {r['matched_name'][:48]}")

# JSON出力
OUT = OUT_DIR / "company_yearly_r5_r6_r7.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n✓ JSON出力: {OUT}")

# 総括
print("\n" + "=" * 78)
print("総括サマリー")
print("=" * 78)
print(f"{'企業':10} {'R5':>10} {'R6':>10} {'R7':>10} {'パターン':25}")
for tid, d in results.items():
    yt = d['year_totals']
    r5 = yt['R5']['amount_oku']
    r6 = yt['R6']['amount_oku']
    r7 = yt['R7']['amount_oku']
    if r5 == 0 and (r6 > 0 or r7 > 0):
        pattern = "🚨 R5=0 → 受注発生"
    elif r5 < r6 < r7:
        pattern = "📈 単調増加"
    elif r5 > r6 and r6 > r7:
        pattern = "📉 単調減少"
    else:
        pattern = "📊 混在パターン"
    print(f"{d['company_name'][:10]:10} ¥{r5:7.2f}億 ¥{r6:7.2f}億 ¥{r7:7.2f}億   {pattern}")
