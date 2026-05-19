# Fiscal OSINT Japan 引き継ぎ 2026/05/18 夜 → 次タイムライン

## ✅ 直近の達成（読むのはここだけでOK）

**2026/5/18 連続成果**:
1. 朝〜午前: 防衛省R7全国9局コンプリート（1,826件¥7,906億、v13）
2. 昼: ECI方式21件¥1,423億の全国スクープ完成、Xポスト投稿
3. 夕方: 国交省R6 関東地整局フルデータ抽出（2,361件¥3,316億）
4. 夜: **関東R6をサイト反映してv14リリース、git push済**

**サイト**: https://nana6fu.github.io/fiscal-osint-japan/

---

## 🎯 次のターゲット（ユーザー指定）

**2025年度（令和7年度）の総務省**を追加してR7サイトを充実化させたい。

### 背景
現在のR7（2025年度）タブは以下で構成：
- デジタル庁（GSS統合）: ¥1,599億
- 総務省（既存分・GSS統合関連）: ¥525億 ← もっと深掘りしたい
- 防衛省 地方防衛局9局: ¥7,906億

総務省は既に枠組みがあるので、R7の最新調達情報を追加してより詳細にする。

### 想定される作業
1. 総務省R7調達情報の取得元確認（CALSアーカイブ、入札公告サイト等）
2. データ抽出スクリプト作成
3. サイトへの反映（v15）

---

## 📂 重要ファイル

### Mac側
- マスターHTML: `/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html`
- ルート: `/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html`
- 関東R6 生データ: `/Volumes/SN0W8ALL/tokubetsu-kaikei/mlit_kanto_dl/kanto_r6_all.json`
- 関東R6 抽出スクリプト: `/Volumes/SN0W8ALL/tokubetsu-kaikei/mlit_kanto_dl/mlit_kanto_r6_extract_v3.py`

### GitHub
- リポジトリ: https://github.com/nana6fu/fiscal-osint-japan
- 公開URL: https://nana6fu.github.io/fiscal-osint-japan/

### Kagoya VPS（4層バックアップ用）
- IP: 133.18.167.199
- ユーザー: ubuntu（NOT root）
- 鍵: `/Volumes/SN0W8ALL/tokubetsu-kaikei/Fiscal OSINT Japan.key`
- バックアップ先: `~/fiscal_osint_backups/`

---

## ⚠ サイト構造の重要メモ

### MLIT_REGION_SUMMARY（2024年度=R6国交省タブ）の現在
```
[
  {region:"九州", cases:2656, amount_oku:2672.44},
  {region:"関東", cases:2361, amount_oku:3316.22}, ← 5/18追加
  {region:"東北", cases:2098, amount_oku:2459.65},
  {region:"近畿", cases:1901, amount_oku:2428.42},
  {region:"中部", cases:1933, amount_oku:2304.68},
  {region:"中国", cases:1554, amount_oku:1533.06},
  {region:"北陸", cases:382, amount_oku:387.76},
  {region:"四国", cases:211, amount_oku:124.82}
]
```

### サイトの設計原則（重要）
- 数字・グラフは出典URLにリンク
- 📄一次資料 と 🤖AI分析 を明確に分ける
- 各案件カードに出典リンク必須
- 個人名は必ず内閣官房R5公表PDFへの一次資料リンク併記

---

## 🚀 次回開始時の最初の発言例

```
昨日(5/18)の続き。
防衛省R7全国コンプリート(9局1,826件¥7,906億)と
国交省R6関東フルデータ(2,361件¥3,316億)反映完了済み。

今日は2025年度の総務省を深掘りしたい。
既存サイトに枠組みはあるけど、R7調達情報をもっと詳細に追加したい。
どこから取得するか相談から。
```

これで私が即把握して、メモリ#24・#23・#22を参照しつつ作業再開できる。

---

## 💡 次のタイムラインで参考にできるオプション

総務省R7深掘りの方向性：

**A. CALS（電子調達システム）からの取得**
- 総務省の入札結果がCALSに統合公開されている
- 既にデジタル庁データはCALS経由で取得済み（5/15）

**B. 各部局HPの個別取得**
- 統計局、消防庁、行政管理局など各部局の調達情報を個別取得
- 散らばっているが、防衛省9局取得パターンを流用可能

**C. GSS（政府共通プラットフォーム）統合関連の深掘り**
- NEC、富士通、NTTデータ、日立、SoftBankなど大手SIerの受注パターン
- 防衛省R7のECI独占構造の総務省版

**D. R6（2024年度）との比較**
- 既存サイトのR6総務省データと比較して構造変化を可視化

---

## 🔑 メモリ参照

引き継ぎ後、これらのメモリ番号を参照すると過去の文脈が分かる：
- #22: 防衛省R7コンプリート (5/18 v13)
- #23: 国交省R6関東フルデータ取得 (5/18 夕方)
- #24: 関東R6サイト反映 (5/18 夜 v14)
