# Fiscal OSINT Japan - Master Dataset

## 概要

This directory contains structured procurement data from Japanese central government ministries.

## ファイル

### `contracts_sample.jsonl` (公開, 100件)
Top contracts by amount across 3 ministries × 2 fiscal years.
**This is a sample for evaluation purposes.**

### `contracts.jsonl` (非公開, 2,785件+)
Full dataset covering all contracts. Not available via this repository.

For full dataset access (research / journalism / commercial), please contact:
- **SN0W8ALL LLC** (saitoukatsuhiko@me.com)

## Schema

Each line is a JSON object:

```json
{
  "id": "12-char-hash",
  "schema_version": "v0.2-pilot",
  "fiscal_year": "R6 | R7",
  "ministry": "財務省 | 厚労省 | デジタル庁",
  "bureau": "本省",
  "contract_type": "競争入札 | 随意契約 | etc",
  "contract_method_raw": "<原文>",
  "project_name": "...",
  "contracting_officer": "...",
  "signed_date": "YYYY-MM-DD",
  "contractor": {
    "name": "...",
    "address": "...",
    "corporate_number": "13-digit (一意キー)"
  },
  "scheduled_amount_jpy": int|null,
  "amount_jpy": int,
  "award_rate": float|null,
  "source": {
    "type": "mof_r7 | mhlw_r6 | etc",
    "file": "original_filename.xlsx",
    "sheet": "...",
    "row": int,
    "url": "primary source URL"
  }
}
```

## Coverage (as of 2026-05-22)

| Ministry | FY | Records |
|---|---|---:|
| 財務省 | R6 | 274 |
| 財務省 | R7 | 255 |
| 厚労省 | R6 | 1,049 |
| 厚労省 | R7 | 872 |
| デジタル庁 | R7 | 335 |
| **Total** | | **2,785** |

法人番号13桁充足率: 97.9%

## サンプル使用例

```bash
# サンプルダウンロード
curl https://nana6fu.github.io/fiscal-osint-japan/data/master/contracts_sample.jsonl -o sample.jsonl

# 任意の企業で検索
jq -c 'select(.contractor.name | contains("NEC"))' sample.jsonl

# 金額順上位
jq -s 'sort_by(-.amount_jpy) | .[:5] | .[] | {name: .contractor.name, amount: .amount_jpy, project: .project_name}' sample.jsonl
```

## ライセンス・引用

サンプルデータは CC BY 4.0 で公開。引用時は以下を明記：
> Fiscal OSINT Japan, SN0W8ALL LLC, https://nana6fu.github.io/fiscal-osint-japan/

## 連絡先

- Website: https://nana6fu.github.io/fiscal-osint-japan/
- Operator: SN0W8ALL LLC (Japan)
