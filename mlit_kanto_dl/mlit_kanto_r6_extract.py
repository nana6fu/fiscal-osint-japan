#!/usr/bin/env python3
"""
関東地方整備局 R6統合Excel → JSON抽出 (v2)

突破口: 「備考」列(col18) の「落札」マークで落札者を特定
これで一般競争入札も含めて全案件カバー可能

入力:
  r6_full/kanto_r6_kouji.xls  (1.7MB, 6111行)
  r6_full/kanto_r6_gyoumu.xls (1.5MB, 4462行)

出力: kanto_r6_all.json
"""
import os
import json
import pandas as pd
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


def parse_excel(path, kind):
    """落札者だけを抽出"""
    df = pd.read_excel(path, engine='xlrd', header=None)
    
    # ヘッダー行検出（「部局名」を含む行）
    header_row = None
    for i in range(min(15, len(df))):
        row_str = ' '.join(str(c) for c in df.iloc[i].values if pd.notna(c))
        if '部局名' in row_str:
            header_row = i
            break
    if header_row is None:
        print(f"  ✗ {path}: ヘッダー行検出失敗")
        return []
    
    data_start = header_row + 3  # ヘッダー+サブヘッダー2行
    
    records = []
    skip_count = 0
    
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        if all(pd.isna(v) for v in row.values): continue
        
        bureau = str(row[0]).strip() if pd.notna(row[0]) else ''
        project = str(row[1]).strip() if pd.notna(row[1]) else ''
        if not project or project == 'nan': continue
        if '関東地方整備局' not in bureau and '事務所' not in bureau and 'NaN' not in bureau:
            continue
        
        # 落札者判定: 「備考=落札」または「見積金額あり」
        memo = str(row[18]).strip() if len(row) > 18 and pd.notna(row[18]) else ''
        contract_amount_col17 = to_int(row[17]) if len(row) > 17 else None
        
        is_winner_by_memo = '落札' in memo
        is_winner_by_zui = contract_amount_col17 is not None  # 随意契約は見積金額に値あり
        
        if not is_winner_by_memo and not is_winner_by_zui:
            skip_count += 1
            continue
        
        # 契約金額決定
        # 優先順位: 見積金額(col17) > 3回目金額(col15) > 2回目金額(col13) > 1回目金額(col11)
        final_amount = None
        if contract_amount_col17:
            final_amount = contract_amount_col17
        else:
            for col in [15, 13, 11]:
                if len(row) > col:
                    v = to_int(row[col])
                    if v: 
                        final_amount = v
                        break
        
        if not final_amount: continue
        
        predicted = to_int(row[8]) if len(row) > 8 else None
        rate_pct = round(final_amount / predicted * 100, 2) if predicted else 0
        
        # 業者名
        company = str(row[7]).strip() if pd.notna(row[7]) else ''
        if not company or company == 'nan': continue
        
        # 入札日・契約日
        bid_date = str(row[2])[:10] if pd.notna(row[2]) else ''
        contract_date = str(row[3])[:10] if pd.notna(row[3]) else ''
        
        # 入札方式・工種・総合評価
        method = str(row[5]).strip() if pd.notna(row[5]) else ''
        type_kind = str(row[4]).strip() if pd.notna(row[4]) else ''
        is_sougou = str(row[6]).strip() if pd.notna(row[6]) else ''
        
        records.append({
            'kind': kind,
            'bureau': bureau,
            'project': project,
            'company': company,
            'method': method,
            'type_kind': type_kind,
            'is_sougou': is_sougou,
            'bid_date': bid_date,
            'contract_date': contract_date,
            'predicted_excl': predicted,
            'contract_amount_excl': final_amount,
            'amount_oku': round(final_amount / 1e8, 4),
            'planned_oku': round(predicted / 1e8, 4) if predicted else 0,
            'rate_pct': rate_pct,
            'memo': memo,
            'win_by': 'memo' if is_winner_by_memo else 'zui',
        })
    
    print(f"  {path}: 落札者{len(records)}件 / 入札参加スキップ{skip_count}件")
    return records


def calc_score(rec):
    """R6サイト方式でスコアリング"""
    score = 0
    reasons = []
    
    rate = rec.get('rate_pct') or 0
    method = rec.get('method') or ''
    company = rec.get('company') or ''
    project = rec.get('project') or ''
    amount_oku = rec.get('amount_oku') or 0
    predicted_oku = rec.get('planned_oku') or 0
    
    # 落札率
    if rate >= 99:
        score += 3
        reasons.append('落札率99%以上')
    elif rate >= 95:
        score += 1
        reasons.append('落札率95%以上')
    
    # 予定価格近接（差100万円以内）
    diff_oku = predicted_oku - amount_oku
    if 0 <= diff_oku * 1e8 <= 1_000_000:
        score += 2
        reasons.append('予定価格との差100万円以内')
    elif 0 <= diff_oku * 1e8 <= 10_000_000:
        score += 1
        reasons.append('予定価格との差1000万円以内')
    
    # 入札方式
    if '随意契約' in method:
        score += 3
        reasons.append('随意契約')
    elif 'プロポーザル' in method:
        score += 2
        reasons.append('プロポーザル方式')
    
    # 金額規模
    if amount_oku >= 10:
        score += 2
        reasons.append('10億円以上')
    elif amount_oku >= 1:
        score += 1
        reasons.append('1億円以上')
    
    # 建設協会・弘済会系
    if any(kw in company for kw in ['建設協会', '弘済会', '地域づくり協会', 'クリエイト協会']):
        score += 3
        reasons.append('建設協会・弘済会系')
    
    # 発注者支援系業務
    if any(kw in project for kw in ['発注者支援', '事業監理', '監督補助', '事業促進']):
        score += 2
        reasons.append('発注者支援系業務')
    
    # 災害復旧
    if any(kw in project for kw in ['災害', '復旧']):
        reasons.append('災害復旧')
    
    return score, ' / '.join(reasons)


def level_from_score(score):
    if score >= 10: return '要確認度 高'
    if score >= 7: return '要確認度 中'
    if score >= 5: return '要確認度 低'
    return '通常'


def clean_company(c):
    import re
    return re.sub(r'(株式会社|有限会社|（株）|（有）|\(株\)|\(有\)|\s|　)', '', c or '')


def main():
    print("=" * 70)
    print("関東地方整備局 R6統合Excel → JSON抽出")
    print("=" * 70)
    
    if not os.path.exists(INPUT_KOUJI):
        print(f"ERROR: {INPUT_KOUJI} がない")
        return
    if not os.path.exists(INPUT_GYOUMU):
        print(f"ERROR: {INPUT_GYOUMU} がない")
        return
    
    print("\n=== 抽出 ===")
    kouji = parse_excel(INPUT_KOUJI, '工事')
    gyoumu = parse_excel(INPUT_GYOUMU, '業務')
    
    # スコア・level付与
    for r in kouji + gyoumu:
        score, reason = calc_score(r)
        r['score'] = score
        r['reason'] = reason
        r['level'] = level_from_score(score)
        r['region'] = '関東'
        r['company_clean'] = clean_company(r['company'])
    
    # 集計
    kouji_total = sum(r['amount_oku'] for r in kouji)
    gyoumu_total = sum(r['amount_oku'] for r in gyoumu)
    
    print(f"\n=== 集計 ===")
    print(f"  工事: {len(kouji)}件 ¥{kouji_total:.2f}億")
    print(f"  業務: {len(gyoumu)}件 ¥{gyoumu_total:.2f}億")
    print(f"  合計: {len(kouji)+len(gyoumu)}件 ¥{kouji_total+gyoumu_total:.2f}億")
    
    # 要確認度別
    all_records = kouji + gyoumu
    high = sum(1 for r in all_records if r['score'] >= 10)
    mid = sum(1 for r in all_records if 7 <= r['score'] < 10)
    low = sum(1 for r in all_records if 5 <= r['score'] < 7)
    
    print(f"\n=== 要確認度別 ===")
    print(f"  高: {high}件")
    print(f"  中: {mid}件")
    print(f"  低: {low}件")
    
    # TOP15表示
    print(f"\n=== 高Score TOP15 ===")
    for r in sorted(all_records, key=lambda x: -x['score'])[:15]:
        print(f"  S={r['score']:>2} ¥{r['amount_oku']:>7.2f}億 [{r['rate_pct']:>5.1f}%] {r['method'][:12]:<12} {r['project'][:40]}")
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
    sorted_companies = sorted(company_agg.items(), key=lambda x: -x[1]['amount_oku'])[:20]
    for name, data in sorted_companies:
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
    
    # JSON保存
    output = {
        'meta': {
            'bureau': '関東地方整備局',
            'year': 'R6',
            'kouji_count': len(kouji),
            'gyoumu_count': len(gyoumu),
            'total_count': len(kouji) + len(gyoumu),
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
