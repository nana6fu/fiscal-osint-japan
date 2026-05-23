# Fiscal OSINT Japan — Open Datasets

公的資金の流れを、公開情報から検証する。

## License

All datasets in this directory are released under [CC0 1.0 Universal](LICENSE).
The data is dedicated to the public domain. You can use, modify, and redistribute
without asking permission.

Recommended (but not required) citation:

    Fiscal OSINT Japan — https://nana6fu.github.io/fiscal-osint-japan/

## Datasets

### 1. jbic_5year.csv — JBIC受領計の5年推移
財政投融資特別会計から JBIC (国際協力銀行) への融資・出資の R5→R8 推移。

- 単位: 億円 (oku-yen / 1 oku = 100 million yen)
- 期間: 令和5年度 (FY2023) ～ 令和8年度 (FY2026)
- 出典: 財務省 財政投融資特別会計 決算・予算
- 関連記事: [80兆円対米投資の財源を、財政投融資特別会計から追跡する](../articles/80trillion.html)

### 2. tokkai_zaitou_5year.csv — 財政投融資特別会計 歳出総額 5年推移
財政投融資特別会計の全勘定合計の歳出総額。

- 単位: 億円 (oku-yen)
- 期間: 令和5年度 (FY2023) ～ 令和8年度 (FY2026)
- 出典: 財務省 財政投融資特別会計 決算・予算

### 3. companies_21.csv — 80兆円対米投資の21社（22企業）リスト
2025年10月28日 日米共同ファクトシートで公表された投資先企業リスト。

- 単位: 10億ドル (USD billion)
- 公表日: 2025年10月28日
- 出典:
  - 日本側仮訳: https://www.mof.go.jp/policy/international_policy/convention/dialogue/251028_fact_sheet_2.pdf
  - 米国側 White House Fact Sheet: https://www.whitehouse.gov/fact-sheets/2025/10/28195/

## Data Methodology

All data is collected from publicly available government documents (Japanese
Ministry of Finance, Cabinet Office, Ministry of Economy/Trade/Industry,
US White House) without any FOIA-style requests. Each data point is traceable
to a public URL listed in the respective CSV.

AI tools (Claude, GPT, DeepSeek, Gemini) are used for:
- Cross-checking numbers against original PDFs
- Extracting structured data from prose documents
- Verifying internal consistency (e.g., column sums)

AI-detected errors are documented in the related article update history.

## How to Cite

Academic / journalistic citation:

    Fiscal OSINT Japan. (2026). [Dataset Name]. CC0 1.0.
    Retrieved from https://nana6fu.github.io/fiscal-osint-japan/datasets/

## Contact

X: @FiscalOSINT_JP - https://x.com/FiscalOSINT_JP
