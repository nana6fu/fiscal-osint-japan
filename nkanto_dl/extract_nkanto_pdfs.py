#!/usr/bin/env python3
"""
北関東防衛局R7 PDF一括抽出スクリプト

使い方:
    pip install pdfplumber --break-system-packages
    python3 extract_nkanto_pdfs.py

入力: ./n_kanto_r7_pdfs/工事/*.pdf, ./n_kanto_r7_pdfs/業務/*.pdf
出力: 
    - ./nkanto_r7_all.json   (全案件データ)
    - ./nkanto_r7_errors.txt (抽出失敗案件のリスト)
    - ./nkanto_r7_summary.txt (サマリ統計)
"""
import os
import re
import sys
import json
import glob
import time
import pdfplumber

INPUT_DIR = "./n_kanto_r7_pdfs"
OUTPUT_JSON = "./nkanto_r7_all.json"
OUTPUT_ERRORS = "./nkanto_r7_errors.txt"
OUTPUT_SUMMARY = "./nkanto_r7_summary.txt"


def parse_yen(s):
    if not s:
        return None
    try:
        return int(s.replace(',', '').replace('，', ''))
    except (ValueError, AttributeError):
        return None


def cell(s):
    if not s:
        return ''
    return s.replace('\n', '').strip()


def cleantxt(s):
    if not s:
        return ''
    return re.sub(r'[\s\u3000]+', '', s)


EXCLUDE_LABELS = {'名称等', '住所', '契約業者名', '契約金額', '予定価格', '調査基準価格'}


def extract_case(pdf_path):
    """PDFから1案件を抽出"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return {'pdf': os.path.basename(pdf_path), 'error': 'no_pages'}
            page0_tables = pdf.pages[0].extract_tables()
    except Exception as e:
        return {'pdf': os.path.basename(pdf_path), 'error': f'pdf_open_failed: {e}'}

    r = {'pdf': os.path.basename(pdf_path)}
    if not page0_tables:
        r['error'] = 'no_tables'
        return r

    t1 = page0_tables[0]
    t2 = page0_tables[1] if len(page0_tables) >= 2 else None

    # 工事 or 業務 判定
    t1_text = ' '.join(cell(c) for row in t1 for c in row)
    if '工事名' in t1_text or '工事概要' in t1_text:
        r['kind'] = '工事'
    elif '業務の名称' in t1_text or '業務内容' in t1_text:
        r['kind'] = '業務'

    # Table 1: ラベル → 隣のセル
    for row in t1:
        for i, c in enumerate(row):
            cl = cleantxt(c)
            if cl in ('工事名', '業務の名称') and i + 1 < len(row):
                r['project'] = cell(row[i + 1])
            elif cl == '入札方式' and i + 1 < len(row):
                r['method'] = cell(row[i + 1])
            elif cl == '入札日' and i + 1 < len(row):
                r['bid_date'] = cell(row[i + 1])
            elif cl in ('工事場所', '履行場所') and i + 1 < len(row):
                r['location'] = cell(row[i + 1])
            elif cl in ('工期', '履行期間') and i + 1 < len(row):
                period = cell(row[i + 1])
                m = re.search(r'(令和\d+年\d+月\d+日)\s*[～~]\s*(令和\d+年\d+月\d+日)', period)
                if m:
                    r['start_date'] = m.group(1)
                    r['end_date'] = m.group(2)
            elif cl == '種別' and i + 1 < len(row):
                r['type_detail'] = cell(row[i + 1])

    # 参加者
    participants = []
    header_idx = None
    for i, row in enumerate(t1):
        if any(re.search(r'業\s*者\s*名', c or '') and ('商号' in (c or '') or '名称' in (c or '')) for c in row):
            header_idx = i
            break

    if header_idx is not None:
        for i in range(header_idx + 1, len(t1)):
            row = t1[i]
            name = cell(row[0])
            if not name or re.search(r'業\s*者\s*名', name):
                continue

            if r.get('project') and name.startswith(r['project']):
                name = name[len(r['project']):].strip()

            corp_id = ''
            bid_amount = None
            for c in row[1:]:
                cl = cell(c)
                if re.match(r'^\d{13}$', cl):
                    corp_id = cl
                elif re.match(r'^[\d,]{6,}$', cl) and ',' in cl:
                    val = parse_yen(cl)
                    if val and val < 1e12 and bid_amount is None:
                        bid_amount = val

            is_winner = any('落札' in cell(c) for c in row)

            participants.append({
                'name': name,
                'corp_id': corp_id,
                'bid_amount': bid_amount,
                'is_winner': is_winner,
            })

    r['participants'] = participants

    # Table 2: 契約結果
    if t2:
        for row in t2:
            joined = ' '.join(cell(c) for c in row)
            cells = [cell(c) for c in row]

            if '名称等' in joined and 'company' not in r:
                for c in cells:
                    cleaned = cleantxt(c)
                    if c and cleaned not in EXCLUDE_LABELS and len(cleaned) > 3:
                        comp = c
                        if r.get('project') and comp.startswith(r['project']):
                            comp = comp[len(r['project']):].strip()
                        r['company'] = comp
                        break

            if re.search(r'住\s*所', joined) and 'company_address' not in r:
                for c in cells:
                    cleaned = cleantxt(c)
                    if c and cleaned not in EXCLUDE_LABELS and not re.match(r'^住\s*所$', c.strip()) and len(cleaned) > 5:
                        r['company_address'] = c
                        break

            if '契約金額' in joined or '契 約 金 額' in joined:
                m = re.search(r'([0-9,]+)\s*[（(]税込.*?([0-9,]+)\s*[（(]税抜', joined)
                if m:
                    r['amount_incl'] = parse_yen(m.group(1))
                    r['amount_excl'] = parse_yen(m.group(2))

            if '予定価格' in joined or '予 定 価 格' in joined:
                m = re.search(r'([0-9,]+)\s*[（(]税込.*?([0-9,]+)\s*[（(]税抜', joined)
                if m:
                    r['predicted_incl'] = parse_yen(m.group(1))
                    r['predicted_excl'] = parse_yen(m.group(2))

            if '調査基準価格' in joined:
                m = re.search(r'([0-9,]+)\s*[（(]税込.*?([0-9,]+)\s*[（(]税抜', joined)
                if m:
                    r['base_price_incl'] = parse_yen(m.group(1))
                    r['base_price_excl'] = parse_yen(m.group(2))

    if r.get('amount_excl') and r.get('predicted_excl'):
        r['rate_pct'] = round(r['amount_excl'] / r['predicted_excl'] * 100, 2)
    if r.get('amount_excl'):
        r['amount_oku'] = round(r['amount_excl'] / 1e8, 4)

    # 落札者の法人番号を補足
    for p in participants:
        if p.get('is_winner') and p.get('corp_id'):
            r['corp_id'] = p['corp_id']
            break

    return r


def calc_score(rec):
    """重点確認スコア（沖縄・北海道と同じロジック）"""
    score = 0
    rate = rec.get('rate_pct') or 0
    method = rec.get('method') or ''
    company = rec.get('company') or ''
    project = rec.get('project') or ''
    amount_oku = rec.get('amount_oku') or 0

    if rate >= 99:
        score += 3
    elif rate >= 95:
        score += 1

    if '随意契約' in method:
        score += 3
    elif 'プロポーザル' in method:
        score += 2

    if '共同体' in company or '共同企業体' in company or '・' in company:
        score += 1

    if amount_oku >= 10:
        score += 2
    elif amount_oku >= 1:
        score += 1

    if '施設最適化' in project:
        score += 3
    if '技術協力業務' in project:
        score += 2
    if any(kw in project for kw in ['基地', '駐屯地', '航空', '海自', '陸自', '防医大']):
        score += 1

    return score


def main():
    if not os.path.isdir(INPUT_DIR):
        print(f"ERROR: {INPUT_DIR} がありません。download_nkanto_pdfs.py を先に実行してください。")
        sys.exit(1)

    all_cases = {'工事': [], '業務': []}
    errors = []
    t_start = time.time()

    for kind in ('工事', '業務'):
        pattern = os.path.join(INPUT_DIR, kind, '*.pdf')
        files = sorted(glob.glob(pattern))
        print(f"\n=== {kind} {len(files)}件 抽出開始 ===")

        for i, fp in enumerate(files, 1):
            r = extract_case(fp)
            r['source_file'] = os.path.basename(fp)

            if r.get('error'):
                errors.append((kind, fp, r.get('error')))
                print(f"  [{i:3d}/{len(files)}] ✗ {os.path.basename(fp)[:50]} - {r.get('error')}")
                continue

            # 必須項目チェック
            missing = []
            for k in ('project', 'amount_excl', 'predicted_excl', 'company'):
                if not r.get(k):
                    missing.append(k)
            if missing:
                errors.append((kind, fp, f"missing: {','.join(missing)}"))
                print(f"  [{i:3d}/{len(files)}] △ {os.path.basename(fp)[:50]} - missing:{missing}")

            # スコア計算
            r['score'] = calc_score(r)

            all_cases[kind].append(r)

            if (i % 20 == 0) or (i == len(files)):
                print(f"  [{i:3d}/{len(files)}] ... 進行中")

    # JSON出力
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'kouji': all_cases['工事'],
            'gyoumu': all_cases['業務'],
        }, f, ensure_ascii=False, indent=2)

    # エラーファイル
    with open(OUTPUT_ERRORS, 'w', encoding='utf-8') as f:
        f.write(f"カテゴリ\tファイル\tエラー内容\n")
        for kind, fp, err in errors:
            f.write(f"{kind}\t{os.path.basename(fp)}\t{err}\n")

    # サマリ
    elapsed = time.time() - t_start
    kouji_total = sum(c.get('amount_oku', 0) for c in all_cases['工事'])
    gyoumu_total = sum(c.get('amount_oku', 0) for c in all_cases['業務'])
    grand_total = kouji_total + gyoumu_total

    kouji_high = sum(1 for c in all_cases['工事'] if c.get('score', 0) >= 10)
    kouji_mid = sum(1 for c in all_cases['工事'] if 7 <= c.get('score', 0) < 10)
    gyoumu_high = sum(1 for c in all_cases['業務'] if c.get('score', 0) >= 10)
    gyoumu_mid = sum(1 for c in all_cases['業務'] if 7 <= c.get('score', 0) < 10)

    summary = f"""========================================
北関東防衛局 R7 集計サマリ
========================================

工事: {len(all_cases['工事'])}件 (¥{kouji_total:.2f}億円)
  高Score (≥10): {kouji_high}件
  中Score (7-9): {kouji_mid}件

業務: {len(all_cases['業務'])}件 (¥{gyoumu_total:.2f}億円)
  高Score (≥10): {gyoumu_high}件
  中Score (7-9): {gyoumu_mid}件

合計: {len(all_cases['工事']) + len(all_cases['業務'])}件 / ¥{grand_total:.2f}億円

エラー/欠損: {len(errors)}件
処理時間: {elapsed:.1f}秒

出力ファイル:
  - {OUTPUT_JSON}
  - {OUTPUT_ERRORS}
  - {OUTPUT_SUMMARY}
"""
    with open(OUTPUT_SUMMARY, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(summary)


if __name__ == "__main__":
    main()
