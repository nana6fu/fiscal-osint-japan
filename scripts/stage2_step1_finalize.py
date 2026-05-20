#!/usr/bin/env python3
"""Stage 2 Step 1 Finalize: OBデータ確定版＋落合健の context 拡張再スキャン"""
import json, re
from pathlib import Path

# --- 1. 落合健 周辺の context 拡張再スキャン（R4 PDF P7前後）---
print("=" * 60)
print("【1】 R4 PDF: いであ 周辺コンテキスト拡張スキャン")
print("=" * 60)

try:
    import pdfplumber
    R4_PDF = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/archives/ob_pdfs/040401-050331.pdf")
    with pdfplumber.open(R4_PDF) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if "いであ" in text:
                # context を 300字前後に広げる
                for m in re.finditer(r'いであ', text):
                    idx = m.start()
                    start = max(0, idx - 300)
                    end = min(len(text), idx + 300)
                    print(f"\nP{page_num} context (拡張):")
                    print(text[start:end])
                    print()
except ImportError:
    import subprocess
    R4_PDF = "/Volumes/SN0W8ALL/tokubetsu-kaikei/archives/ob_pdfs/040401-050331.pdf"
    r = subprocess.run(['pdftotext', '-layout', R4_PDF, '-'], capture_output=True, text=True)
    for m in re.finditer(r'いであ', r.stdout):
        idx = m.start()
        print(r.stdout[max(0,idx-300):idx+300])
        print()

# --- 2. JSON最終版を書き出し ---
print("\n" + "=" * 60)
print("【2】 OBデータ確定版 JSON 書き出し")
print("=" * 60)

DATA_DIR = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/data/stage2")

FINAL = {
  "meta": {
    "version": "v1.1-phase1-finalized",
    "scope": "Stage 2 Phase 1 - 防衛省系3社（東洋建設・いであ・オオバ）",
    "policy": "全レコード verified=True（一次資料PDF確認済み）。受注推移とのクロスはStep 3で実施。相関であり因果ではない。",
    "verification_date": "2026-05-20",
    "next_phase": "Phase 2: NEC（井上剛＝R4PDF P7記載確認済み、Step 1.5副産物）等のIT系を追加"
  },
  
  "ob_records": [
    {
      "id": "ob_idea_001",
      "ob_name": "落合健",
      "previous_role": "海上自衛隊幹部候補生学校 副校長／校務統括補佐",
      "previous_org": "防衛省（海上自衛隊）",
      "retirement_date": "2023-02-20",  # R5.2.20
      "reemployment_date": "2023-02-21",  # R5.2.21
      "current_company": "いであ株式会社",
      "industry": "環境計量証明業",
      "current_position": "主任研究員",
      "disclosure_pdf_year": "R4",
      "disclosure_pdf_file": "040401-050331.pdf",
      "disclosure_pdf_page": 7,
      "source_url": "https://www.mod.go.jp/j/profile/employ/saisyusyoku/index.html",
      "verified": True,
      "verification_note": "R4 PDF P7で 'いであ株式会社 環境計量証明業 主任研究員' を確認。退職日R5.2.20→再就職日R5.2.21（連日）",
      "related_bureau": "沖縄防衛局",
      "related_contracts_note": "沖縄防衛局の環境監視4業務 累計¥61.81億・99%+落札率（R5→R7継続独占）"
    },
    {
      "id": "ob_ooba_001",
      "ob_name": "坪倉幹男",
      "ob_age_at_retirement": 60,
      "previous_role": "北関東防衛局企画部長",
      "previous_org": "防衛省（北関東防衛局）",
      "retirement_date": "2023-03-31",  # R5.3.31
      "reemployment_date": "2023-06-01",  # R5.6.1
      "current_company": "株式会社オオバ",
      "industry": "建設コンサルタント",
      "current_position": "顧問（営業本部）",
      "disclosure_pdf_year": "R5",
      "disclosure_pdf_file": "050401-060331.pdf",
      "disclosure_pdf_page": 16,
      "disclosure_record_no": 75,
      "source_url": "https://www.mod.go.jp/j/profile/employ/saisyusyoku/index.html",
      "verified": True,
      "verification_note": "R5 PDF P16 #75 で確認。退職R5.3.31→再就職R5.6.1（約2ヶ月のブランク）",
      "related_bureau": "北関東防衛局",
      "related_contracts_note": "北関東防衛局から¥14.19億受注（同氏顧問就任後）"
    },
    {
      "id": "ob_toyo_001",
      "ob_name": "石倉三良",
      "ob_age_at_retirement": 59,
      "previous_role": "北海道防衛局長",
      "previous_org": "防衛省（北海道防衛局）",
      "retirement_date": "2023-07-14",  # R5.7.14
      "reemployment_date": "2023-11-01",  # R5.11.1
      "current_company": "東洋建設株式会社",
      "industry": "総合建設業（海上・陸上土木・建築）・不動産事業等",
      "current_position": "常務理事",
      "disclosure_pdf_year": "R5",
      "disclosure_pdf_file": "050401-060331.pdf",
      "disclosure_pdf_page": 17,
      "disclosure_record_no": 90,
      "source_url": "https://www.mod.go.jp/j/profile/employ/saisyusyoku/index.html",
      "verified": True,
      "verification_note": "R5 PDF P17 #90 で確認。退職R5.7.14→再就職R5.11.1（約4ヶ月ブランク）",
      "related_bureau": "北海道防衛局（起点）→ 全国地方防衛局",
      "related_contracts_note": "東洋建設は6地方防衛局以上で受注。R7単年で¥228億+"
    }
  ],

  "target_companies": [
    {
      "id": "idea", "name": "いであ株式会社", "category": "環境コンサル",
      "related_ob_ids": ["ob_idea_001"],
      "ob_entry_date": "2023-02-21",
      "fiscal_baseline": "OB入社年（2023）= R4年度末。実質R5/R6/R7で効果検証可能"
    },
    {
      "id": "ooba", "name": "株式会社オオバ", "category": "建設コンサル",
      "related_ob_ids": ["ob_ooba_001"],
      "ob_entry_date": "2023-06-01",
      "fiscal_baseline": "OB入社年（2023）= R5年度の途中。R6/R7でフル効果"
    },
    {
      "id": "toyo", "name": "東洋建設株式会社", "category": "建設・ゼネコン",
      "related_ob_ids": ["ob_toyo_001"],
      "ob_entry_date": "2023-11-01",
      "fiscal_baseline": "OB入社年（2023）= R5年度の途中。R6/R7でフル効果"
    }
  ],

  "phase2_candidates_discovered_in_scan": [
    {
      "ob_name": "井上剛",
      "ob_age_at_retirement": 57,
      "previous_role": "情報本部情報官",
      "current_company": "日本電気株式会社（NEC）",
      "current_position": "参与（嘱託）",
      "disclosure_pdf_year": "R4",
      "disclosure_pdf_file": "040401-050331.pdf",
      "disclosure_pdf_page": 7,
      "note": "Phase 2でNECを追加する際の起点。メモリ記載の『R5公表NEC5人』とは別の可能性あり、要突合"
    }
  ],

  "timeline": {
    "2023-02-21": "落合健 → いであ",
    "2023-06-01": "坪倉幹男 → オオバ",
    "2023-11-01": "石倉三良 → 東洋建設",
    "fiscal_year_alignment": "全員 R5年度内（2023-04~2024-03）に再就職。R5/R6/R7の3年で受注推移を分析可能"
  }
}

OUTPUT = DATA_DIR / "ob_index_v1_finalized.json"
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(FINAL, f, ensure_ascii=False, indent=2)

print(f"\n✓ 確定版JSON出力: {OUTPUT}")
print(f"\n--- 確定版サマリー ---")
for r in FINAL['ob_records']:
    print(f"  {r['reemployment_date']}  {r['ob_name']:6} ({r['previous_role'][:25]})")
    print(f"             → {r['current_company']} {r['current_position']}")
print(f"\n--- Phase 2 候補（副産物） ---")
for c in FINAL['phase2_candidates_discovered_in_scan']:
    print(f"  {c['ob_name']}（{c['ob_age_at_retirement']}歳）{c['previous_role']} → {c['current_company']}")
