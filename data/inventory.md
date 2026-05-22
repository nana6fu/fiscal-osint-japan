# Fiscal OSINT Japan データインベントリ

生成日時: 2026-05-22 08:40
ルート: `/Volumes/SN0W8ALL/tokubetsu-kaikei`

## サマリー

- **総ファイル数**: 2,248
- **総サイズ**: 361.4 MB

### 拡張子別

| 拡張子 | ファイル数 | サイズ (MB) |
|---|---:|---:|
| `.pdf` | 1,330 | 182.3 |
| `.xlsx` | 394 | 15.0 |
| `.xls` | 203 | 25.1 |
| `.html` | 160 | 119.3 |
| `.json` | 80 | 18.2 |
| `.txt` | 51 | 0.2 |
| `.csv` | 30 | 1.3 |

### ディレクトリ別（上位30）

| ディレクトリ | ファイル数 | サイズ (MB) |
|---|---:|---:|
| `data/defense/chushi/r05/gyoumu` | 224 | 7.6 |
| `nkanto_dl/n_kanto_r7_pdfs/業務` | 144 | 72.1 |
| `kyushu_dl/kyushu_r7_pdfs/業務_調達部` | 141 | 7.2 |
| `nkanto_dl/n_kanto_r7_pdfs/工事` | 110 | 22.4 |
| `data/mlit_r5_confirmed` | 99 | 14.5 |
| `data/defense/chushi/r05/kouji` | 97 | 4.7 |
| `data/defense/s-kanto/r05/gyoumu` | 97 | 8.4 |
| `data/defense/s-kanto/r05/kouji` | 87 | 6.5 |
| `data/defense/tohoku/r05/kouji` | 84 | 10.1 |
| `kyushu_dl/kyushu_r7_pdfs/工事_調達部` | 77 | 4.2 |
| `data/defense/kinki-chubu/r05/kouji` | 74 | 8.1 |
| `data/defense/kinki-chubu/r05/gyoumu` | 74 | 7.7 |
| `入札エクセル/令和6年度/中国` | 48 | 1.5 |
| `入札エクセル/令和6年度/中部` | 48 | 3.7 |
| `入札エクセル/令和6年度/九州` | 48 | 1.9 |
| `入札エクセル/令和6年度/四国` | 48 | 2.2 |
| `入札エクセル/令和6年度/東北` | 48 | 1.7 |
| `入札エクセル/令和6年度/近畿` | 48 | 2.6 |
| `data/mof_r6` | 48 | 0.9 |
| `data/mof_r7` | 45 | 0.8 |
| `data/mlit_r5_confirmed/kanto_r5_kouji_pdfs` | 45 | 6.5 |
| `backups` | 44 | 97.4 |
| `入札エクセル/令和7年度/関東` | 44 | 4.7 |
| `data/mlit_r5/raw/chubu` | 24 | 3.1 |
| `.venv_mod/lib/python3.13/site-packages/numpy/_core/tests/data` | 21 | 1.1 |
| `data/digital_r7` | 20 | 0.6 |
| `data/mhlw_r7` | 19 | 6.4 |
| `data/mhlw_r6` | 19 | 6.9 |
| `kyushu_dl/kyushu_r7_pdfs/工事_管理部` | 18 | 0.6 |
| `kyushu_dl/kyushu_r7_pdfs/業務_企画部管理部` | 16 | 0.7 |

## 既知データソース（メモリから整理）

| データソース | 場所 | スコープ | 一次資料 |
|---|---|---|---|
| **厚労省 R6 本省** | `data/mhlw_r6/` | 一般会計4 Excel + 各勘定PDF 15 | https://www.mhlw.go.jp/sinsei/chotatu/zuii/24honsyo.html |
| **財務省 R6 本省** | `data/mof_r6/` | 全12ヶ月×4様式=48ファイル | https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm |
| **Phase 2 OB×受注** | `data/stage2/phase2_obs_complete.json` | 17社29人 + R7 4省庁内訳 | — |
| **R6 RV集計** | `data/stage2/mhlw_r6_targets.json + mof_r6_targets.json` | 主要IT 14社R6集計 | — |
| **内閣官房 OB公表 R5** | `archives/cabinet_obs/r06/siryou3-1.xlsx` | 1,742人 / うち営利法人642人 | https://www.cas.go.jp/jp/gaiyou/jimu/jinjikyoku/106-25-2/r06/kouhyou_0924.html |
| **防衛省9局 (R5/R6/R7)** | `src/frontend/index.html 内 MOD_*_ALL_CASES (要分離)` | 9局×3年=27パッケージ中22個 (5個欠) | 各地方防衛局HP |
| **MLIT 8整備局 R6** | `src/frontend/index.html 内 (要分離)` | 8局R6全件 (R604除外) | 各地方整備局HP |
| **入札Excel原典** | `入札エクセル/` | 防衛省・MLITの一次Excel | — |
| **政治献金 (Kyoto/Kokumin)** | `(場所要確認)` | Kyoto 128 PDFs / Kokumin 20 | 京都府選管 / 国民政治協会 |

## 要調査ポイント（次の確認事項）


- [ ] 防衛省9局・MLIT 8局の **生データ Excel** はどこにある？（index.html 内変数からの逆抽出が必要か）
- [ ] 政治献金関連の **128 PDFs** はどのディレクトリか
- [ ] **総務省R7・デジタル庁R7** の生データは存在するか（Phase 2 で集計済みだが原典は？）
- [ ] **内閣官房OB公表 R4・R3** 等の過年度データはあるか
- [ ] **特別会計予算書PDF** （財務省公表）の取得状況

## 次のステップ（API化への道筋）


### Phase 1: 共通スキーマ設計（今日中）
全契約データを以下のフィールドで統一:

```yaml
contract:
  fiscal_year: R5 | R6 | R7
  ministry: デジタル庁 | 総務省 | 厚労省 | 財務省 | 防衛省 | 国交省 | ...
  bureau: 本省 | 北海道防衛局 | 関東地方整備局 | ...
  contract_type: 一般競争入札 | 随意契約(ECI) | ...
  contractor:
    name: 株式会社○○
    corporate_number: 13桁  # 一意キー
    address: 東京都...
  project_name: ○○システム運用保守業務
  amount_jpy: 1234567890
  scheduled_amount_jpy: 1234567890  # 予定価格
  award_rate: 0.95
  signed_date: 2024-04-01
  source:
    url: https://...
    document: tekiseika202404-3.xlsx
    row_id: 47  # 検証可能性
```

### Phase 2: master.jsonl 生成
- 全データを JSON Lines 形式で統合 → `data/master/contracts.jsonl`
- 推定 7,000〜10,000件 / 5〜15 MB
- 1行1契約、`jq` で即検索可能

### Phase 3: OB データの統合
- OB公表データを `data/master/officials.jsonl` として別ファイル
- フィールド: 氏名・元職・退職日・再就職先(法人番号)・役職
- contracts.jsonl の corporate_number で JOIN 可能

### Phase 4: 検索インターフェース
- CLI: `jq 'select(.contractor.corporate_number == "...")' contracts.jsonl`
- Web: GitHub Pages に検索ページ追加（任意の企業/省庁/年度で検索）
- API: 将来的に Cloudflare Workers でB2B課金

### Phase 5: 公開
- `data/master/` を GitHub Pages で `/api/` として無料公開
- ユーザーが好きに検索・分析できる
- ショーケース(現状サイト)はあくまで Saito さんが選んだ発見のみ
