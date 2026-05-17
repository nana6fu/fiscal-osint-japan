#!/usr/bin/env python3
"""
北関東防衛局R7 PDF一括抽出スクリプト v2

修正点:
- フォーマット3種類対応 (normal / discretionary / kouji_kenmei)
- 「工事件名」と「工事名」の両対応
- 「随意契約結果書」フォーマット(Table1のみ)対応
- 複数ページにまたがる参加者リスト結合
- 空白入りラベル ('工 事 名'等) への正規化判定

使い方:
    pip install pdfplumber --break-system-packages
    python3 extract_nkanto_pdfs_v2.py
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
    """すべての空白除去（ラベル比較用）"""
    if not s:
        return ''
    return re.sub(r'[\s\u3000]+', '', s)


EXCLUDE_LABELS = {'名称等', '住所', '契約業者名', '契約金額', '予定価格', '調査基準価格', '法人番号', '契約の相手方'}


def detect_format(all_tables_flat):
    text = cleantxt(' '.join(cell(c) for t in all_tables_flat for row in t for c in row))
    if '選定理由' in text:
        return 'discretionary'
    if '工事件名' in text:
        return 'kouji_kenmei'
    return 'normal'


def extract_normal_or_kenmei(pdf_path):
    """通常入札 + 工事件名タイプ"""
    with pdfplumber.open(pdf_path) as pdf:
        page0_tables = pdf.pages[0].extract_tables()
        all_participant_tables = list(page0_tables)
        for p in pdf.pages[1:]:
            for t in p.extract_tables():
                if not t:
                    continue
                joined_clean = cleantxt(' '.join(cell(c) for row in t for c in row))
                if '業者名' in joined_clean and ('商号' in joined_clean or '名称' in joined_clean):
                    all_participant_tables.append(t)

    r = {}
    if not page0_tables:
        return r

    t1 = page0_tables[0]
    t2 = page0_tables[1] if len(page0_tables) >= 2 else None

    t1_text_clean = cleantxt(' '.join(cell(c) for row in t1 for c in row))
    if '工事名' in t1_text_clean or '工事件名' in t1_text_clean or '工事概要' in t1_text_clean:
        r['kind'] = '工事'
    elif '業務の名称' in t1_text_clean or '業務内容' in t1_text_clean:
        r['kind'] = '業務'

    for row in t1:
        for i, c in enumerate(row):
            cl = cleantxt(c)
            if cl in ('工事名', '工事件名', '業務の名称') and i + 1 < len(row):
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

    participants = []
    seen_names = set()
    for tbl in all_participant_tables:
        header_idx = None
        for i, row in enumerate(tbl):
            if any(re.search(r'業\s*者\s*名', c or '') and ('商号' in (c or '') or '名称' in (c or '')) for c in row):
                header_idx = i
                break
        if header_idx is None:
            continue
        for i in range(header_idx + 1, len(tbl)):
            row = tbl[i]
            name = cell(row[0])
            if not name or re.search(r'業\s*者\s*名', name):
                continue
            if r.get('project') and name.startswith(r['project']):
                name = name[len(r['project']):].strip()
            if not name or name in seen_names:
                continue
            seen_names.add(name)

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
                m = re.search(r'([0-9,]+)[\s（(]*税込.*?([0-9,]+)[\s（(]*税抜', joined)
                if m:
                    r['amount_incl'] = parse_yen(m.group(1))
                    r['amount_excl'] = parse_yen(m.group(2))
            if '予定価格' in joined or '予 定 価 格' in joined:
                m = re.search(r'([0-9,]+)[\s（(]*税込.*?([0-9,]+)[\s（(]*税抜', joined)
                if m:
                    r['predicted_incl'] = parse_yen(m.group(1))
                    r['predicted_excl'] = parse_yen(m.group(2))
            if '調査基準価格' in joined:
                m = re.search(r'([0-9,]+)[\s（(]*税込.*?([0-9,]+)[\s（(]*税抜', joined)
                if m:
                    r['base_price_incl'] = parse_yen(m.group(1))
                    r['base_price_excl'] = parse_yen(m.group(2))

    return r


def extract_discretionary(pdf_path):
    """随意契約結果書フォーマット"""
    with pdfplumber.open(pdf_path) as pdf:
        page0_tables = pdf.pages[0].extract_tables()

    r = {'method': '随意契約'}
    if not page0_tables:
        return r

    t1 = page0_tables[0]
    t1_text_clean = cleantxt(' '.join(cell(c) for row in t1 for c in row))
    r['kind'] = '工事' if ('工事名' in t1_text_clean or '工事件名' in t1_text_clean or '工事概要' in t1_text_clean) else '業務'

    for row in t1:
        cells = [cell(c) for c in row]
        joined = ' '.join(cells)

        for i, c in enumerate(cells):
            cl = cleantxt(c)
            if cl in ('工事名', '工事件名') and i + 1 < len(cells):
                r['project'] = cells[i + 1]
            elif cl == '工事場所' and i + 1 < len(cells):
                r['location'] = cells[i + 1]
            elif cl == '種別' and i + 1 < len(cells):
                r['type_detail'] = cells[i + 1]
            elif cl == '工期' and i + 1 < len(cells):
                period = cells[i + 1]
                m = re.search(r'(\d+\.\d+\.\d+)\s*[～~]\s*(\d+\.\d+\.\d+)', period)
                if m:
                    r['start_date'] = m.group(1)
                    r['end_date'] = m.group(2)
            elif cl == '名称等' and i + 1 < len(cells):
                comp = cells[i + 1]
                if r.get('project') and comp.startswith(r['project']):
                    comp = comp[len(r['project']):].strip()
                r['company'] = comp
            elif cl == '法人番号' and i + 1 < len(cells):
                if re.match(r'^\d{13}$', cells[i + 1]):
                    r['corp_id'] = cells[i + 1]
            elif cl == '住所' and i + 1 < len(cells):
                r['company_address'] = cells[i + 1]

        if '契約金額' in cleantxt(joined):
            m = re.search(r'([0-9,]+)\s*[（(]税込.*?([0-9,]+)\s*[（(]税抜', joined)
            if m:
                r['amount_incl'] = parse_yen(m.group(1))
                r['amount_excl'] = parse_yen(m.group(2))
        if '予定価格' in cleantxt(joined):
            m = re.search(r'([0-9,]+)\s*[（(]税込.*?([0-9,]+)\s*[（(]税抜', joined)
            if m:
                r['predicted_incl'] = parse_yen(m.group(1))
                r['predicted_excl'] = parse_yen(m.group(2))

    return r


def extract_case(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for p in pdf.pages:
                all_tables.extend(p.extract_tables())
    except Exception as e:
        return {'pdf': os.path.basename(pdf_path), 'error': f'pdf_open: {e}'}

    fmt = detect_format(all_tables)

    if fmt == 'discretionary':
        r = extract_discretionary(pdf_path)
    else:
        r = extract_normal_or_kenmei(pdf_path)

    r['pdf'] = os.path.basename(pdf_path)
    r['format'] = fmt

    if r.get('amount_excl') and r.get('predicted_excl'):
        r['rate_pct'] = round(r['amount_excl'] / r['predicted_excl'] * 100, 2)
    if r.get('amount_excl'):
        r['amount_oku'] = round(r['amount_excl'] / 1e8, 4)

    # 落札者の法人番号を補足
    for p in r.get('participants') or []:
        if p.get('is_winner') and p.get('corp_id'):
            r['corp_id'] = p['corp_id']
            break

    return r


def calc_score(rec):
    """重点確認スコア"""
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
        print(f"ERROR: {INPUT_DIR} がありません。")
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

            missing = []
            for k in ('project', 'amount_excl', 'predicted_excl', 'company'):
                if not r.get(k):
                    missing.append(k)
            if missing:
                errors.append((kind, fp, f"missing: {','.join(missing)}"))
                print(f"  [{i:3d}/{len(files)}] △ {os.path.basename(fp)[:50]} - missing:{missing}")

            r['score'] = calc_score(r)
            # kindフィールドが空の場合の補正
            if not r.get('kind'):
                r['kind'] = kind

            all_cases[kind].append(r)

            if (i % 20 == 0):
                print(f"  [{i:3d}/{len(files)}] ... 進行中")

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'kouji': all_cases['工事'],
            'gyoumu': all_cases['業務'],
        }, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_ERRORS, 'w', encoding='utf-8') as f:
        f.write("カテゴリ\tファイル\tエラー内容\n")
        for kind, fp, err in errors:
            f.write(f"{kind}\t{os.path.basename(fp)}\t{err}\n")

    elapsed = time.time() - t_start
    kouji_total = sum(c.get('amount_oku', 0) for c in all_cases['工事'])
    gyoumu_total = sum(c.get('amount_oku', 0) for c in all_cases['業務'])
    grand_total = kouji_total + gyoumu_total

    kouji_high = sum(1 for c in all_cases['工事'] if c.get('score', 0) >= 10)
    kouji_mid = sum(1 for c in all_cases['工事'] if 7 <= c.get('score', 0) < 10)
    gyoumu_high = sum(1 for c in all_cases['業務'] if c.get('score', 0) >= 10)
    gyoumu_mid = sum(1 for c in all_cases['業務'] if 7 <= c.get('score', 0) < 10)

    # 高スコア案件のリスト
    high_cases = [c for c in all_cases['工事'] + all_cases['業務'] if c.get('score', 0) >= 10]
    high_cases.sort(key=lambda x: -x.get('amount_oku', 0))

    summary = f"""========================================
北関東防衛局 R7 集計サマリ (v2)
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

【高Score案件 TOP10】
"""
    for i, c in enumerate(high_cases[:10], 1):
        summary += f"  #{i:2d} score={c['score']:>2} ¥{c.get('amount_oku',0):>7.2f}億 {c.get('rate_pct',0):>5.1f}%  {(c.get('project') or '')[:45]}\n"
        summary += f"      {(c.get('company') or '')[:80]}\n"

    with open(OUTPUT_SUMMARY, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(summary)


if __name__ == "__main__":
    main()
