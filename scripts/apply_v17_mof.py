#!/usr/bin/env python3
"""v17: 財務省R7本省カードをMINISTRIES_2025に追加"""
import shutil, re
from datetime import datetime
from pathlib import Path

FILES = [
    Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html"),
    Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/index.html"),
]

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
for f in FILES:
    if f.exists():
        shutil.copy(f, str(f) + f".bak_v17_{ts}")
        print(f"✓ バックアップ: {f.name}.bak_v17_{ts}")

# ソース定義（mof_zuii_r6 の直後に挿入）
NEW_SOURCE = '''  mof_zuii_r7: {label:"📄 財務省 R7本省 公共調達の適正化に係る情報の公表（11ヶ月44ファイル）", url:"https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm"},
'''

# 財務省R7カード本体
MOF_R7_CARD = '''  {
    id:"mof", name:"財務省", alert:true, tag:"R7¥656億・富士通¥199億IT独占・NTTデータ官庁会計¥194億・造幣局¥172億継続",
    note:"令和7年度の財務省本省調達は確認済み総額¥655.78億・242件（≥¥1M案件・11ヶ月Excel集計、令和7年4月〜令和8年2月公表分）。種類別：物品役務競争121件¥364.91億+物品役務随契97件¥275.66億+公共工事競争24件¥15.21億+公共工事随契0件。R6（R5データ・随契のみ¥184.2億）と比較すると競争入札を含めて全体像が3.5倍に拡大。最大の構造的発見は富士通が¥199.49億・26件で財務省ITインフラ全体を独占（予算編成支援システム8次・財務省理財局更改・国有財産総合情報・会計業務電子決裁基盤等）。NTTデータが官庁会計システム（ADAMS）¥194.35億で実質2位（表記揺れで全角・半角分離だが法人番号同一）。造幣局への100%随契¥171.60億は R5(167.1億)→R6(171億)→R7(171.6億) と毎年微増で固定化。NEC財務省LANシステム¥29.01億の100%随契も R7新規発見（厚労省LAN東芝¥482億と類似のロックイン構造）。BlackRock外貨資産運用は R5(6.5億)→R6(6.6億)→R7(7.15億) と毎年微増で米国大手資産運用会社への継続随契。",
    primary_facts:[
      {text:"📄 <strong>R7財務省本省 合計¥655.78億・242件</strong>（≥¥1M、令和7年4月〜令和8年2月の11ヶ月Excel集計）。種類別：物品役務競争121件¥364.91億 / 物品役務随契97件¥275.66億 / 公共工事競争24件¥15.21億 / 公共工事随契0件。R6（R5データ随契のみ¥184.2億）から競争入札含めて3.5倍に拡大。出典：<a href='https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm' target='_blank' style='color:#4a8aff'>財務省 公共調達の適正化に係る情報の公表（令和7年度）</a>", src:"mof_zuii_r7"},
      {text:"📄 <strong>令和7年4月集中発注 ¥484.37億（全体の73.9%・132件）</strong>：年度開始時に大型情報システム年間契約をまとめて発注する官庁会計の慣習。8月以降は毎月¥1〜10億規模。この4月集中だけで R6（R5データ¥184億）の2.6倍超。", src:"mof_zuii_r7"},
      {text:"📄 <strong>富士通の財務省ITインフラ完全ロックイン ¥199.49億・26件（実質1位）</strong>：予算編成支援システム8次（賃貸借¥40.63億+維持管理¥39.75億）¥80.38億、財務省理財局情報システム更改（機器構築・賃貸借・保守）¥39.34億+α、国有財産総合情報管理システム（運用+保守）¥14.05億、会計業務電子決裁基盤・証拠書類管理システム¥24.96億等。「次世代化」更新サイクルで永続的に富士通が受注する典型。", src:"mof_zuii_r7"},
      {text:"📄 <strong>NTTデータ官庁会計システム（ADAMS）独占 ¥194.35億・7件</strong>：官庁会計システム等更新¥133.90億（競争入札・落札率「-」=予定価格非公表）+運用保守¥33.15億+クラウドサービス¥26.73億（100%随契）等。<strong>⚠️表記揺れ問題：「株式会社ＮＴＴデータ」（全角¥134.47億・5件）と「株式会社NTTデータ」（半角¥59.88億・2件）に分裂集計、法人番号は同一</strong>。名寄せすれば実質2位。", src:"mof_zuii_r7"},
      {text:"📄 <strong>独立行政法人造幣局への100%随契継続 ¥171.60億</strong>：「貨幣の製造に関する事務 一式」。R5(167.1億)→R6(171.0億)→R7(171.6億) と<strong>毎年微増で固定化</strong>。財務省所管の独立行政法人への随意契約還流構造そのまま。R7全体の26%を造幣局1社が占める。", src:"mof_zuii_r7"},
      {text:"📄 <strong>R7新規発見：NEC財務省LANシステム ¥29.01億・100%随契</strong>：行政情報化LAN（賃貸借期間：令和7年4月1日～令和9年6月）。R5・R6では取れていなかった案件。<strong>厚労省R7のLAN（東芝¥482億）と類似のロックイン構造</strong>。賃貸借契約の更新サイクルが見える。さらにNEC「行政LAN（端末）」¥2.44億・100%随契も同時受注。", src:"mof_zuii_r7"},
      {text:"📄 <strong>BlackRock外貨資産運用の経年微増 ¥7.15億・100%随契</strong>：R5(6.5億)→R6(6.6億)→R7(7.15億) と<strong>毎年微増継続</strong>。「外国為替資金特別会計の保有する外貨資産の運用分析に係るレポート提供業務」。日本の外貨準備（約1.3兆ドル）の運用分析を米国大手資産運用会社に毎年随契。国内の運用会社を構造的に排除。", src:"mof_zuii_r7"},
      {text:"📄 <strong>R7新規発見：電通東日本の国債広告 ¥4.01億・競争入札</strong>：「国債広告の企画・制作及び実施委託業務」。財務省→電通系列の地方法人への国債PR広告予算。", src:"mof_zuii_r7"},
      {text:"📄 <strong>落札率「-」（予定価格非公表）の競争入札が多数</strong>：Top10案件のうち競争入札系のNTTデータ¥133.90億、富士通¥40.63億、¥39.75億、¥39.34億等が全て落札率「-」表記。デジタル庁R7「予定価格非公表45件」「個別契約の応札者数・再就職役員数空欄」と同じ透明性問題が財務省でも観察される。", src:"mof_zuii_r7"},
      {text:"📄 <strong>外国為替情報提供の継続随契：リフィニティブ・ジャパン¥1.92億・7件 / ブルームバーグL.P.¥1.55億・1件</strong>：「WORKSPACE等による外国為替情報等の提供」「ブルームバーグによる外国債価格情報等の提供」等。米英資本の外為情報ベンダー2社への継続随契。BlackRockと合わせて<strong>外貨準備運用の情報インフラがすべて外資</strong>。", src:"mof_zuii_r7"},
      {text:"🏛 <strong>【構造的問題】R6→R7で見えた「3社集中構造」</strong>：R6（R5データ）では「造幣局91%独占の単純構造」だったが、R7で競争入札を含めると<strong>富士通¥199億+NTTデータ¥194億+造幣局¥172億=¥565億（全体の86.2%）の3社集中</strong>に拡大した IT利権構造が露呈。「特別会計の番人」である財務省が、自省所管法人（造幣局）と特定ITベンダー2社にほぼ全予算を集中させる構造。", src:"mof_zuii_r7"},
      {text:"🚩 <strong>R7次フェーズの優先課題</strong>：①NTTデータ官庁会計システム¥133.90億の応札者数・落札率欄を情報公開請求で取得。②富士通の予算編成支援システム「8次」の経年契約推移（1次〜7次の累積金額）を調査しロックイン構造を立証。③造幣局への随意契約理由書（R5〜R7）の入手と貨幣製造コスト構造の検証。④BlackRockへの外貨運用委託の選定経緯と国内運用会社が排除されている合理性の確認。⑤財務省所管独法（造幣局・国立印刷局・統計センター）への発注の全体把握。", src:"mof_zuii_r7"},
    ],
    houjin:[
      {name:"富士通株式会社", region:"財務省本省（IT全般）", gyomu:"予算編成支援システム8次¥80億・財務省理財局情報システム更改¥40億+α・国有財産総合情報管理¥14億・会計業務電子決裁基盤¥25億等26件", amount_oku:199.49, tensyakuri:"📋 デジタル庁R7・厚労省R7と同じくR5公表2人（元警視総監→執行役員SEVP・元国交省大臣官房付→シニアアドバイザー）。財務省契約への直接クロスは未確認"},
      {name:"独立行政法人造幣局", region:"財務省所管独法", gyomu:"貨幣の製造に関する事務 一式¥171.60億（100%随契・R5→R6→R7で167.1→171.0→171.6億と毎年微増）", amount_oku:171.60, tensyakuri:"🤖 未確認（財務省所管法人）"},
      {name:"株式会社NTTデータ（全角・半角統合）", region:"財務省本省（官庁会計システム）", gyomu:"官庁会計システム等更新¥133.90億（競・落札率「-」）+運用保守¥33.15億+クラウドサービス¥26.73億等 計7件。⚠️表記揺れで全角¥134.47億・5件+半角¥59.88億・2件に分裂集計、法人番号は同一", amount_oku:194.35, tensyakuri:"🤖 未確認（厚労省R7でも¥41.39億・労保徴収システムOCR等を受注、R6では受注総額¥1,421億のうち随意¥962億独占）"},
      {name:"日本電気株式会社（NEC）", region:"財務省本省（LANシステム）", gyomu:"財務省行政情報化LAN¥29.01億（100%随契）+行政LAN端末¥2.44億（100%随契）+不正侵入防御装置¥1.17億+α 計4件", amount_oku:32.66, tensyakuri:"📋 デジタル庁R7・厚労省R7と同じくR5公表5人がNECに集中（元経産審議官→Corporate SEVP副社長等）"},
      {name:"日本電設工業株式会社", region:"財務省本省（公共工事）", gyomu:"財務省本庁舎非常用発電設備増設工事¥7.97億（競争入札・99.9%）1件", amount_oku:7.97, tensyakuri:"🤖 未確認"},
      {name:"BlackRock Financial Management,Inc.", region:"外国為替資金特別会計", gyomu:"外貨資産運用分析¥7.15億（100%随契・R5→R6→R7で6.5→6.6→7.15億と毎年微増）", amount_oku:7.15, tensyakuri:"🤖 未確認（米国本社・国内資産運用会社が構造的に排除）"},
      {name:"ソフトバンク株式会社", region:"財務省本省（通信）", gyomu:"インターネット接続回線等業務¥4.46億（100%随契）等2件", amount_oku:4.53, tensyakuri:"🤖 未確認"},
      {name:"株式会社電通東日本", region:"財務省本省（広告）", gyomu:"国債広告の企画・制作及び実施委託業務¥4.01億（競争入札）等2件", amount_oku:4.40, tensyakuri:"🤖 未確認（電通系列地方法人）"},
      {name:"KDDI株式会社", region:"財務省本省（通信）", gyomu:"財務省理財局情報システム通信回線提供等¥2.07億等6件", amount_oku:2.90, tensyakuri:"🤖 未確認"},
      {name:"リフィニティブ・ジャパン株式会社", region:"外国為替資金特別会計", gyomu:"WORKSPACE等による外国為替情報等の提供¥1.92億・7件（一部100%随契）", amount_oku:1.92, tensyakuri:"🤖 未確認（旧トムソン・ロイター金融部門、LSEGグループ）"},
      {name:"ブルームバーグL.P.", region:"外国為替資金特別会計", gyomu:"ブルームバーグによる外国債価格情報等の提供¥1.55億（100%随契）1件", amount_oku:1.55, tensyakuri:"🤖 未確認（米国本社）"},
      {name:"PwCコンサルティング/Japan", region:"財務省本省（投融資コンサル）", gyomu:"産業投資のポートフォリオ管理運営コンサルティング業務¥0.50億（100%随契）等", amount_oku:1.71, tensyakuri:"📋 デジタル庁R7でR5公表1人（元農林水産省輸出企画課調査官→マネージャー）"},
    ],
    houjin_note:"令和7年度・財務省本省 公共調達適正化情報公表 月次Excel11ヶ月分（令和7年4月〜令和8年2月公表分）を集計、≥¥1M案件のみ採録、計242件・¥655.78億。⚠️NTTデータの表記揺れ（全角・半角）は法人番号で名寄せすれば実質第2位。📋OB再就職情報はデジタル庁R7・厚労省R7で確認済みの内閣人事局R5公表とのクロスを併記。財務省契約への直接クロスは次フェーズで実施予定。出典：財務省 公共調達の適正化に係る情報の公表（令和7年度）",
    accounts:[
      {name:"物品役務（IT・情報システム中心）",amount_oku:640.57,alert:true,
       note:"令和7年度・本省物品役務 計¥640.57億・218件（競争121件¥364.91億+随契97件¥275.66億）。R5財務省全体（¥184億）の3.5倍。富士通¥199.49億（26件・予算編成支援システム8次/理財局更改/国有財産/会計電子決裁等のIT全独占）が事実上1位、NTTデータ官庁会計システム¥194.35億（7件・表記揺れ統合）が実質2位、造幣局¥171.60億（貨幣製造・100%随契毎年微増固定）、NEC¥32.66億（財務省LAN賃貸借・新規発見）、BlackRock¥7.15億（外貨資産運用毎年微増継続）。R6で見えなかった「富士通+NTTデータ+造幣局の3社集中¥565億・全体86%」というIT利権構造が R7で露呈。",
       contract:"物品役務 競争入札121件¥364.91億＋随意契約97件¥275.66億",
       src_key:"mof_zuii_r7",src_url:"https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm"},
      {name:"公共工事（本庁舎・宿舎改修中心）",amount_oku:15.21,alert:false,
       note:"令和7年度・本省公共工事 計¥15.21億・24件（競争入札24件・随意契約0件）。最大は日本電設工業¥7.97億「財務省本庁舎非常用発電設備増設工事」（99.9%）。次にプランドシー¥2.08億「財務省下落合宿舎内装ほか修繕工事」（83.3%）。本庁舎・宿舎の改修修繕が中心。",
       contract:"公共工事 競争入札24件・随意契約0件",
       src_key:"mof_zuii_r7",src_url:"https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm"},
      {name:"R6→R7構造変化（造幣局単独→3社集中）",amount_oku:565,alert:true,
       note:"R6（R5データ・随契のみ¥184億）では「造幣局167億で91%独占」の単純構造だったが、R7で競争入札含めると<strong>富士通¥199億+NTTデータ¥194億+造幣局¥172億=¥565億（全体86%）の3社集中構造</strong>に拡大。「特別会計の番人」である財務省が自省所管法人（造幣局）と特定IT2社（富士通・NTTデータ）にほぼ全予算を集中させるIT利権構造が R7で露呈。",
       contract:"3社集中の構造的問題",
       src_key:"mof_zuii_r7",src_url:"https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm"},
      {name:"外貨資産運用の外資独占",amount_oku:10.62,alert:true,
       note:"外国為替資金特別会計（外貨準備約1.3兆ドル）の情報インフラがすべて外資。BlackRock Financial Management ¥7.15億（米国・運用分析）、リフィニティブ・ジャパン¥1.92億（英国LSEGグループ・外為情報）、ブルームバーグL.P.¥1.55億（米国・外国債価格情報）等で計¥10.62億。<strong>BlackRockは R5(6.5億)→R6(6.6億)→R7(7.15億) と毎年微増継続</strong>。国内運用会社・情報ベンダーが構造的に排除される合理性の確認が必要。",
       contract:"全件 随意契約（競争を許さない・100%）",
       src_key:"mof_zuii_r7",src_url:"https://www.mof.go.jp/application-contact/procurement/approach/tekiseika/index.htm"},
    ]
  }'''

for f in FILES:
    if not f.exists(): continue
    print(f"\n--- 処理中: {f.name} ---")
    content = f.read_text(encoding="utf-8")
    
    # 1. ソース定義の追加（mof_zuii_r6 の直後）
    if "mof_zuii_r7" in content:
        print(f"  既存ソース定義あり、スキップ")
    else:
        pattern = r'(mof_zuii_r6: \{label:"📄 財務省[^}]+\},\n)'
        new_content = re.sub(pattern, r'\1' + NEW_SOURCE, content, count=1)
        if new_content == content:
            print(f"  ⚠ ソース定義アンカー(mof_zuii_r6)未発見、スキップ")
        else:
            content = new_content
            print(f"  ✓ ソース定義 mof_zuii_r7 追加")
    
    # 2. MINISTRIES_2025 配列に財務省R7カードを挿入
    if 'id:"mof", name:"財務省", alert:true, tag:"R7¥656億' in content:
        print(f"  既存R7財務省カードあり、スキップ")
    else:
        m = re.search(r'var MINISTRIES_2025 = \[', content)
        if not m:
            print(f"  ❌ MINISTRIES_2025 未発見")
            continue
        
        start = m.end()
        depth = 1
        pos = start
        in_str = False
        in_tpl = False
        prev = ''
        while pos < len(content) and depth > 0:
            c = content[pos]
            if not in_str and not in_tpl:
                if c == '"' and prev != '\\':
                    in_str = True
                elif c == '`' and prev != '\\':
                    in_tpl = True
                elif c == '[':
                    depth += 1
                elif c == ']':
                    depth -= 1
            else:
                if in_str and c == '"' and prev != '\\':
                    in_str = False
                elif in_tpl and c == '`' and prev != '\\':
                    in_tpl = False
            prev = c
            pos += 1
        
        if depth == 0:
            close_pos = pos - 1
            j = close_pos - 1
            while j > start and content[j] in ' \t\n':
                j -= 1
            if content[j] == '}':
                insertion = ',\n' + MOF_R7_CARD + '\n'
            else:
                insertion = '\n' + MOF_R7_CARD + '\n'
            content = content[:close_pos] + insertion + content[close_pos:]
            print(f"  ✓ MINISTRIES_2025 に財務省R7カード挿入（pos={close_pos}）")
        else:
            print(f"  ❌ MINISTRIES_2025 閉じ括弧未発見")
            continue
    
    f.write_text(content, encoding="utf-8")
    print(f"  ✓ 書き込み完了")

print("\n=== v17 反映完了 ===")
print("検証コマンド:")
print('  grep -c "mof_zuii_r7" /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html')
print('  grep -c "富士通¥199億IT独占" /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html')
print('  grep -c "造幣局" /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html')
