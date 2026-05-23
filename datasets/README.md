# Fiscal OSINT Japan — Open Datasets

公的資金の流れを、公開情報から検証する。

## License

All datasets in this directory are released under [CC0 1.0 Universal](LICENSE).
The data is dedicated to the public domain. You can use, modify, and redistribute
without asking permission.

Recommended (but not required) citation:

    Fiscal OSINT Japan — https://nana6fu.github.io/fiscal-osint-japan/

## Datasets

### Series 1: 対米資金フロー (US-bound public capital flows)

#### 1. jbic_5year.csv — JBIC受領計の5年推移
財政投融資特別会計から JBIC (国際協力銀行) への融資・出資の R5→R8 推移。

- 単位: 億円 (oku-yen / 1 oku = 100 million yen)
- 期間: 令和5年度 (FY2023) ～ 令和8年度 (FY2026)
- 出典: 財務省 財政投融資特別会計 決算・予算
- 関連記事: [80兆円対米投資の財源を、財政投融資特別会計から追跡する](../articles/80trillion.html)

#### 2. tokkai_zaitou_5year.csv — 財政投融資特別会計 歳出総額 5年推移
財政投融資特別会計の全勘定合計の歳出総額。

- 単位: 億円 (oku-yen)
- 期間: 令和5年度 (FY2023) ～ 令和8年度 (FY2026)
- 出典: 財務省 財政投融資特別会計 決算・予算
- 関連記事: [80兆円対米投資の財源を、財政投融資特別会計から追跡する](../articles/80trillion.html)

#### 3. companies_21.csv — 80兆円対米投資の21社（22企業）リスト
2025年10月28日 日米共同ファクトシートで公表された投資先企業リスト。

- 単位: 10億ドル (USD billion)
- 公表日: 2025年10月28日
- 出典:
  - 日本側仮訳: https://www.mof.go.jp/policy/international_policy/convention/dialogue/251028_fact_sheet_2.pdf
  - 米国側 White House Fact Sheet: https://www.whitehouse.gov/fact-sheets/2025/10/28195/
- 関連記事: [80兆円対米投資の財源を、財政投融資特別会計から追跡する](../articles/80trillion.html)

#### 4. special_account_defense_routes.csv — 防衛費財源 ¥1.84兆の3経路
令和5年度に外為特会・財投特会から一般会計へ繰り入れられた¥1.84兆円の3経路の内訳と根拠条文。

- 単位: 円 (yen, integer) と億円 (oku-yen)
- 対象年度: 令和5年度 (FY2023)
- 経路: ①外為特会 ¥1兆2,004億 / ②財投投資 ¥4,367億 / ③財投融資 ¥2,000億
- 出典: 財務省 防衛財源確保法案要綱、参議院常任委員会調査室レポート
- 関連記事: [防衛費財源の単発スキーム — 特会¥1.84兆を抜く特別法と、米海軍の2倍で買うトマホーク](../articles/special-account-defense.html)

#### 5. defense_budget_yoy.csv — 防衛関係費の年度推移 (R4→R7)
反撃能力保有決定（2022年12月）前後の防衛関係費の急拡大。

- 単位: 億円 (oku-yen) / 円 (yen, integer)
- 期間: 令和4年度 (FY2022) ～ 令和7年度 (FY2025)
- 注: SACO関係経費・米軍再編経費のうち地元負担軽減分を含む歳出額（防衛省の総額表記）
- 出典: 防衛白書 令和5年版・令和6年版、防衛省R7予算概要
- 関連記事: [防衛費財源の単発スキーム](../articles/special-account-defense.html)

#### 6. fms_tomahawk_price_comparison.csv — トマホーク日米豪3者価格比較
FMS（対外有償軍事援助）によるトマホーク調達価格の日本・米国・オーストラリア比較。

- 単位: ドル (USD) / 円 (yen)
- 注: 日本のトマホーク本体単価は政府が非公開とした（岸田首相が2023年2月衆院予算委で「明らかにしなかった」と赤旗報道）。本CSVの単価はDSCA承認時($23.5億)と最終契約(¥2,540億)の両ベースを並列表記している。
- 出典: 米海軍省R23予算書、米DSCA議会通知、米国務省対外軍事売却承認、東京新聞、しんぶん赤旗
- 関連記事: [防衛費財源の単発スキーム](../articles/special-account-defense.html)

#### 7. defense_funding_timeline.csv — 防衛費財源 意思決定タイムライン
2022年5月の日米首脳会談から2024年1月のFMS契約署名までの主要イベント12件。

- 期間: 2022-05-23 〜 2024-01-18
- 出典: 外務省、首相官邸、財務省、防衛省、衆参両院議事録
- 関連記事: [防衛費財源の単発スキーム](../articles/special-account-defense.html)

## Data Methodology

All data is collected from publicly available government documents (Japanese
Ministry of Finance, Cabinet Office, Ministry of Economy/Trade/Industry,
Ministry of Defense, Board of Audit of Japan, US White House, US DSCA,
US Navy Department) without any FOIA-style requests. Each data point is
traceable to a public URL listed in the respective CSV.

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
