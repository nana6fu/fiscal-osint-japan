#!/usr/bin/env python3
"""
関東地方整備局 R6統合Excel → JSON抽出 v3

工事Excel: 19列構造 (備考=col18)
業務Excel: 22列構造 (備考=col21)

両方の構造に対応。「落札」マークで全案件捕捉。
"""
import os
import json
import pandas as pd
import re
from collections import defaultdict

INPUT_KOUJI = "r6_full/kanto_r6_kouji.xls"
INPUT_GYOUMU = "r6_full/kanto_r6_gyoumu.xls"
OUTPUT_JSON = "kanto_r6_all.json"


def to_int(v):
    if pd.isna(v): return None
    if isinstance(v, str):
        v = v.replace(',','').strip()
        if v in ('-', '', '－'): return None
        try: return int(float(v))
        except: return None
    try: return int(v)
    except: return None


def parse_excel(path, kind, col_map):
    """落札者だけを抽出する汎用関数
    col_map: 列マッピング
      - 'memo': 備考列 (落札マーク)
      - 'contract_amount': 見積金額列
      - 'amount_1', 'amount_2', 'amount_3': 1/2/3回目入札金額列
    """
    df = pd.read_excel(path, engine='xlrd', header=None)
    print(f"\n--- {path} ---")
    print(f"  shape: {df.shape}")
    
    # ヘッダー行検出
    header_row = None
    for i in range(min(15, len(df))):
        row_str = ' '.join(str(c) for c in df.iloc[i].values if pd.notna(c))
        if '部局名' in row_str:
            header_row = i
            break
    if header_row is None:
        print(f"  ✗ ヘッダー行検出失敗")
        return []
    
    data_start = header_row + 3
    
    records = []
    skip_count = 0
    
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        if all(pd.isna(v) for v in row.values): continue
        
        bureau = str(row[0]).strip() if pd.notna(row[0]) else ''
        project = str(row[1]).strip() if pd.notna(row[1]) else ''
        if not project or project == 'nan': continue
        
        # 「落札」マーク / 「決定」マーク
        memo = str(row[col_map['memo']]).strip() if len(row) > col_map['memo'] and pd.notna(row[col_map['memo']]) else ''
        contract_amount_col = to_int(row[col_map['contract_amount']]) if len(row) > col_map['contract_amount'] else None
        
        is_winner_by_memo = ('落札' in memo) or ('決定' in memo)
        is_winner_by_zui = contract_amount_col is not None
        
        if not is_winner_by_memo and not is_winner_by_zui:
            skip_count += 1
            continue
        
        # 契約金額決定
        final_amount = None
        if contract_amount_col:
            final_amount = contract_amount_col
        else:
            for col_key in ['amount_3', 'amount_2', 'amount_1']:
                col = col_map.get(col_key)
                if col is None: continue
                if len(row) > col:
                    v = to_int(row[col])
                    if v: 
                        final_amount = v
                        break
        
        if not final_amount: continue
        
        predicted = to_int(row[8]) if len(row) > 8 else None
        rate_pct = round(final_amount / predicted * 100, 2) if predicted else 0
        
        company = str(row[7]).strip() if pd.notna(row[7]) else ''
        if not company or company == 'nan': continue
        
        records.append({
            'kind': kind,
            'bureau': bureau,
            'project': project,
            'company': company,
            'method': str(row[5]).strip() if pd.notna(row[5]) else '',
            'type_kind': str(row[4]).strip() if pd.notna(row[4]) else '',
            'is_sougou': str(row[6]).strip() if pd.notna(row[6]) else '',
            'bid_date': str(row[2])[:10] if pd.notna(row[2]) else '',
            'contract_date': str(row[3])[:10] if pd.notna(row[3]) else '',
            'predicted_excl': predicted,
            'contract_amount_excl': final_amount,
            'amount_oku': round(final_amount / 1e8, 4),
            'planned_oku': round(predicted / 1e8, 4) if predicted else 0,
            'rate_pct': rate_pct,
            'memo': memo,
            'win_by': 'memo' if is_winner_by_memo else 'zui',
        })
    
    print(f"  落札者: {len(records)}件, スキップ: {skip_count}件")
    return records


def calc_score(rec):
    score = 0
    reasons = []
    
    rate = rec.get('rate_pct') or 0
    method = rec.get('method') or ''
    company = rec.get('company') or ''
    project = rec.get('project') or ''
    amount_oku = rec.get('amount_oku') or 0
    predicted_oku = rec.get('planned_oku') or 0
    
    if rate >= 99:
        score += 3; reasons.append('落札率99%以上')
    elif rate >= 95:
        score += 1; reasons.append('落札率95%以上')
    
    diff_yen = (predicted_oku - amount_oku) * 1e8
    if 0 <= diff_yen <= 1_000_000:
        score += 2; reasons.append('予定価格との差100万円以内')
    elif 0 <= diff_yen <= 10_000_000:
        score += 1; reasons.append('予定価格との差1000万円以内')
    
    if '随意契約' in method:
        score += 3; reasons.append('随意契約')
    elif 'プロポーザル' in method:
        score += 2; reasons.append('プロポーザル方式')
    
    if amount_oku >= 10:
        score += 2; reasons.append('10億円以上')
    elif amount_oku >= 1:
        score += 1; reasons.append('1億円以上')
    
    if any(kw in company for kw in ['建設協会', '弘済会', '地域づくり協会', 'クリエイト協会']):
        score += 3; reasons.append('建設協会・弘済会系')
    
    if any(kw in project for kw in ['発注者支援', '事業監理', '監督補助', '事業促進']):
        score += 2; reasons.append('発注者支援系業務')
    
    if any(kw in project for kw in ['災害', '復旧']):
        reasons.append('災害復旧')
    
    return score, ' / '.join(reasons)


def level_from_score(score):
    if score >= 10: return '要確認度 高'
    if score >= 7: return '要確認度 中'
    if score >= 5: return '要確認度 低'
    return '通常'


def clean_company(c):
    return re.sub(r'(株式会社|有限会社|（株）|（有）|\(株\)|\(有\)|\s|　)', '', c or '')


def main():
    print("=" * 70)
    print("関東地方整備局 R6統合Excel → JSON抽出 v3")
    print("=" * 70)
    
    # 工事Excel (19列)
    kouji_col_map = {
        'memo': 18,
        'contract_amount': 17,
        'amount_1': 11, 'amount_2': 13, 'amount_3': 15,
    }
    
    # 業務Excel (22列)
    gyoumu_col_map = {
        'memo': 21,
        'contract_amount': 20,
        'amount_1': 11, 'amount_2': 14, 'amount_3': 17,
    }
    
    kouji = parse_excel(INPUT_KOUJI, '工事', kouji_col_map)
    gyoumu = parse_excel(INPUT_GYOUMU, '業務', gyoumu_col_map)
    
    # スコア・level付与
    for r in kouji + gyoumu:
        score, reason = calc_score(r)
        r['score'] = score
        r['reason'] = reason
        r['level'] = level_from_score(score)
        r['region'] = '関東'
        r['company_clean'] = clean_company(r['company'])
    
    all_records = kouji + gyoumu
    kouji_total = sum(r['amount_oku'] for r in kouji)
    gyoumu_total = sum(r['amount_oku'] for r in gyoumu)
    
    print(f"\n{'=' * 70}")
    print(f"=== 関東R6 集計 ===")
    print(f"{'=' * 70}")
    print(f"  工事: {len(kouji)}件 ¥{kouji_total:.2f}億")
    print(f"  業務: {len(gyoumu)}件 ¥{gyoumu_total:.2f}億")
    print(f"  合計: {len(all_records)}件 ¥{kouji_total + gyoumu_total:.2f}億")
    
    # 要確認度別
    high = sum(1 for r in all_records if r['score'] >= 10)
    mid = sum(1 for r in all_records if 7 <= r['score'] < 10)
    low = sum(1 for r in all_records if 5 <= r['score'] < 7)
    
    print(f"\n=== 要確認度別 ===")
    print(f"  高: {high}件")
    print(f"  中: {mid}件")
    print(f"  低: {low}件")
    
    print(f"\n=== 高Score TOP20 ===")
    for r in sorted(all_records, key=lambda x: -x['score'])[:20]:
        print(f"  S={r['score']:>2} ¥{r['amount_oku']:>7.2f}億 [{r['rate_pct']:>5.1f}%] {r['method'][:14]:<14} {r['kind']} {r['project'][:35]}")
        print(f"      {r['company'][:60]}")
        print(f"      reason: {r['reason']}")
    
    # 受注上位企業
    company_agg = defaultdict(lambda: {'cases': 0, 'amount_oku': 0, 'projects': []})
    for r in all_records:
        cname = r['company_clean'] or r['company']
        company_agg[cname]['cases'] += 1
        company_agg[cname]['amount_oku'] += r['amount_oku']
        company_agg[cname]['projects'].append(r['project'][:30])
    
    print(f"\n=== 受注上位企業 TOP20 ===")
    for name, data in sorted(company_agg.items(), key=lambda x: -x[1]['amount_oku'])[:20]:
        print(f"  {data['cases']:>4}件 ¥{data['amount_oku']:>9.2f}億 {name[:50]}")
    
    # 入札方式別
    print(f"\n=== 入札方式別 ===")
    method_agg = defaultdict(lambda: {'cases': 0, 'amount_oku': 0})
    for r in all_records:
        m = r['method']
        method_agg[m]['cases'] += 1
        method_agg[m]['amount_oku'] += r['amount_oku']
    for m, data in sorted(method_agg.items(), key=lambda x: -x[1]['amount_oku']):
        print(f"  {data['cases']:>4}件 ¥{data['amount_oku']:>9.2f}億 {m[:40]}")
    
    # 建設協会・弘済会系
    print(f"\n=== 建設協会・弘済会系・地域づくり協会 ===")
    associations = [r for r in all_records if any(kw in r['company'] for kw in ['建設協会', '弘済会', '地域づくり協会', 'クリエイト協会'])]
    asso_total = sum(r['amount_oku'] for r in associations)
    print(f"  {len(associations)}件 ¥{asso_total:.2f}億")
    for r in sorted(associations, key=lambda x: -x['amount_oku'])[:10]:
        print(f"    ¥{r['amount_oku']:>5.2f}億 [{r['rate_pct']:>5.1f}%] {r['company'][:30]:<30} {r['project'][:40]}")
    
    # 業務全体の落札率分布
    if gyoumu:
        gyoumu_rates = [r['rate_pct'] for r in gyoumu if r['rate_pct']]
        if gyoumu_rates:
            avg_rate = sum(gyoumu_rates) / len(gyoumu_rates)
            print(f"\n=== 業務の落札率分布 ===")
            print(f"  平均落札率: {avg_rate:.2f}%")
            high_rate_gyoumu = [r for r in gyoumu if r['rate_pct'] >= 99]
            print(f"  落札率99%以上: {len(high_rate_gyoumu)}件 ¥{sum(r['amount_oku'] for r in high_rate_gyoumu):.2f}億")
    
    # JSON保存
    output = {
        'meta': {
            'bureau': '関東地方整備局',
            'year': 'R6',
            'kouji_count': len(kouji),
            'gyoumu_count': len(gyoumu),
            'total_count': len(all_records),
            'kouji_amount_oku': round(kouji_total, 2),
            'gyoumu_amount_oku': round(gyoumu_total, 2),
            'total_amount_oku': round(kouji_total + gyoumu_total, 2),
            'high_score_count': high,
            'mid_score_count': mid,
        },
        'all_cases': all_records,
    }
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n→ {OUTPUT_JSON} 保存完了")


if __name__ == "__main__":
    main()
