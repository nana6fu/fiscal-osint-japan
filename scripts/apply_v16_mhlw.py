#!/usr/bin/env python3
"""v16: 厚労省R7本省5系統カードをMINISTRIES_2025に追加"""
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
        bak = f.parent / (f.name + f".bak_v16_{ts}")
        shutil.copy(f, bak)
        print(f"✓ バックアップ: {bak.name}")
    else:
        print(f"⚠ {f} が存在しない、スキップ")

NEW_SOURCES = '''  mhlw_r7_honsyo: {label:"📄 厚労省 R7本省 公共調達公表（25honsyo.html・14ファイル）", url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
  mhlw_r7_ippan: {label:"📄 厚労省 R7本省 一般会計（25honsyo_ippan_01-04）", url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
  mhlw_r7_nenkin: {label:"📄 厚労省 R7本省 年金特別会計業務勘定（25honsyo_nenkin_03-04）", url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
  mhlw_r7_roudou: {label:"📄 厚労省 R7本省 労働保険特別会計 徴収勘定（25honsyo_roudou_01-02）", url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
  mhlw_r7_rousai: {label:"📄 厚労省 R7本省 労働保険特別会計 労災勘定（25honsyo_rousai_01-02）", url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
  mhlw_r7_koyou: {label:"📄 厚労省 R7本省 労働保険特別会計 雇用勘定（25honsyo_koyou_01-04）", url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
'''

MHLW_R7_CARD = '''  {
    id:"mhlw", name:"厚生労働省", alert:true, tag:"5系統合計¥1,724億・東芝LAN¥482億・47都道府県100%随契",
    note:"令和7年度の厚労省本省（5系統）調達は確認済み総額約¥1,724億・約1,065件（≥¥1M案件のみ採録）。①一般会計¥1,261億・867件（東芝デジタルソリューションズ¥516.15億で厚労省LAN完全ロックイン、アクセンチュアG-MIS¥31.34億・落札率99.8%）②年金特会業務勘定¥41.5億（NEC年金番号管理サブ更改¥40.17億）③労働保険徴収勘定¥125億（富士通+NTTデータ+日立 3社で労働保険適用徴収システム¥87.64億の変更契約増額ロックイン）④労働保険労災勘定¥47億（不落随契のオンパレード）⑤労働保険雇用勘定¥250億（47都道府県への離職者等再就職訓練事業全件100%随契~¥130億+パソナリスキリング¥39.6億）。R6（R5データ・4勘定合算¥3,444億）からの拡充。出典：厚生労働省 随意契約・競争入札情報公表PDF（令和7年度・25honsyo.html配下14ファイル）",
    primary_facts:[
      {text:"📄 <strong>R7本省5系統合計：約¥1,724億・約1,065件</strong>。①一般会計¥1,260.71億・867件、②年金特会業務勘定¥41.51億・9件、③労働保険徴収勘定~¥125億・~59件、④労災勘定~¥47億・~50件、⑤雇用勘定~¥250億・~80件（≥¥1M案件のみ採録）。出典：<a href='https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html' target='_blank' style='color:#4a8aff'>厚労省 公共調達公表（令和7年度・本省）</a>", src:"mhlw_r7_honsyo"},
      {text:"📄 <strong>東芝デジタルソリューションズ¥516.15億（10件）：厚労省LAN完全ロックイン</strong>。¥481.61億「厚生労働省LANシステム更改整備・運用保守」（競争入札・76.0%）が単独で総務省R7全体（¥525億）の92%相当。¥91.13億「介護保険総合DB改修運用R7-R9」・¥71.22億「地域包括ケア見える化システム改修運用R7-R9」・¥33.04億「要介護認定ソフト改修運用R7-R9」を独占。介護保険DB系を全件独占する構造。", src:"mhlw_r7_ippan"},
      {text:"📄 <strong>NEC × マイナンバー番号管理 三省庁三角形</strong>。総務省R7 J-LIS¥55.34億（次期マイナンバーカード整備）に加え、厚労省R7年金特会¥40.17億（年金業務システム個人番号管理サブ更改・競争入札・落札率58.6%・応札2者）。マイナンバー基盤の運用は、総務省側・厚労省側両面でNECがロックイン。", src:"mhlw_r7_nenkin"},
      {text:"📄 <strong>アクセンチュア G-MIS¥31.34億・落札率99.8%：デジタル庁監視委員会警告パターンの再現</strong>。G-MIS（医療機関等情報支援システム）の機能拡充及び運用保守等業務一式¥31.34億を競争入札・99.8%で受注。デジタル庁監視委員会R6第6回で「変更契約の連発で1者確定」と警告されたパターンと同構造。アクセンチュアはR6で4ヶ月指名停止処分を受けたが、厚労省への発注には影響しない（省庁横断指名停止制度なし）。", src:"mhlw_r7_ippan"},
      {text:"📄 <strong>労働保険適用徴収システム：富士通＋NTTデータ＋日立 3社完全ロックイン</strong>。R3年度に締結した5年「国債」契約の<strong>変更契約による増額3件で¥87.64億</strong>：①富士通+東京センチュリー 本省サーバ機器 ¥42.31億（100%随意）、②富士通+東京センチュリー 端末機器 ¥27.05億（100%随意）、③NTTデータ OCR機器等 ¥18.28億（100%随意）。さらに④日立製作所+JECC 都道府県労働局LAN R4-R8 ¥26.25億（100%随意）。競争入札側では富士通が機能改修4契約を全1社応札97-98%で取得＝既設機器が富士通だから機能改修も富士通しかできない構造。", src:"mhlw_r7_roudou"},
      {text:"📄 <strong>47都道府県への「離職者等再就職訓練事業」 全件随意契約100% ~¥130億</strong>（雇用勘定）。東京都¥20.38億・兵庫県¥13.51億・北海道¥9.06億・埼玉県¥9.47億・千葉県¥8.81億・新潟県¥7.60億・愛知県¥6.48億・長野県¥5.69億…全47都道府県に対し会計法29条の3第4項「契約の性質が競争を許さない」根拠で100%随契。<strong>都道府県以外の事業者を構造的に排除</strong>。", src:"mhlw_r7_koyou"},
      {text:"📄 <strong>47県職業能力開発協会への「若年技能者人材育成支援」 全件「不落」随契99-100%</strong>。中央職業能力開発協会¥1.77億・大阪府協会¥9,080万・宮城県¥6,394万・群馬県¥5,855万・神奈川県¥4,712万…全47都道府県協会に対し、公告→1者応札→不落→不落随契のパターン。実質的に協会以外には公告開始時点で発注先が決まっている構造。計~¥15億規模。", src:"mhlw_r7_koyou"},
      {text:"📄 <strong>感染症・ワクチン関連の大型100%随契（一般会計）</strong>。①日本通運¥119.52億（備蓄用個人防護服等保管管理）②KMバイオロジクス¥47.30億（H5N1新型インフルワクチン原液購入）+¥3.03億（同 一部製剤化）③国立健康危機管理研究機構¥45.99億・21件（旧国立感染症研究所が令和7年4月に改組統合された組織への集中発注：感染症臨床研究NW¥25.13億・DAMT体制整備¥9.88億・薬剤耐性臨床情報センター¥3.87億等）④社会保険診療報酬支払基金¥32.27億・5件。", src:"mhlw_r7_ippan"},
      {text:"📄 <strong>歴史的継続事業：戦没者・原爆・公害補償</strong>。①三井三池炭鉱CO中毒患者特別対策事業 福岡県社会保険医療協会¥4.94億（労災勘定・100%随契・60年継続）②戦没者遺骨収集 日本戦没者遺骨収集推進協会¥9.94億＋硫黄島掘削調査 鹿島建設東京土木支店¥10.09億③長崎・広島の被爆者関係事業計~¥25.88億（長崎市¥12.15億・長崎県¥5.40億+¥3.03億・広島平和文化センター¥3.26億・長崎平和推進協会¥2.74億・広島県¥2.33億等）。", src:"mhlw_r7_ippan"},
      {text:"📄 <strong>三菱総合研究所 ¥50.13億（27件）：厚労省コンサル分野独占</strong>。介護保険総合DB等介護関連システム改修工程管理¥9.07億・指定難病及び小児慢性特定疾病対策の電子化全体管理¥8.67億・自治体検診DXの推進¥5.70億・医療機能情報提供制度プロジェクト管理¥4.12億・入院外来機能分化等データ収集分析¥3.50億等、政策立案系の調査研究を27件で独占。R7一般会計の業者別件数No.1。", src:"mhlw_r7_ippan"},
      {text:"🏛 <strong>【構造的問題】R6（R5データ・4勘定合算¥3,444億）からの変化と地続き</strong>：①R6厚労省ハイライト「富士通ハローワークシステム¥1,025億」「NTTデータ年金Phase2¥839億」など本省超大型システム案件は5年契約のため毎年計上はされず、R7年度の毎年支出として表面化するのは「変更契約増額」や「保守・改修」の形で確認可能。②R7労働保険徴収システム¥87.64億の「変更契約増額」3件はまさにこのパターン。③R6の「アクセンチュア利益相反リスク」がR7のG-MIS¥31.34億・99.8%として表面化。④R6で言及された「ロックイン構造（競争入札で大型を取った後保守を随契化）」がR7東芝デジタルソリューションズ¥516.15億（厚労省LAN+介護保険DB系）として完全に観察される。", src:"mhlw_r7_honsyo"},
      {text:"🚩 <strong>R7次フェーズの優先課題</strong>：①R7労働保険適用徴収システム変更契約増額3件¥87.64億の「変更契約理由書」情報公開請求。②47都道府県への離職者等再就職訓練事業¥130億の都道府県内訳と再委託先の調査。③47県職業能力開発協会の「不落随契」パターンの公告内容・予定価格算定根拠。④東芝デジタルソリューションズ¥481.61億の厚労省LAN契約の応札者数（PDF未記載）。⑤厚労省R6→R7のNTTデータ・富士通・日立の保守系契約金額の経年比較（ロックイン構造の検証）。⑥地方厚生支局8局（北海道・東北・関東信越・東海北陸・近畿・中国四国・四国・九州）の調達データの取得・抽出。", src:"mhlw_r7_honsyo"},
    ],
    houjin:[
      {name:"東芝デジタルソリューションズ株式会社", region:"一般会計（厚労省LAN・介護保険DB）", gyomu:"厚生労働省LANシステム更改整備¥481.61億（競・76.0%）・介護保険総合DB R7-R9¥91.13億・地域包括ケア見える化R7-R9¥71.22億・要介護認定ソフトR7-R9¥33.04億等10件", amount_oku:516.15, tensyakuri:"🚩 厚労省LAN完全ロックイン構造。応札者数欄非公開（要追加調査）"},
      {name:"日本通運株式会社", region:"一般会計（健康危機管理）", gyomu:"備蓄用個人防護服等保管管理¥119.52億（100%随契）1件", amount_oku:119.52, tensyakuri:"🤖 未確認（コロナ禍備蓄の継続事業）"},
      {name:"富士通株式会社（含む東京センチュリーJV）", region:"③徴収・①一般会計・④労災", gyomu:"労保適用徴収システム本省サーバ¥42.31億（随・変更契約増額）・端末機器¥27.05億（随・変更契約増額）・機能改修4件¥1.56億（競・全1社応札・平均97.9%）・技能講習修了証明書発行管理¥3.26億（競・99.0%・1社応札）等", amount_oku:74.18, tensyakuri:"📋 デジタル庁R7でR5公表2人（元警視総監→執行役員SEVP・元国交省大臣官房付→シニアアドバイザー）"},
      {name:"ＫＭバイオロジクス株式会社", region:"一般会計（感染症）", gyomu:"H5N1新型インフルワクチン原液購入¥47.30億・一部製剤化¥3.03億等3件（全件100%随契）", amount_oku:51.62, tensyakuri:"🤖 未確認（旧化血研、明治HD傘下）"},
      {name:"株式会社三菱総合研究所", region:"一般会計（政策コンサル）", gyomu:"介護保険DB工程管理¥9.07億・難病小児慢性疾病電子化¥8.67億・自治体検診DX¥5.70億・医療機能情報PM¥4.12億・入院外来機能分化¥3.50億等27件", amount_oku:50.13, tensyakuri:"🤖 未確認（厚労省政策立案コンサル独占・件数No.1）"},
      {name:"アクセンチュア株式会社", region:"一般会計（G-MIS等）", gyomu:"G-MIS機能拡充¥31.34億（競・99.8%）・オンライン資格確認¥5.28億等9件", amount_oku:47.71, tensyakuri:"🚩 R6でデジタル庁4ヶ月指名停止・R5公表で元金融庁検査企画官→プリンシプル・ディレクター"},
      {name:"日本電気株式会社（NEC）", region:"②年金特会・①一般会計", gyomu:"年金業務システム個人番号管理サブ更改¥40.17億（競・58.6%・応札2者）・介護情報電子的共有実証¥5.94億等", amount_oku:46.11, tensyakuri:"📋 R5公表5人がNECに集中（元経産審議官→Corporate SEVP副社長等）。総務省R7（J-LIS関連¥55.34億）と合わせマイナンバー基盤を独占"},
      {name:"パソナ株式会社", region:"⑤雇用勘定", gyomu:"キャリア形成・リスキリング推進¥39.60億（競・95.6%）・中小企業育介推進¥2.70億・特区雇用労働相談センター4ヶ所", amount_oku:45.30, tensyakuri:"🤖 未確認（R6でも雇用勘定¥21億受注）"},
      {name:"国立健康危機管理研究機構", region:"一般会計（感染症研究）", gyomu:"感染症臨床研究NW¥25.13億・DAMT体制整備¥9.88億・薬剤耐性臨床情報センター¥3.87億・国際感染症危機管理¥2.59億等21件（全件100%随契）", amount_oku:45.99, tensyakuri:"🤖 旧国立感染症研究所が令和7年4月に改組統合された組織"},
      {name:"株式会社NTTデータ", region:"③徴収・①一般会計", gyomu:"労保適用徴収システムOCR機器¥18.28億（随・変更契約増額）・診療報酬改定保険医療機関管理システム¥9.35億×2件（競・99.0%）・医療機能情報提供制度全国統一システム¥6.58億（随・100%）等", amount_oku:41.39, tensyakuri:"🤖 未確認（R6では受注総額¥1,421億うち随意¥962億独占）"},
      {name:"株式会社日立製作所（含むJECC JV）", region:"③徴収・④労災", gyomu:"都道府県労働局LAN R4-R8¥26.25億（随・100%・JECC JV）・DPC DB管理運用¥7.15億（競・99.0%・1社応札）等", amount_oku:34.01, tensyakuri:"📋 デジタル庁R7でR5公表2人（元経産審議官→社長付・元総務省大臣官房付→公共システム事業部特別顧問）"},
      {name:"社会保険診療報酬支払基金", region:"一般会計（医療保険）", gyomu:"匿名医療保険等関連情報業務¥23.73億・データヘルス分析関連サービス¥7.51億等5件（全件100%随契）", amount_oku:32.27, tensyakuri:"🤖 未確認"},
      {name:"全国社会保険労務士会連合会", region:"⑤雇用勘定", gyomu:"中小企業働き方改革推進支援センター事業¥25.66億（競・90.2%）1件", amount_oku:25.66, tensyakuri:"🤖 未確認（社労士業界団体）"},
      {name:"長崎・広島の被爆者関係", region:"一般会計（被爆者援護法）", gyomu:"長崎市¥12.15億（第二種健康診断特例区域治療）・長崎県¥5.40億（在外被爆者支援）・長崎県¥3.03億・広島県¥2.33億・広島平和文化センター¥3.26億・長崎平和推進協会¥2.74億等", amount_oku:25.88, tensyakuri:"🤖 未確認（被爆者援護法に基づく継続事業）"},
      {name:"エヌ・ティ・ティ・コミュニケーションズ株式会社", region:"③徴収・④労災・①一般会計", gyomu:"次期厚労省LANシステム統合NW¥14.74億+¥7.78億（随・100%）・労働基準行政システムDRセンタ運用保守¥1.95億（随）等7件", amount_oku:23.52, tensyakuri:"🤖 未確認（厚労省統合NW全般を独占）"},
      {name:"鹿島建設株式会社東京土木支店", region:"一般会計（戦没者）", gyomu:"硫黄島における掘削調査一式¥10.09億（100%随契）1件", amount_oku:10.09, tensyakuri:"🤖 未確認"},
      {name:"一般社団法人日本戦没者遺骨収集推進協会", region:"一般会計（戦没者）", gyomu:"令和7年度戦没者の遺骨収集等事業¥9.94億（100%随契）1件", amount_oku:9.94, tensyakuri:"🤖 未確認"},
      {name:"福岡県社会保険医療協会", region:"④労災勘定（CO中毒）", gyomu:"三井三池炭鉱CO中毒患者特別対策事業¥4.94億（100%随契・60年継続）1件", amount_oku:4.94, tensyakuri:"🤖 未確認（歴史的特殊事業）"},
    ],
    houjin_note:"令和7年度・本省5系統公表14ファイル（PDF/Excel）を集計、≥¥1M案件のみ採録。合計約1,065件・¥1,724億。📋OB再就職情報はデジタル庁R7・総務省R7で確認済みの内閣人事局R5公表とのクロスを併記。厚労省契約への直接クロスは次フェーズで実施予定。出典：厚生労働省 随意契約・競争入札情報公表（令和7年度・25honsyo.html配下14ファイル）",
    accounts:[
      {name:"①一般会計（物品役務+公共工事）",amount_oku:1260.71,alert:true,
       note:"令和7年度・本省一般会計¥1,260.71億・867件（物品役務850件¥1,256.36億+公共工事17件¥4.35億）。東芝デジタルソリューションズ¥516.15億（厚労省LAN+介護保険DB）が圧倒的1位、三菱総合研究所¥50.13億（27件・コンサル独占）、アクセンチュア¥47.71億（G-MIS含む）、NTTデータ¥41.39億、日立¥34.01億。日本通運¥119.52億・KMバイオ¥47.30億・国立健康危機管理研究機構¥45.99億・社保支払基金¥32.27億の感染症/ワクチン/医療保険系も100%随契で大型集中。",
       contract:"競争入札598件¥852.18億+随意契約252件¥404.18億+公共工事競争12件・随契5件",
       src_key:"mhlw_r7_ippan",src_url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
      {name:"②年金特別会計（業務勘定）",amount_oku:41.51,alert:true,
       note:"令和7年度・本省年金特会業務勘定¥41.51億・9件（≥¥1M）。NEC「年金業務システム個人番号管理サブ更改」¥40.17億が単独で96.8%を占める。落札率58.6%・応札2者の総合評価競争入札だが、巨額。マイナンバー基盤運用を総務省R7（J-LIS¥55.34億）と並んでNECが独占。アイフォーコム¥9,631万（99.77%・1社）・日立社会情報¥2,873万（97.67%・1社）等の小型案件も大半が高落札率・1社応札。",
       contract:"競争入札9件＋随意契約（単価契約・全銀協/コンビニ/クレカモデル）",
       src_key:"mhlw_r7_nenkin",src_url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
      {name:"③労働保険特別会計（徴収勘定）",amount_oku:125,alert:true,
       note:"令和7年度・本省徴収勘定~¥125億・~59件。<strong>労働保険適用徴収システムの3社完全ロックイン：富士通¥69.36億+NTTデータ¥18.28億+日立¥26.25億（都道府県労働局LAN）=¥113.89億</strong>。R3年度に締結した5年「国債」契約の変更契約増額3件で¥87.64億。競争入札側でも富士通の機能改修4契約を全1社応札97-98%で取得（既設機器が富士通のため）。TOPPANエッジ7契約独占（労働保険料申告書印書）。担当：労働基準局 労働保険徴収課長 宿里明弘。",
       contract:"競争入札~45件+随意契約14件（変更契約増額が大半）",
       src_key:"mhlw_r7_roudou",src_url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
      {name:"④労働保険特別会計（労災勘定）",amount_oku:47,alert:true,
       note:"令和7年度・本省労災勘定~¥47億・~50件。三井三池炭鉱CO中毒患者特別対策事業（福岡県社会保険医療協会）¥4.94億の60年継続事業が最大の特殊案件。マーブル¥2.02億（時間外労働協定届PDF・99.8%・1社・不落随契）・NTTコム¥1.95億（労基行政システムDRセンタ運用保守延長）・広済堂ネクスト¥5.94億（厚労省ポータル3契約独占）。<strong>不落随契のオンパレード</strong>（一度入札にかけたが落札者が決まらず随契に切替が労災勘定で多数）。担当：労働基準局 労災管理課長 松永久→宮下雅行。",
       contract:"競争入札~30件+随意契約~20件（不落随契多数）",
       src_key:"mhlw_r7_rousai",src_url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
      {name:"⑤労働保険特別会計（雇用勘定）",amount_oku:250,alert:true,
       note:"令和7年度・本省雇用勘定~¥250億・~80件。<strong>47都道府県への「離職者等再就職訓練事業」全件100%随契~¥130億</strong>が圧倒的最大の構造的問題（東京都¥20.38億・兵庫¥13.51億・北海道¥9.06億等）。次にパソナ¥42.30億（キャリア形成リスキリング¥39.60億+中小企業育介推進¥2.70億）。全国社会保険労務士会連合会¥25.66億（中小企業働き方改革センター）・SBテクノロジー¥4.76億（job tag）・日本コンピュータシステム¥7.79億（職場情報サイト・女性活躍）。47県職業能力開発協会への「若年技能者人材育成支援」も全件「不落随契」99-100%で~¥15億。担当：職業安定局 雇用保険課長 岡英範。",
       contract:"競争入札~30件+随意契約~50件（47都道府県100%随契が中核）",
       src_key:"mhlw_r7_koyou",src_url:"https://www.mhlw.go.jp/sinsei/chotatu/zuii/25honsyo.html"},
    ]
  }'''

for f in FILES:
    if not f.exists():
        continue
    print(f"\n--- 処理中: {f.name} ---")
    content = f.read_text(encoding="utf-8")
    
    # 1. ソース定義の追加
    if "mhlw_r7_honsyo" in content:
        print(f"  既存ソース定義あり、スキップ")
    else:
        pattern = r'(mhlw_nenkin_r5: \{label:"📄 厚労省年金特別会計 随意契約公表（令和5年度）"[^}]+\},\n)'
        new_content = re.sub(pattern, r'\1' + NEW_SOURCES, content, count=1)
        if new_content == content:
            print(f"  ⚠ ソース定義アンカー未発見、スキップ")
        else:
            content = new_content
            print(f"  ✓ ソース定義6種類追加")
    
    # 2. MINISTRIES_2025 配列に厚労省カードを挿入
    if 'id:"mhlw", name:"厚生労働省", alert:true, tag:"5系統合計' in content:
        print(f"  既存カードあり、スキップ")
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
                insertion = ',\n' + MHLW_R7_CARD + '\n'
            else:
                insertion = '\n' + MHLW_R7_CARD + '\n'
            content = content[:close_pos] + insertion + content[close_pos:]
            print(f"  ✓ MINISTRIES_2025 に厚労省R7カード挿入（pos={close_pos}）")
        else:
            print(f"  ❌ MINISTRIES_2025 閉じ括弧未発見")
            continue
    
    f.write_text(content, encoding="utf-8")
    print(f"  ✓ 書き込み完了")

print("\n=== v16 反映完了 ===")
print("\n--- 検証コマンド ---")
print('grep -c "mhlw_r7_honsyo" /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html')
print('grep -c "5系統合計" /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html')
print('grep -c "東芝デジタルソリューションズ" /Volumes/SN0W8ALL/tokubetsu-kaikei/src/frontend/index.html')
