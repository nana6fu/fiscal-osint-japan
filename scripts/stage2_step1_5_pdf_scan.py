#!/usr/bin/env python3
"""Stage 2 Step 1.5: 防衛省再就職PDF（R4/R5/R6）から対象3人＋関連企業名を検索"""
from pathlib import Path
import json
import re

PDF_DIR = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/archives/ob_pdfs")
PDFS = {
    "R4": PDF_DIR / "040401-050331.pdf",  # 2022-04~2023-03
    "R5": PDF_DIR / "050401-060331.pdf",  # 2023-04~2024-03
    "R6": PDF_DIR / "060401-070331.pdf",  # 2024-04~2025-03
}

# 検索ターゲット（人名 + 企業名）
SEARCH_TARGETS = {
    "人名": ["坪倉", "落合健", "石倉"],
    "企業名": ["オオバ", "いであ", "東洋建設"],
}

# pdfplumber 優先、ダメなら pdftotext
def extract_text(pdf_path):
    try:
        import pdfplumber
        text_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_pages.append(page.extract_text() or "")
        return text_pages
    except ImportError:
        import subprocess
        result = subprocess.run(['pdftotext', '-layout', str(pdf_path), '-'],
                                capture_output=True, text=True)
        # ページ区切りで分割
        return result.stdout.split('\x0c')

results = {}

for year, pdf_path in PDFS.items():
    print(f"\n{'=' * 70}")
    print(f"=== {year} ({pdf_path.name}) ===")
    print(f"{'=' * 70}")
    
    if not pdf_path.exists():
        print(f"  ⚠ ファイル未発見: {pdf_path}")
        continue
    
    text_pages = extract_text(pdf_path)
    print(f"  総ページ数: {len(text_pages)}")
    
    year_hits = {"人名": [], "企業名": []}
    
    for cat, terms in SEARCH_TARGETS.items():
        print(f"\n  ▼ {cat}検索")
        for term in terms:
            hits = []
            for page_num, text in enumerate(text_pages, 1):
                if not text: continue
                for m in re.finditer(re.escape(term), text):
                    idx = m.start()
                    start = max(0, idx - 80)
                    end = min(len(text), idx + 200)
                    context = text[start:end].replace('\n', ' | ').replace('  ', ' ')
                    hits.append({"page": page_num, "context": context})
            
            if hits:
                print(f"\n    [✓] 「{term}」: {len(hits)}件ヒット")
                for h in hits[:5]:  # 最大5件表示
                    print(f"      P{h['page']}: ...{h['context']}...")
                year_hits[cat].append({"term": term, "count": len(hits), "samples": hits[:3]})
            else:
                print(f"    [ ] 「{term}」: ヒットなし")
    
    results[year] = year_hits

# JSON保存
OUT = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/data/stage2/pdf_scan_results.json")
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 70}")
print(f"✓ スキャン完了: {OUT}")
print(f"\n--- サマリー ---")
for year, hits in results.items():
    n_persons = sum(h['count'] for h in hits['人名'])
    n_companies = sum(h['count'] for h in hits['企業名'])
    print(f"  {year}: 人名{n_persons}ヒット / 企業名{n_companies}ヒット")

print(f"\n--- 次のアクション ---")
print(f"  ・坪倉幹男のヒット年度 → JSON更新")
print(f"  ・落合健・石倉三良の階級・前職詳細を文脈から抽出")
print(f"  ・企業名ヒットから「同じ企業に再就職した他のOB」も発見できる可能性")
