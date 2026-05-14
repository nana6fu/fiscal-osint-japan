# Fiscal OSINT Japan — R7 デジタル庁 実装セッションログ

- **日付**: 2026-05-14
- **プロジェクト**: tokubetsu-kaikei
- **マスター**: `/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html`
- **ルート**: `/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html`
- **リポジトリ**: github.com/nana6fu/fiscal-osint-japan

---

## 1. 完成項目

### データ収集（R7デジタル庁）
- データソース: https://www.digital.go.jp/procurement/proper-public-procurement
- 公表ファイル: 19本（2025年4-12月分・競争入札/随意契約/公共工事）
- ローカル保存: `data/digital_r7/digital_r7_all_contracts.json`
- 総契約数: 343件
- 総契約額: ¥159,943,850,302（約¥1,599億）

### 主要発見
| 項目 | 数値 | 構造的問題 |
|---|---|---|
| GSS集中 | ¥979億（全契約61.2%） | 霞が関全省庁の統合移行年 |
| NEC一強 | ¥553億（2位NTTデータの3.3倍） | GSS関連だけで¥503億独占 |
| 落札率100% | 22件（競争入札の20.2%） | PwC¥3.85億・NTTデータ¥1.55億等 |
| 応札者数 | 全343件で空欄 | 他省庁は記載、デジタル庁のみ非開示 |
| 再就職役員数 | 全343件で空欄 | 同上 |
| 随意契約97% | 「契約の性質又は目的が競争を許さない」根拠 | 形骸化 |
| 初の公共工事 | マイスター社・大阪国際空港¥2,535万 | R7/12月、 物品役務契約のみだったデジタル庁が初発注 |
| アクセンチュア | R6で4ヶ月指名停止→R7で6件・¥39.7億復帰 | 指名停止は新規契約のみ効力 |
| NTT商号変更 | NTTコミュニケーションズ→NTTドコモビジネス | 2025年7月吸収合併・両表記混在 |

### ダッシュボード実装
- `MINISTRIES_2025` 配列追加（デジタル庁R7エントリ1件・R6と完全同形スキーマ）
- 構成: `primary_facts` 8件 / `houjin` 18社 / `accounts` 4枚
- 年度切替ハンドラに `2025` 分岐追加、 上部サマリーR7数値に更新
- `appendModMinistryItem()` にR7ガード追加（防衛省カードをR7で非表示・既存min-modは自動削除）
- `selectMinistry()` のR6/2006ハードコードラベルを `m.id==="daj"` 条件で分岐
- `renderMinistries()` 左サイドバー合計のデジタル庁R7用override（3,871→1,599）
- `daj_r7_proc` を SOURCES に登録（一次資料リンク用）

### 解決した重大バグ（再発防止メモ）
1. **防衛省カードが R7 にも出る** → `appendModMinistryItem` に `year==='2025'` ガード追加で解消
2. **クリック反応なし・中央パネルが国交省2006データで固定** → `daj_r7_proc` が SOURCES 未登録のため `selectMinistry` が TypeError で停止していた。 SOURCES登録で解消
3. **企業表が「令和6年度・関東東北...地整局」表示** → `m.id==="daj"` 条件分岐で R7 デジタル庁用ラベルに切替
4. **サイドバー合計が3,871億（accounts のoverlap合算）** → デジタル庁R7のとき1,599固定override
5. **中央パネル省庁ヘッダー総計も3,871固定** → 同じく1,599固定override（L2082 ministry-subtitle）

---

## 2. 残作業

### 短期（即時）
- [ ] git commit & push（R7デジタル庁完了マイルストーン）
- [ ] X投稿（130字版3案作成済み: 不透明性フック / NEC独占フック / 総合パンチライン）
- [ ] GitHub Pages デプロイ後の動作確認

### 中期
- [ ] R7他省庁追加（厚労省・国交省・財務省・総務省）
  - 仕組みは確立済み、 `MINISTRIES_2025` 配列にエントリ追加するだけで R6 と同じデザインで描画される
- [ ] 2026/7 R7決算データ確定後の本集計更新（特に上部サマリー「歳出純計額」「特別会計数」）
- [ ] Selenium による政治献金照合（前回引き継ぎから持ち越し）
- [ ] 8地整局への情報公開請求書（前回引き継ぎから持ち越し）

### 長期
- [ ] R7他省庁データが揃ったら「デジタル庁だけが異常に不透明」を比較表で定量化
- [ ] 記者向け OSINT メモを公式レポート化
- [ ] Ishii Tanya 等の透明性論者へのリーチ戦略

---

## 3. 技術メモ・鉄則

### Pythonヒアドキュメントパッチ方式（今日の学び）
1. **既存アーキテクチャを必ず `grep -n` で確認してから着手** — 関数名・データ構造の場所を特定
2. **新規 src_key は必ず SOURCES に登録** — 未登録だと `selectMinistry` が TypeError で停止し、 中央パネルが前ロード時の表示で固まる
3. **MINISTRIES_* 追加時は両方更新** — change handler の if/else分岐 と 初期化IIFE の両方に分岐を入れる
4. **年度共通の付加処理関数（appendModMinistryItem等）にも年度ガード** — MINISTRIES配列とは別機構で動く独立関数を見落とさない
5. **selectMinistry 内のハードコードラベルは ministry id 条件で分岐** — R6時代の「令和6年度・地整局」固定文言が多数残っているため
6. **zsh の for 構文に注意** — `for f in glob 2>/dev/null; do` は parse エラー。 redirect は loop 全体に置くか、 Python等で書く
7. **bash heredoc 内に Python のトリプルクォート + Markdownのトリプルバッククォートを同時に入れない** — heredoc> プロンプトが終わらなくなる。 ログ等は別ファイルに保存してから読み込ませる

### 構造的論点（記事化候補）
- デジタル庁の設立趣旨（2021/9）: 「ベンダーロックイン解消」「縦割り行政打破」「透明性向上」
- R6→R7の実態: 旧来型ロックインから新型ロックイン（GSS統合の名目でNECに集中）へ転換
- 監視機能の機能不全: デジタル庁自身の入札等監視委員会が「変更契約の連発で対応事業者が一者に確定するおそれ」と公式警告 → 改善されないまま翌年も同じ構造
- 開示水準: 応札者数・再就職役員数を全契約空欄、 他省庁より低い

---

## 4. データソース

- 📄 デジタル庁 公共調達適正化情報公表（令和7年度）
  https://www.digital.go.jp/procurement/proper-public-procurement
- 📄 デジタル庁 入札等監視委員会（令和6年度第2回）議事概要
  https://www.digital.go.jp/procurement/bid-surveillance-commission/ee294e66-d874-4595-a2e3-fb84217906a0

---

## 5. ファイル構成（推奨）

backups/
　└── milestones/                                       マイルストーン（残す）
　　　├── index_master_R7_digital_YYYYMMDD_HHMM.html
　　　├── index_root_R7_digital_YYYYMMDD_HHMM.html
　　　└── tokubetsu-kaikei_R7_digital_YYYYMMDD_HHMM.tar.gz
　└── intermediate_YYYYMMDD_HHMM/                       中間bak（削除可）
　　　└── index.html.bak_*

logs/
　└── SESSION_LOG_YYYYMMDD_HHMM_R7_digital.md           本ログ

---

## 6. Xポスト原稿（130字以内・3パターン）

### 案A：不透明性フック
🇯🇵デジタル庁 R7公共調達

霞が関で最も不透明な省庁。
全343契約で「応札者数」「再就職役員数」が空欄。他省庁が記載する項目を、デジタル庁だけ非開示。

#FOJ #公共調達

### 案B：NEC独占フック
🇯🇵デジタル庁 R7

NEC独占が確定。¥553億で1位（2位の3.3倍）。
R7契約¥1,599億の61%がGSS関連、NECだけでGSS¥503億を独占。
応札者数は全343件空欄。

#FOJ

### 案C：総合パンチライン
🇯🇵デジタル庁 令和7年度

📊¥1,599億（343件）
🏆NEC独占¥553億（2位の3.3倍）
🔴落札率100% 22件
🔴応札者数・再就職役員数 全件空欄
🔴随意97%が「競争を許さない」根拠

#FOJ
