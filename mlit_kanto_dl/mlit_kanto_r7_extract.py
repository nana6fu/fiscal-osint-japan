#!/usr/bin/env python3
"""
関東地方整備局 R7 Excel → JSON抽出

入力: ./mlit_kanto_r7/{kouji,gyoumu}/r7_{月}.xls (24本、ダウンロード済み前提)
出力: kanto_r7_all.json

データ構造:
  1案件 = 複数行（入札参加者ごと）
  → groupby (工事名+入札日+契約日) で集約
  → 「見積金額」（落札金額）が入っている行 = 落札者
"""
import os
import re
import json
import pandas as pd
from collections import defaultdict

INPUT_DIR = "./mlit_kanto_r7"
OUTPUT_JSON = "kanto_r7_all.json"


def yen(v):
    """整数化、NaN/-を None に"""
    if pd.isna(v): return None
    if isinstance(v, str):
        v = v.replace(',','').strip()
        if v in ('-', '', '－', '－'): return None
        try: return int(v)
        except: return None
    try: return int(v)
    except: return None


def parse_month_excel(path, kind):
    """1ヶ月分のExcelをパースしてレコードリスト化"""
    try:
        df = pd.read_excel(path, engine='xlrd', header=None)
    except Exception as e:
        print(f"  ✗ {path}: {e}")
        return []
    
    # ヘッダー行を検出（「部局名」を含む行）
    header_row = None
    for i in range(min(10, len(df))):
        row_str = ' '.join(str(c) for c in df.iloc[i].values if not pd.isna(c))
        if '部局名' in row_str:
            header_row = i
            break
    if header_row is None:
        print(f"  ✗ {path}: ヘッダー行が見つからない")
        return []
    
    # データ開始行はheader_row+3 (ヘッダー+サブヘッダー2行を飛ばす)
    data_start = header_row + 3
    
    # カラム位置を固定で割り当て (Excel構造から)
    # 0:部局名, 1:工事名, 2:入札日, 3:契約日, 4:工種区分, 5:入札方式, 6:総合評価の有無,
    # 7:入札業者名, 8:予定価格, 9:調査基準価格, 10:基礎点+加算点,
    # 11-12:1回目金額/評価値, 13-14:2回目, 15-16:3回目,
    # 17:見積金額(=落札金額), 18:備考
    
    raw_records = []
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        bureau = str(row[0]) if not pd.isna(row[0]) else ''
        project = str(row[1]) if not pd.isna(row[1]) else ''
        
        # 工事名が空ならスキップ（マージセル等の理由）
        if not project or project == 'nan': continue
        if '関東地方整備局' not in bureau and '事務所' not in bureau and 'NaN' in bureau:
            continue
        
        bid_date = row[2] if not pd.isna(row[2]) else None
        contract_date = row[3] if not pd.isna(row[3]) else None
        type_kind = str(row[4]) if not pd.isna(row[4]) else ''
        method = str(row[5]) if not pd.isna(row[5]) else ''
        is_sougou = str(row[6]) if not pd.isna(row[6]) else ''
        company = str(row[7]) if not pd.isna(row[7]) else ''
        predicted = yen(row[8])
        base_price = yen(row[9])
        # 見積金額 (落札額) - 19列目(index 17)
        contract_amount = yen(row[17]) if len(row) > 17 else None
        memo = str(row[18]) if len(row) > 18 and not pd.isna(row[18]) else ''
        
        # 入札結果ステータス (11列目あたり)
        # 「入札結果」が「辞退」「無効」なら除外
        bid_status = str(row[11]) if not pd.isna(row[11]) else ''
        
        raw_records.append({
            'bureau': bureau.strip(),
            'project': project.strip(),
            'bid_date': str(bid_date)[:10] if bid_date else '',
            'contract_date': str(contract_date)[:10] if contract_date else '',
            'type_kind': type_kind.strip(),
            'method': method.strip(),
            'is_sougou': is_sougou.strip(),
            'company': company.strip(),
            'predicted_excl': predicted,
            'base_price_excl': base_price,
            'contract_amount_excl': contract_amount,
            'bid_status': bid_status.strip(),
            'memo': memo.strip(),
        })
    
    return raw_records


def aggregate_to_cases(raw_records):
    """1案件=複数行 → 1案件=1レコードに集約 (落札者を特定)"""
    # 工事名+契約日 でグループ化
    groups = defaultdict(list)
    for r in raw_records:
        key = (r['project'], r['contract_date'])
        groups[key].append(r)
    
    cases = []
    for (project, contract_date), records in groups.items():
        # 落札者特定: contract_amount_excl が入っている記録 = 落札者
        winners = [r for r in records if r['contract_amount_excl']]
        if not winners:
            # 全員辞退・無効
            continue
        
        # 通常は1業者だけ落札する
        # 複数いる場合は、契約金額が最大の業者を落札者とする(同金額なら最初)
        winner = max(winners, key=lambda x: x['contract_amount_excl'])
        
        # 落札率
        rate_pct = 0
        if winner['contract_amount_excl'] and winner['predicted_excl']:
            rate_pct = round(winner['contract_amount_excl'] / winner['predicted_excl'] * 100, 2)
        
        # 参加業者リスト
        all_companies = [r['company'] for r in records if r['company'] and r['company'] != 'nan']
        
        cases.append({
            'bureau': winner['bureau'],
            'project': project,
            'kind': '工事' if 'kouji' in str(records[0]) else '',  # 後で上書き
            'company': winner['company'],
            'method': winner['method'],
            'type_kind': winner['type_kind'],
            'contract_date': contract_date,
            'bid_date': winner['bid_date'],
            'predicted_excl': winner['predicted_excl'],
            'contract_amount_excl': winner['contract_amount_excl'],
            'amount_oku': round(winner['contract_amount_excl']/1e8, 4) if winner['contract_amount_excl'] else 0,
            'rate_pct': rate_pct,
            'is_sougou': winner['is_sougou'],
            'num_participants': len(all_companies),
            'participants': all_companies[:30],  # 最大30人まで
            'memo': winner['memo'],
        })
    
    return cases


def calc_score(rec):
    score = 0
    rate = rec.get('rate_pct') or 0
    method = rec.get('method') or ''
    company = rec.get('company') or ''
    project = rec.get('project') or ''
    amount_oku = rec.get('amount_oku') or 0
    if rate >= 99: score += 3
    elif rate >= 95: score += 1
    if '随意契約' in method: score += 3
    elif 'プロポーザル' in method: score += 2
    if '共同体' in company or '共同企業体' in company or 'JV' in company or '・' in company: score += 1
    if amount_oku >= 10: score += 2
    elif amount_oku >= 1: score += 1
    if '災害' in project or '復旧' in project: score += 1  # 災害復旧は要確認案件
    return score


def main():
    print(f"=== 関東地整局R7 工事 ===")
    all_kouji = []
    for month in ['4月','5月','6月','7月','8月','9月','10月','11月','12月','1月','2月','3月']:
        path = f"{INPUT_DIR}/kouji/r7_{month}.xls"
        if not os.path.exists(path):
            print(f"  ✗ {month}: ファイルなし")
            continue
        records = parse_month_excel(path, '工事')
        print(f"  ✓ {month}: 行数={len(records)}")
        all_kouji.extend(records)
    
    print(f"\n=== 関東地整局R7 業務 ===")
    all_gyoumu = []
    for month in ['4月','5月','6月','7月','8月','9月','10月','11月','12月','1月','2月','3月']:
        path = f"{INPUT_DIR}/gyoumu/r7_{month}.xls"
        if not os.path.exists(path):
            print(f"  ✗ {month}: ファイルなし")
            continue
        records = parse_month_excel(path, '業務')
        print(f"  ✓ {month}: 行数={len(records)}")
        all_gyoumu.extend(records)
    
    print(f"\n=== 集約 ===")
    kouji_cases = aggregate_to_cases(all_kouji)
    gyoumu_cases = aggregate_to_cases(all_gyoumu)
    for c in kouji_cases: c['kind'] = '工事'
    for c in gyoumu_cases: c['kind'] = '業務'
    
    # スコア付与
    for c in kouji_cases + gyoumu_cases:
        c['score'] = calc_score(c)
    
    print(f"  工事案件: {len(kouji_cases)}件")
    print(f"  業務案件: {len(gyoumu_cases)}件")
    
    # 集計
    kouji_total = sum(c['amount_oku'] for c in kouji_cases)
    gyoumu_total = sum(c['amount_oku'] for c in gyoumu_cases)
    print(f"\n  工事合計: ¥{kouji_total:.2f}億")
    print(f"  業務合計: ¥{gyoumu_total:.2f}億")
    print(f"  総額: ¥{kouji_total + gyoumu_total:.2f}億")
    
    # 高Score
    high_score = [c for c in kouji_cases + gyoumu_cases if c['score'] >= 8]
    print(f"\n  高Score案件 (>=8): {len(high_score)}件")
    
    # TOP15
    print(f"\n=== 高額 TOP15 ===")
    all_cases = sorted(kouji_cases + gyoumu_cases, key=lambda x: -x['amount_oku'])
    for c in all_cases[:15]:
        print(f"  ¥{c['amount_oku']:>7.2f}億 [{c['rate_pct']:>5.1f}%] {c['method'][:15]:<15} {c['project'][:50]}")
        print(f"      {c['company'][:60]}")
    
    # 随意契約案件
    zui = [c for c in kouji_cases + gyoumu_cases if '随意契約' in (c.get('method') or '')]
    zui_total = sum(c['amount_oku'] for c in zui)
    print(f"\n=== 随意契約 ===")
    print(f"  件数: {len(zui)}件")
    print(f"  総額: ¥{zui_total:.2f}億")
    
    # JSON保存
    out = {
        'kouji': kouji_cases,
        'gyoumu': gyoumu_cases,
        'meta': {
            'bureau': '関東地方整備局',
            'year': 'R7',
            'kouji_count': len(kouji_cases),
            'gyoumu_count': len(gyoumu_cases),
            'kouji_total_oku': round(kouji_total, 2),
            'gyoumu_total_oku': round(gyoumu_total, 2),
            'total_oku': round(kouji_total + gyoumu_total, 2),
        }
    }
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n→ {OUTPUT_JSON} 保存完了")


if __name__ == "__main__":
    main()
