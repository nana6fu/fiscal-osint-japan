#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# R7デジタル庁ダッシュボードに 内閣人事局R5公表との
# クロスリファレンス結果（B案+C案）を統合するパッチ

from pathlib import Path
import shutil
import datetime

MASTER = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html")
ROOT = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html")
src = MASTER if MASTER.exists() else ROOT

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak = src.parent / f"index.html.bak_{ts}"
shutil.copy(src, bak)
print(f"Backup: {bak}")

content = src.read_text(encoding="utf-8")
orig_len = len(content)

# === [1] SOURCES に jinjikyoku_r5 を追加 ===
SOURCE_ANCHOR = 'daj_r7_proc: {label:"📄 デジタル庁 公共調達適正化情報公表（令和7年度）", url:"https://www.digital.go.jp/procurement/proper-public-procurement"},'

SOURCE_NEW = (
    SOURCE_ANCHOR
    + '\n  jinjikyoku_r5: {label:"📄 内閣人事局 国家公務員再就職状況の公表（令和5年度）", url:"https://www.cas.go.jp/jp/gaiyou/jimu/jinjikyoku/106-25-2/r06/kouhyou_0924.html"},'
)

# === [2] primary_facts に 2件追加（B案 + C案） ===
# 既存の最終fact「構造的問題」エントリの直後に挿入
ANCHOR_FACT_END = 'アクセンチュア無断再委託・指名停止」問題と地続きの構造。", src:"daj_r7_proc"},'

NEW_FACT_B = """{text:"🚩 <strong>R5年度・国家公務員OB再就職とR7契約の重なり（内閣人事局公表との突合）</strong>：① 経済産業審議官（事務次官級）2人 → NEC Corporate SEVP（副社長）／日立製作所 社長付（両社のR7契約計¥573億）。② 警視総監 → 富士通 執行役員SEVP、 警視庁副総監 → NTT東日本 特別参与。③ 国土交通省航空局管制技術課長 → NEC エアロスペース事業部門 参与（業務直結）。④ 元 内閣サイバーセキュリティセンター（NISC）参事官 → デロイト ディレクター。⑤ 元 金融庁検査企画官 → アクセンチュア プリンシプル・ディレクター（同社はR6で4ヶ月指名停止）。合計13人がデジタル庁R7受注7社（計¥830億・全契約の約52%）に再就職。出典：<a href='https://www.cas.go.jp/jp/gaiyou/jimu/jinjikyoku/106-25-2/r06/kouhyou_0924.html' target='_blank' style='color:#4a8aff'>内閣人事局 国家公務員再就職状況の公表（令和5年度）</a>", src:"jinjikyoku_r5"},"""

NEW_FACT_C = """{text:"📊 <strong>NEC ¥553億受注への国家公務員OB集中（5人）</strong>：内閣人事局R5公表データで、 NECには5人が再就職。①経済産業審議官（事務次官級）→Corporate SEVP（副社長）、 ②財務省関税局長→顧問、 ③国土交通省航空局管制技術課長→エアロスペース事業部参与、 ④財務省大臣官房付→嘱託（上席主幹）、 ⑤外務省（内閣情報調査室併任）→上席プロフェッショナル。 NEC R7契約¥553億は2位NTTデータ¥166億の3.3倍。 ※公開データの相関であり違法性を断定するものではない。", src:"jinjikyoku_r5"},"""

FACT_NEW_BLOCK = ANCHOR_FACT_END + "\n      " + NEW_FACT_B + "\n      " + NEW_FACT_C

# === [3] houjin テーブルの tensyakuri を 7社分更新 ===
HOUJIN_PATCHES = [
    (
        'amount_oku:552.9, tensyakuri:"🤖未確認（13件・随5/競8）"',
        'amount_oku:552.9, tensyakuri:"📋R5公表5人: 元経済産業審議官→Corporate SEVP副社長、 元財務省関税局長→顧問、 元国交省航空局管制技術課長→エアロスペース参与 他"',
        "houjin: NEC",
    ),
    (
        'amount_oku:149.7, tensyakuri:"🤖未確認（8件・法人番号で名寄せ）"',
        'amount_oku:149.7, tensyakuri:"📋R5公表1人: 元警視庁副総監→特別参与"',
        "houjin: NTT東日本",
    ),
    (
        'amount_oku:39.7, tensyakuri:"🚩R6で4ヶ月指名停止、R7で6件受注復帰（随5/競1）"',
        'amount_oku:39.7, tensyakuri:"🚩R6で4ヶ月指名停止 + 📋R5公表1人: 元金融庁検査企画官→プリンシプル・ディレクター"',
        "houjin: アクセンチュア",
    ),
    (
        'amount_oku:32.2, tensyakuri:"🤖未確認（6件・随5/競1）"',
        'amount_oku:32.2, tensyakuri:"📋R5公表2人: 元警視総監→執行役員SEVP（社長特命）、 元国交省大臣官房付→シニアアドバイザー"',
        "houjin: 富士通",
    ),
    (
        'amount_oku:21.5, tensyakuri:"🤖未確認（13件・随8/競5）"',
        'amount_oku:21.5, tensyakuri:"📋R5公表1人: 元農林水産省輸出企画課調査官→マネージャー"',
        "houjin: PwC",
    ),
    (
        'amount_oku:20.0, tensyakuri:"🤖未確認（4件・随3/競1）"',
        'amount_oku:20.0, tensyakuri:"📋R5公表2人: 元経済産業審議官→社長付、 元総務省大臣官房付→公共システム事業部特別顧問"',
        "houjin: 日立製作所",
    ),
    (
        'amount_oku:13.2, tensyakuri:"🤖未確認（9件・随5/競4）"',
        'amount_oku:13.2, tensyakuri:"📋R5公表1人: 元 内閣サイバーセキュリティセンター（NISC）参事官→ディレクター"',
        "houjin: デロイト",
    ),
]

# === [4] houjin_note の更新 ===
NOTE_OLD = '令和7年度・公表ファイル19本（2025年4-12月分・全343契約）を集計。NTT東日本・NTTコミュニケーションズ・KDDIは法人番号で名寄せ済み。※R7第4四半期（2026/1-3）データ未公開、2026年7月以降に更新予定。出典：デジタル庁 公共調達適正化情報公表（令和7年度）'

NOTE_NEW = '令和7年度・公表ファイル19本（2025年4-12月分・全343契約）を集計。NTT東日本・NTTコミュニケーションズ・KDDIは法人番号で名寄せ済み。📋OB再就職情報は内閣人事局 令和5年度公表（1,586件）とのクロスリファレンスで7社に計13人を確認。※R7第4四半期（2026/1-3）データ未公開、2026年7月以降に更新予定。出典：デジタル庁 公共調達適正化情報公表（令和7年度）・内閣人事局 再就職状況の公表（令和5年度）'

# === [5] tag の更新 (天下り重なり追加) ===
TAG_OLD = 'tag:"GSS統合年・NEC一強・契約レベルの開示は限定的"'
TAG_NEW = 'tag:"GSS統合年・NEC一強・受注7社全社にOB再就職"'

# ==================== パッチ実行 ====================
print("\n=== R7デジタル庁ダッシュボード 統合パッチ ===\n")

# 1. SOURCES
if SOURCE_ANCHOR in content:
    content = content.replace(SOURCE_ANCHOR, SOURCE_NEW, 1)
    print("[OK] 1) SOURCES に jinjikyoku_r5 を登録")
else:
    print("[WARN] 1) SOURCES anchor not found")

# 2. primary_facts に2件追加
if ANCHOR_FACT_END in content:
    content = content.replace(ANCHOR_FACT_END, FACT_NEW_BLOCK, 1)
    print("[OK] 2) primary_facts に 2件追加（B案+C案）")
else:
    print("[WARN] 2) primary_facts anchor not found")

# 3. houjin tensyakuri 7社更新
for old, new, label in HOUJIN_PATCHES:
    if old in content:
        content = content.replace(old, new, 1)
        print(f"[OK] 3) {label}")
    else:
        print(f"[WARN] 3) {label}: anchor not found")

# 4. houjin_note
if NOTE_OLD in content:
    content = content.replace(NOTE_OLD, NOTE_NEW, 1)
    print("[OK] 4) houjin_note 更新")
else:
    print("[WARN] 4) houjin_note anchor not found")

# 5. tag
if TAG_OLD in content:
    content = content.replace(TAG_OLD, TAG_NEW, 1)
    print("[OK] 5) tag 更新")
else:
    print("[WARN] 5) tag anchor not found")

# 書き込み
src.write_text(content, encoding="utf-8")
new_len = len(content)
print(f"\nSize: {orig_len:,} -> {new_len:,} ({new_len - orig_len:+,} bytes)")

# Master/Root 同期
other = ROOT if src == MASTER else MASTER
if other != src and other.parent.exists():
    shutil.copy(src, other)
    print(f"Synced to: {other}")

print("\n=== 完了 ===")
print("cmd+shift+R でリロードして、 年度=2025 で確認してください。")
print("")
print("反映される内容:")
print(" ・タグ「GSS統合年・NEC一強・受注7社全社にOB再就職」")
print(" ・一次資料セクションに新規2件:")
print("    🚩 R5年度・国家公務員OB再就職とR7契約の重なり（5パターン）")
print("    📊 NEC ¥553億受注への国家公務員OB集中（5人内訳）")
print(" ・主要落札企業表の『OB再就職・役員情報』列で7社が📋確認済みに更新:")
print("    NEC / NTT東日本 / 富士通 / 日立 / アクセンチュア / PwC / デロイト")
print(" ・出典欄に内閣人事局を追加")
