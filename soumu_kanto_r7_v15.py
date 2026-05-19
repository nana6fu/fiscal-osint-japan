#!/usr/bin/env python3
"""
Fiscal OSINT Japan v15: 総務省R7 関東総合通信局 追加スクリプト
============================================================
実行場所: Mac terminal
実行コマンド:
  cd "/Volumes/SN0W8ALL/tokubetsu-kaikei"
  python3 - << 'PYEOF'
  exec(open('/Volumes/SN0W8ALL/tokubetsu-kaikei/soumu_kanto_r7_v15.py').read())
  PYEOF

または直接:
  python3 /Volumes/SN0W8ALL/tokubetsu-kaikei/soumu_kanto_r7_v15.py

対象ファイル:
  /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html
  /Volumes/SN0W8ALL/tokubetsu-kaikei/index.html
"""

import re
import shutil
from datetime import datetime

# 設定 ----------------------------------------------------------------------
TARGETS = [
    "/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html",
    "/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html",
]
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================
# 修正1: ソースリンク追加（soumu_r7_procの直後に2本挿入）
# ============================================================
SRC_ANCHOR = '  soumu_r7_proc: {label:"📄 総務省 公共調達に関する公表（令和7年度）", url:"https://www.soumu.go.jp/menu_sinsei/cyoutatsu/koukyouchoutatsu.html"},'

SRC_INSERTION = SRC_ANCHOR + '''
  soumu_kanto_r7_kyou: {label:"📄 総務省 関東総合通信局 競争入札（物品役務等）令和7年度", url:"https://www.soumu.go.jp/main_content/001069763.pdf"},
  soumu_kanto_r7_zui: {label:"📄 総務省 関東総合通信局 随意契約（物品役務等）令和7年度", url:"https://www.soumu.go.jp/main_content/001069764.pdf"},
  soumu_kanto_r7_kouji: {label:"📄 総務省 関東総合通信局 競争入札（公共工事）令和7年度", url:"https://www.soumu.go.jp/main_content/001027266.pdf"},
  soumu_kanto_order: {label:"📄 総務省 関東総合通信局 調達情報トップページ", url:"https://www.soumu.go.jp/soutsu/kanto/other/order/index.html"},'''

# ============================================================
# 修正2: R7総務省 tag更新
# ============================================================
TAG_OLD = 'id:"soumu", name:"総務省", alert:true, tag:"GSSデータ連係終了予告（R8.10）・NEC電波監視ロックイン・J-LISマイナンバー独占",'
TAG_NEW = 'id:"soumu", name:"総務省", alert:true, tag:"GSSデータ連係終了予告（R8.10）・NEC電波監視ロックイン・J-LISマイナンバー独占・関東総合通信局R7追加（v15）",'

# ============================================================
# 修正3: R7総務省 note更新（地方追加宣言を末尾に追記）
# ============================================================
NOTE_OLD = '''note:"令和7年度の総務省本省（大臣官房会計課）調達は、トラッキング総額￥525.22億（11ヶ月・236契約・≥￥1M案件のみ採録、R7.10公共調達PDFは未公表）。実年額は￥600～700億規模と推定。電波監視設備の「設備一意性」ロックインを軸にNECが￥65.67億（17件・9件が落札率99.9%以上）でTOP1。J-LIS（地方公共団体情報システム機構）はマイナンバー4件￥55.34億を全て100%随意で独占。IBMは「総合無線局監理」コンピュータ機器再借入だけで￥39.82億。FY末（R8.2）にACCESS￥27.9億・BCG￥18.5億の駆け込み大型2件。GSS統合年（デジタル庁R7とリンク）の証拠として「総務省共通基盤支援システムが令和8年10月で終了 → GSS AMS/GIMA連係」が随意契約の理由欄に明記された一次資料を確認。※内閣人事局R5天下りクロスは次フェーズで実施予定（ハーフスライス）。",'''

NOTE_NEW = '''note:"令和7年度の総務省本省（大臣官房会計課）調達は、トラッキング総額￥525.22億（11ヶ月・236契約・≥￥1M案件のみ採録、R7.10公共調達PDFは未公表）。実年額は￥600～700億規模と推定。電波監視設備の「設備一意性」ロックインを軸にNECが￥65.67億（17件・9件が落札率99.9%以上）でTOP1。J-LIS（地方公共団体情報システム機構）はマイナンバー4件￥55.34億を全て100%随意で独占。IBMは「総合無線局監理」コンピュータ機器再借入だけで￥39.82億。FY末（R8.2）にACCESS￥27.9億・BCG￥18.5億の駆け込み大型2件。GSS統合年（デジタル庁R7とリンク）の証拠として「総務省共通基盤支援システムが令和8年10月で終了 → GSS AMS/GIMA連係」が随意契約の理由欄に明記された一次資料を確認。※内閣人事局R5天下りクロスは次フェーズで実施予定（ハーフスライス）。【v15更新】地方総合通信局11局のうち関東総合通信局R7（独立小規模・3PDF集計）を追加。本省NEC・三菱電機・IBMの「システム的ロックイン」に対し、地方は「現場機器ロックイン（製造メーカー個別）＋研究委託の大学集中＋庁舎管理の地場業者」で構造が異なる。",'''

# ============================================================
# 修正4: R7総務省 primary_facts に3項目追加（既存最後の jinjikyoku_r5 項目の前に挿入）
# ============================================================
PF_ANCHOR = '      {text:"🤖 <strong>内閣人事局R5天下りクロスは未着手（ハーフスライス・次フェーズ）</strong>：Top12のうち民間企業11社（NEC、三菱電機、三菱総研、BCG、ACCESS、楽天モバイル、富士通、アズビル、沖電気、IBM、IIJ）について国家公務員OB再就職クロスは次フェーズで実施予定。NECはデジタル庁R7クロスで既に5人（元経済産業審議官→Corporate SEVP、財務省関税局長→顧問、国交省航空局管制技術課長→エアロスペース参与等）が確認済みだが、「総務省契約に対する天下り」は別途検証が必要。", src:"jinjikyoku_r5"},'

PF_INSERTION = '''      {text:"📄 <strong>【v15新規】関東総合通信局R7：3PDF集計総額約￥8.2億（48件以上）</strong>：競争入札（物品役務）19件約￥3.59億、随意契約（物品役務）28件以上約￥1.55億、公共工事1件￥3.02億の合計。最大案件は競争入札の「非常用発電機等更新作業」（R8.2・株式会社大三洋行）￥1.46億、次が「短波監査装置の遠隔操作用簡易コンソール」（R7.4・日本無線株式会社）￥1.08億国庫債務R7-R8、3番が公共工事「三浦電波監視センターフェンス等改修」（R7.6・小雀建設）￥3.02億国庫債務R7-R8。三浦電波監視センター関連が随契28件中ほぼ半数を占める。出典：<a href=\\'https://www.soumu.go.jp/soutsu/kanto/other/order/index.html\\' target=\\'_blank\\' style=\\'color:#4a8aff\\'>関東総合通信局 調達情報ページ</a>", src:"soumu_kanto_order"},
      {text:"📄 <strong>【v15新規】関東R7 電波監視機器の「製造メーカー固有」ロックイン</strong>：本省のNEC（遠隔方位A型）・三菱電機（B型/短波/宇宙電波）の二大寡占に対し、地方では機器ごとに製造メーカー個別ロックイン。日本無線（短波監査装置）・東洋メディック（Narda S.T.S.較正・L70型電波スペクトル自動記録装置）・キーサイト（FieldFox N9960B・スペクトラムアナライザ広帯域化）・電気興業（三浦受信空中線）・勝島製作所（G60電波監視装置・クローバテック事業譲受）。全件「製造業者以外は対応不可」を随意契約理由として明記。スカパーJSATは「C帯静止衛星監視」3件￥21.25M（土地・建物借料・5G干渉モニタリング）で独占。", src:"soumu_kanto_r7_zui"},
      {text:"📄 <strong>【v15新規】関東R7 大学への研究委託集中：「持続可能な電波有効利用のための基盤技術研究開発事業」</strong>：R7.8.1に同事業の20件以上の研究委託が一斉に随意契約で発注。外部評価委員会の選定結果を根拠とする随契。委託先は東京理科大・大阪大・東大・横浜国大・三重大・新潟大・九州工業大・電気通信大・埼玉大・東京農工大・東京電機大・日本大・日本工業大・首都大学（東京都立大）・産総研・NICT等。1件あたり￥250〜975万。電波利用料財源の研究開発費が大学に再分配される構造の可視化。", src:"soumu_kanto_r7_zui"},
      {text:"🏛 <strong>【構造的問題・v15新規】「地方総合通信局」全11局の実態は本省￥525.22億の外側にある独立調達構造</strong>：関東局単体でR7約￥8.2億（48件以上）。11局合計推定￥80〜100億（局による規模差大）。本省houjin_noteの「実年額￥600〜700億推定」の差分は地方総合通信局・消防庁・統計局等の独立調達。今回関東1局を着手、他10局（北海道・東北・信越・北陸・東海・近畿・中国・四国・九州・沖縄）は未着手で次フェーズ。各局のPDF公開状況も統一されていない（局によっては個別案件HTMLのみ＝抽出困難）。", src:"soumu_kanto_order"},
'''

# ============================================================
# 修正5: R7総務省 houjin_note更新（地方追加宣言）
# ============================================================
HN_OLD = '''houjin_note:"令和7年度・本省（大臣官房会計課）公表ファイル22本のうち21本を集計（R7.10公共調達PDFは404・未公表）。≥￥1M案件のみ採録、計236契約・トラッキング総額￥525.22億。実年額は￥600～700億規模と推定。消防庁・統計局・地方総合通信局は別系統で除外。📋 OB再就職情報（内閣人事局R5公表とのクロスリファレンス）は次フェーズで実施予定（ハーフスライス）。出典：総務省 公共調達に関する公表 / 内閣人事局 再就職状況の公表（令和5年度）",'''

HN_NEW = '''houjin_note:"令和7年度・本省（大臣官房会計課）公表ファイル22本のうち21本を集計（R7.10公共調達PDFは404・未公表）。≥￥1M案件のみ採録、計236契約・トラッキング総額￥525.22億。実年額は￥600～700億規模と推定。消防庁・統計局・地方総合通信局は別系統で除外。📋 OB再就職情報（内閣人事局R5公表とのクロスリファレンス）は次フェーズで実施予定（ハーフスライス）。出典：総務省 公共調達に関する公表 / 内閣人事局 再就職状況の公表（令和5年度）　【v15・関東総合通信局R7追加】3PDF集計総額約￥8.2億・48件以上。出典：関東総合通信局 調達情報ページ（競争入札物品役務R7・随意契約物品役務R7・公共工事R7）",'''

# ============================================================
# 修正6: R7総務省 accounts に新セクション追加（既存最後の異常落札率の前に挿入）
# ============================================================
ACC_ANCHOR = '''      {name:"異常落札率案件（追加調査候補）",amount_oku:5.6,alert:true,'''

ACC_INSERTION = '''      {name:"【v15新規】関東総合通信局R7（地方初の地方総合通信局データ）",amount_oku:8.2,alert:true,
       note:"3PDF集計：競争入札物品役務19件約￥3.59億・随意契約物品役務28件以上約￥1.55億・公共工事1件￥3.02億＝合計約￥8.2億・48件以上。最大案件＝非常用発電機更新（大三洋行）￥1.46億、短波監査装置遠隔操作コンソール（日本無線・国庫債務R7-R8）￥1.08億、三浦電波監視センターフェンス改修（小雀建設・国庫債務R7-R8）￥3.02億。本省NEC・三菱電機の二大寡占ロックインに対し、地方は「製造メーカー個別ロックイン（日本無線/東洋メディック/キーサイト/電気興業/勝島製作所）＋スカパーJSAT独占（C帯衛星監視3件￥21.25M）＋大学への基盤技術研究委託（東京理科大・大阪大・東大・横浜国大等20件以上）＋庁舎管理の地場業者」で構造が異なる。次フェーズは他10地方総合通信局（北海道・東北・信越・北陸・東海・近畿・中国・四国・九州・沖縄）の調達情報ページの構造調査と取得・抽出。",
       contract:"競争入札＋随意契約混在（製造メーカー固有・大学評価委員会選定が随契理由の主軸）",
       src_key:"soumu_kanto_order",src_url:"https://www.soumu.go.jp/soutsu/kanto/other/order/index.html"},
      ''' + ACC_ANCHOR

# ============================================================
# 実行
# ============================================================

def apply_edits(path):
    print(f"\n=== {path} ===")

    # バックアップ
    backup = f"{path}.bak_v15_{TIMESTAMP}"
    shutil.copy(path, backup)
    print(f"✓ バックアップ: {backup}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)
    edits = [
        ("ソースリンク追加（4本）",         SRC_ANCHOR,    SRC_INSERTION),
        ("R7 tag更新",                      TAG_OLD,       TAG_NEW),
        ("R7 note更新",                     NOTE_OLD,      NOTE_NEW),
        ("R7 primary_facts追加（4項目）",   PF_ANCHOR,     PF_INSERTION + PF_ANCHOR),
        ("R7 houjin_note更新",              HN_OLD,        HN_NEW),
        ("R7 accounts追加（関東R7）",       ACC_ANCHOR,    ACC_INSERTION),
    ]

    for name, old, new in edits:
        count = content.count(old)
        if count == 0:
            print(f"  ✗ {name}: マッチなし（既に適用済みかパターン変更の可能性）")
            continue
        if count > 1:
            print(f"  ⚠ {name}: 複数マッチ({count}件)。最初の1件のみ置換")
            content = content.replace(old, new, 1)
        else:
            content = content.replace(old, new)
            print(f"  ✓ {name}: 置換成功")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    new_len = len(content)
    print(f"✓ 書込完了: {original_len} → {new_len} bytes ({new_len - original_len:+d})")

print("=" * 60)
print(f"Fiscal OSINT Japan v15 反映スクリプト")
print(f"実行時刻: {TIMESTAMP}")
print(f"対象: 関東総合通信局R7 追加")
print("=" * 60)

for path in TARGETS:
    try:
        apply_edits(path)
    except FileNotFoundError:
        print(f"\n✗ ファイル未発見: {path}")
    except Exception as e:
        print(f"\n✗ エラー {path}: {e}")

print("\n" + "=" * 60)
print("検証コマンド:")
print(r'  grep -c "MOD_KUMAMOTO_R7_SUMMARY" "/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html"')
print(r'  grep -c "soumu_kanto" "/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html"  # 期待値: 8前後')
print(r'  grep -c "v15新規" "/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html"  # 期待値: 5')
print("=" * 60)
print()
print("Git push手順:")
print("  cd /Volumes/SN0W8ALL/tokubetsu-kaikei")
print('  git add index.html src/frontend/index.html')
print('  git commit -m "v15: 総務省R7 関東総合通信局を追加（3PDF集計・約¥8.2億・48件）"')
print("  git push")
