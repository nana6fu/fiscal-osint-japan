import json
import re
from pathlib import Path
from collections import defaultdict

import pdfplumber


def to_int(v):
    if v is None:
        return None
    s = str(v).replace(",", "").replace("円", "").replace("\n", "").strip()
    if not s or s in ["-", "－", ""]:
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def to_float(v):
    if v is None:
        return None
    s = str(v).replace("%", "").replace("\n", "").strip()
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def clean_text(v):
    if v is None:
        return ""
    return re.sub(r"\s+", " ", str(v).replace("\n", " ")).strip()


def clean_company(v):
    s = clean_text(v)
    # 住所が同じセルに入るため、原則1行目を会社名とみなす
    first = str(v or "").split("\n")[0].strip()
    first = re.sub(r"\s+", " ", first)
    return first


def kind_from_prefix(prefix):
    if prefix == "kk":
        return "工事"
    if prefix == "kg":
        return "業務"
    if prefix == "ke":
        return "役務"
    return "不明"


def calc_score(r):
    score = 0
    reasons = []

    rate = r.get("rate_pct") or 0
    amount_oku = r.get("amount_oku") or 0
    method = r.get("method", "")
    company = r.get("company_clean", "")
    project = r.get("project", "")

    if rate >= 99:
        score += 3
        reasons.append("落札率99%以上")
    elif rate >= 95:
        score += 1
        reasons.append("落札率95%以上")

    if "随意" in method:
        score += 3
        reasons.append("随意契約")

    if "プロポーザル" in method:
        score += 2
        reasons.append("プロポーザル方式")

    if amount_oku >= 10:
        score += 3
        reasons.append("10億円以上")
    elif amount_oku >= 1:
        score += 1
        reasons.append("1億円以上")

    org_words = ["建設弘済会", "地域づくり", "建設マネジメント"]
    if any(w in company for w in org_words):
        score += 3
        reasons.append("建設協会・弘済会系")

    support_words = ["事業監理", "監督支援", "積算技術", "技術審査", "資料作成", "発注者支援"]
    if any(w in project for w in support_words):
        score += 2
        reasons.append("発注者支援系業務")

    return score, " / ".join(reasons)


def level_from_score(score):
    if score >= 10:
        return "高"
    if score >= 6:
        return "中"
    if score >= 4:
        return "低"
    return ""


def parse_pdf(path):
    prefix = path.name[:2]
    kind = kind_from_prefix(prefix)
    records = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                for row in table[1:]:
                    if not row or len(row) < 10:
                        continue

                    project = clean_text(row[0])
                    if not project or "名称" in project:
                        continue

                    bureau = clean_text(row[1])
                    contract_date = clean_text(row[2])
                    company_raw = row[3]
                    company = clean_company(company_raw)
                    method = clean_text(row[5])
                    planned = to_int(row[6])
                    amount = to_int(row[7])
                    rate = to_float(row[8])
                    memo = clean_text(row[9])

                    if not amount:
                        continue

                    if rate is None and planned:
                        rate = round(amount / planned * 100, 2)

                    r = {
                        "kind": kind,
                        "bureau": bureau,
                        "project": project,
                        "company": clean_text(company_raw),
                        "company_clean": company,
                        "method": method,
                        "type_kind": kind,
                        "is_sougou": "有" if "総合" in method else "",
                        "bid_date": "",
                        "contract_date": contract_date,
                        "predicted_excl": planned,
                        "contract_amount_excl": amount,
                        "amount_oku": round(amount / 1e8, 4),
                        "planned_oku": round(planned / 1e8, 4) if planned else 0,
                        "rate_pct": rate or 0,
                        "memo": memo,
                        "source_file": path.name,
                        "region": "四国",
                    }

                    score, reason = calc_score(r)
                    r["score"] = score
                    r["reason"] = reason
                    r["level"] = level_from_score(score)
                    records.append(r)

    return records


def main():
    print("=" * 70)
    print("四国地方整備局 R7 PDF → JSON抽出 v1")
    print("=" * 70)

    all_records = []
    for pdf in sorted(Path("r7_pdf").glob("*.pdf")):
        rows = parse_pdf(pdf)
        all_records.extend(rows)
        print(f"{pdf.name}: {len(rows)}件")

    kouji = [r for r in all_records if r["kind"] == "工事"]
    gyoumu = [r for r in all_records if r["kind"] == "業務"]
    ekimu = [r for r in all_records if r["kind"] == "役務"]

    total_amount = round(sum(r["amount_oku"] for r in all_records), 2)
    kouji_amount = round(sum(r["amount_oku"] for r in kouji), 2)
    gyoumu_amount = round(sum(r["amount_oku"] for r in gyoumu), 2)
    ekimu_amount = round(sum(r["amount_oku"] for r in ekimu), 2)

    levels = defaultdict(int)
    for r in all_records:
        if r["level"]:
            levels[r["level"]] += 1

    print("\n" + "=" * 70)
    print("=== 四国R7 集計 ===")
    print("=" * 70)
    print(f"  工事: {len(kouji)}件 ¥{kouji_amount:.2f}億")
    print(f"  業務: {len(gyoumu)}件 ¥{gyoumu_amount:.2f}億")
    print(f"  役務: {len(ekimu)}件 ¥{ekimu_amount:.2f}億")
    print(f"  合計: {len(all_records)}件 ¥{total_amount:.2f}億")

    print("\n=== 要確認度別 ===")
    print(f"  高: {levels['高']}件")
    print(f"  中: {levels['中']}件")
    print(f"  低: {levels['低']}件")

    print("\n=== 高Score TOP20 ===")
    for r in sorted(all_records, key=lambda x: (-x.get("score", 0), -x.get("amount_oku", 0)))[:20]:
        print(f"  S={r['score']:>2} ¥{r['amount_oku']:>7.2f}億 [{r['rate_pct']:>5.1f}%] {r['method'][:16]:<16} {r['kind']} {r['project'][:60]}")
        print(f"      {r['company_clean']}")
        print(f"      reason: {r['reason']}")

    out = {
        "meta": {
            "bureau": "四国地方整備局",
            "year": "R7",
            "kouji_count": len(kouji),
            "gyoumu_count": len(gyoumu),
            "ekimu_count": len(ekimu),
            "total_count": len(all_records),
            "kouji_amount_oku": kouji_amount,
            "gyoumu_amount_oku": gyoumu_amount,
            "ekimu_amount_oku": ekimu_amount,
            "total_amount_oku": total_amount,
            "high_score_count": levels["高"],
            "mid_score_count": levels["中"],
        },
        "all_cases": all_records,
    }

    Path("shikoku_r7_all_full.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n→ shikoku_r7_all_full.json 保存完了")


if __name__ == "__main__":
    main()
