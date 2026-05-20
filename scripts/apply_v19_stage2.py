#!/usr/bin/env python3
"""v19: Stage 2 Phase 1 - OB配置×受注推移セクションをHTMLに追加"""
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
        shutil.copy(f, str(f) + f".bak_v19_{ts}")
        print(f"✓ バックアップ: {f.name}.bak_v19_{ts}")

INJECTION = r'''
<!-- ===== Stage 2 Phase 1: OB配置×受注推移 ===== -->
<script id="stage2-script">
var STAGE2_DATA = {
  obs_timeline: [
    {date:"2023-02-21", name:"落合健", prev:"元海上自衛隊幹部候補生学校副校長", company:"いであ株式会社", pos:"主任研究員", pdf:"R4再就職届(P7 #78)"},
    {date:"2023-06-01", name:"坪倉幹男", prev:"元北関東防衛局企画部長", company:"株式会社オオバ", pos:"顧問", pdf:"R5再就職届(P16 #75)"},
    {date:"2023-11-01", name:"石倉三良", prev:"元北海道防衛局長", company:"東洋建設株式会社", pos:"常務理事", pdf:"R5再就職届(P17 #90)"}
  ],
  companies: [
    {
      id:"toyo", name:"東洋建設株式会社", color:"#ff8a65", color_dim:"#a55244",
      ob_name:"石倉三良", ob_role:"元北海道防衛局長", ob_pos:"常務理事", ob_date:"2023-11-01",
      years: {
        R5: {cases:0, oku:0, details:[]},
        R6: {cases:2, oku:18.00, details:[
          {bureau:"九州", oku:17.60, rate:99.8, kind:"随意契約", project:"東洋建設(株) 単独受注"},
          {bureau:"近畿中部", oku:0.40, rate:99.5, kind:"JV参加", project:"伊丹（６）技術協力業務"}
        ]},
        R7: {cases:5, oku:346.27, details:[
          {bureau:"沖縄", oku:235.40, rate:null, kind:"JV競争入札", project:"シュワブ（Ｒ７）造成工事（２工区）大林組JV", highlight:"辺野古関連"},
          {bureau:"沖縄", oku:41.52, rate:null, kind:"JV競争入札", project:"シュワブ（Ｒ７）地盤改良工事 安藤・間JV", highlight:"辺野古関連"},
          {bureau:"九州", oku:39.00, rate:92.5, kind:"JV競争入札", project:"東洋建設・松山建設特定JV"},
          {bureau:"九州", oku:30.35, rate:93.4, kind:"JV競争入札", project:"東洋建設・不動テトラ・梅村組JV"}
        ]}
      }
    },
    {
      id:"idea", name:"いであ株式会社", color:"#81c784", color_dim:"#3d6b41",
      ob_name:"落合健", ob_role:"元海上自衛隊副校長", ob_pos:"主任研究員", ob_date:"2023-02-21",
      years: {
        R5: {cases:0, oku:0, details:[]},
        R6: {cases:6, oku:29.25, details:[
          {bureau:"沖縄", oku:14.79, rate:88.0, kind:"競争+プロポ", project:"いであ沖縄支社（5件・空自那覇土質調査ほか）"},
          {bureau:"沖縄", oku:14.46, rate:99.9, kind:"プロポーザル", project:"シュワブ（Ｒ６）水域生物等調査", highlight:"辺野古関連"}
        ]},
        R7: {cases:3, oku:32.57, details:[
          {bureau:"沖縄", oku:32.57, rate:null, kind:"プロポーザル", project:"シュワブ（Ｒ７）水域生物等調査ほか3件", highlight:"辺野古関連"}
        ]}
      }
    },
    {
      id:"ooba", name:"株式会社オオバ", color:"#64b5f6", color_dim:"#3a6c93",
      ob_name:"坪倉幹男", ob_role:"元北関東防衛局企画部長", ob_pos:"顧問", ob_date:"2023-06-01",
      years: {
        R5: {cases:1, oku:21.78, details:[
          {bureau:"近畿中部", oku:21.78, rate:null, kind:"プロポJV", project:"小牧外(７)施設最適化JV参加"}
        ]},
        R6: {cases:3, oku:58.26, details:[
          {bureau:"沖縄", oku:24.78, rate:99.9, kind:"JV", project:"シュワブ（Ｒ６）総括事業監理（その２）", highlight:"辺野古関連"},
          {bureau:"北関東", oku:18.81, rate:99.6, kind:"JV", project:"朝霞（６）施設最適化（OB元職場）", highlight:"OB元職場！"},
          {bureau:"北海道", oku:14.67, rate:99.7, kind:"JV", project:"札幌（６）施設最適化"}
        ]},
        R7: {cases:1, oku:14.19, details:[
          {bureau:"北関東", oku:14.19, rate:98.6, kind:"競争入札JV", project:"アジア・パシフィック・オオバ・内藤建築共同体", highlight:"OB元職場継続"}
        ]}
      }
    }
  ],
  totals: {R5: 21.78, R6: 105.51, R7: 393.03},
  confounding_factors: [
    "防衛省ECI随契の「設計→技術協力→工事」二段構造そのものが、R5に設計、R6/R7に工事が出るパターンを作る可能性",
    "辺野古（沖縄シュワブ）・馬毛島など地政学的大型新規発注はOB効果と独立した要因",
    "能登半島地震復興需要（R6）による建設業界全体の伸び",
    "防衛予算全体の伸び（R7で大幅増額）",
    "ECI随契方式の拡大による特定企業集中",
    "R7沖縄案件の落札率0.0% = 予定価格非公表（一般競争入札・WTO特例の特性）"
  ]
};

function renderStage2() {
  var sec = document.getElementById('stage2-ob-revenue-section');
  if (!sec) return;
  var yearSelect = document.querySelector('select');
  var year = yearSelect && yearSelect.value ? parseInt(yearSelect.value) : 2025;
  if (year !== 2025) { sec.style.display = 'none'; return; }
  sec.style.display = 'block';

  var d = STAGE2_DATA;
  
  // 全体最大値（棒グラフのスケール計算用）
  var allMax = 0;
  d.companies.forEach(function(c){
    ["R5","R6","R7"].forEach(function(y){
      if (c.years[y].oku > allMax) allMax = c.years[y].oku;
    });
  });
  if (d.totals.R7 > allMax) allMax = d.totals.R7;
  
  function bar(oku, color, maxVal) {
    var pct = maxVal > 0 ? (oku / maxVal * 100) : 0;
    var w = Math.max(pct, 0.5);  // 0でも見えるように
    return '<div style="background:' + color + ';height:18px;width:' + w + '%;border-radius:3px;display:inline-block;vertical-align:middle;min-width:2px;"></div>';
  }
  
  var h = '';
  h += '<div style="background:rgba(120,180,220,0.06);border:1px solid #4a7090;border-radius:8px;padding:22px 26px;margin-top:36px;">';
  
  // ヘッダー
  h += '<h2 style="color:#7ec8ff;font-size:22px;margin:0 0 4px 0;">📊 OB配置 × 受注推移（Stage 2 Phase 1：防衛省系3社）</h2>';
  h += '<div style="color:#bbb;font-size:13px;margin-bottom:16px;line-height:1.6;">公表された再就職届と公共調達データの組み合わせを時系列で可視化。<strong style="color:#ffcc66;">相関の可視化であり、因果関係は主張しません</strong>。交絡要因を末尾に明示。</div>';
  
  // OB入社タイムライン
  h += '<div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:14px 18px;margin-bottom:20px;">';
  h += '<div style="color:#ffcc66;font-size:14px;font-weight:600;margin-bottom:8px;">▼ OB入社タイムライン（一次資料：防衛省再就職届公表PDF）</div>';
  d.obs_timeline.forEach(function(ob){
    h += '<div style="font-size:13px;color:#ddd;margin:5px 0;">';
    h += '<span style="color:#7ec8ff;font-weight:600;">' + ob.date + '</span> ';
    h += '<span style="color:#ff9999;">' + ob.name + '</span> ';
    h += '<span style="color:#aaa;">（' + ob.prev + '）</span>';
    h += '<span style="color:#999;"> → </span>';
    h += '<span style="color:#fff;">' + ob.company + ' ' + ob.pos + '</span> ';
    h += '<span style="color:#666;font-size:11px;">[' + ob.pdf + ']</span>';
    h += '</div>';
  });
  h += '</div>';
  
  // 3社合計の年度別棒グラフ
  h += '<div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:14px 18px;margin-bottom:20px;">';
  h += '<div style="color:#ffcc66;font-size:14px;font-weight:600;margin-bottom:12px;">▼ 3社合計：防衛省地方防衛局からの受注推移</div>';
  ["R5","R6","R7"].forEach(function(y){
    var oku = d.totals[y];
    var label_year = {R5:"R5 (2023)", R6:"R6 (2024)", R7:"R7 (2025)"}[y];
    var label_note = {R5:"OB入社年度（途中）", R6:"入社後1年目（フル稼働）", R7:"入社後2年目"}[y];
    h += '<div style="margin:6px 0;display:flex;align-items:center;gap:10px;font-size:13px;">';
    h += '<div style="width:120px;color:#ddd;"><strong>' + label_year + '</strong></div>';
    h += '<div style="flex:1;">' + bar(oku, "#ff9966", allMax) + '</div>';
    h += '<div style="width:90px;text-align:right;color:#ff9966;font-weight:700;">¥' + oku.toFixed(2) + '億</div>';
    h += '<div style="width:180px;color:#888;font-size:11px;">' + label_note + '</div>';
    h += '</div>';
  });
  var ratio = d.totals.R5 > 0 ? (d.totals.R7 / d.totals.R5).toFixed(1) : '—';
  h += '<div style="color:#ffcc66;font-size:14px;font-weight:700;margin-top:10px;text-align:center;">R5→R7 で <span style="color:#ff8888;font-size:18px;">' + ratio + '倍</span>（¥' + d.totals.R5.toFixed(0) + '億 → ¥' + d.totals.R7.toFixed(0) + '億）</div>';
  h += '</div>';
  
  // 各社カード
  h += '<div style="color:#ffcc66;font-size:14px;font-weight:600;margin:20px 0 10px 0;">▼ 企業別の3年比較</div>';
  h += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px;">';
  
  d.companies.forEach(function(c){
    h += '<div style="background:rgba(0,0,0,0.3);border:1px solid ' + c.color_dim + ';border-radius:6px;padding:14px;">';
    h += '<div style="color:' + c.color + ';font-size:15px;font-weight:700;margin-bottom:4px;">' + c.name + '</div>';
    h += '<div style="color:#aaa;font-size:11px;margin-bottom:10px;">';
    h += '<span style="color:#ff9999;">' + c.ob_name + '</span>（' + c.ob_role + '）→ ' + c.ob_pos + '　<span style="color:#7ec8ff;">' + c.ob_date + '</span> 入社';
    h += '</div>';
    
    // 各年度の棒グラフ
    ["R5","R6","R7"].forEach(function(y){
      var oku = c.years[y].oku;
      var cases = c.years[y].cases;
      var bg = (y === "R5") ? c.color_dim : c.color;
      h += '<div style="margin:5px 0;display:flex;align-items:center;gap:8px;font-size:12px;">';
      h += '<div style="width:30px;color:#ddd;font-weight:600;">' + y + '</div>';
      h += '<div style="flex:1;">' + bar(oku, bg, allMax) + '</div>';
      h += '<div style="width:80px;text-align:right;color:' + c.color + ';font-weight:700;font-size:12px;">¥' + oku.toFixed(2) + '億</div>';
      h += '<div style="width:42px;text-align:right;color:#888;font-size:11px;">' + cases + '件</div>';
      h += '</div>';
    });
    
    // 局別詳細（展開済み）
    h += '<details style="margin-top:10px;"><summary style="cursor:pointer;color:#999;font-size:11px;">▶ 局別詳細を表示（' + (c.years.R5.details.length + c.years.R6.details.length + c.years.R7.details.length) + '件）</summary>';
    ["R5","R6","R7"].forEach(function(y){
      if (c.years[y].details.length === 0) return;
      c.years[y].details.forEach(function(det){
        var rateStr = det.rate === null ? "非公表" : det.rate.toFixed(1) + "%";
        var rateColor = det.rate === null ? "#aaa" : (det.rate >= 99 ? "#ff8888" : "#bbb");
        h += '<div style="font-size:11px;color:#aaa;margin:4px 0;padding:5px 8px;background:rgba(255,255,255,0.03);border-left:2px solid ' + c.color_dim + ';">';
        h += '<span style="color:#7ec8ff;font-weight:600;">' + y + '</span> ';
        h += '<span style="color:#ddd;">' + det.bureau + '</span> ';
        h += '<span style="color:' + c.color + ';font-weight:600;">¥' + det.oku.toFixed(2) + '億</span> ';
        h += '<span style="color:' + rateColor + ';">(' + rateStr + ')</span> ';
        h += '<span style="color:#888;">[' + det.kind + ']</span>';
        if (det.highlight) {
          h += '<span style="color:#ff9966;font-weight:600;margin-left:5px;">🔥 ' + det.highlight + '</span>';
        }
        h += '<div style="color:#999;font-size:10px;margin-top:2px;">' + det.project + '</div>';
        h += '</div>';
      });
    });
    h += '</details>';
    h += '</div>';
  });
  h += '</div>';
  
  // 交絡要因の明示
  h += '<div style="margin-top:24px;padding:14px 18px;background:rgba(180,140,80,0.08);border:1px solid #864;border-radius:6px;">';
  h += '<div style="color:#ffaa66;font-size:13px;font-weight:700;margin-bottom:8px;">⚠ 検証が必要な交絡要因（因果関係を主張しないために）</div>';
  h += '<ul style="margin:0;padding-left:22px;color:#ccc;font-size:12px;line-height:1.7;">';
  d.confounding_factors.forEach(function(f){
    h += '<li>' + f + '</li>';
  });
  h += '</ul>';
  h += '</div>';
  
  // 一次資料リンク
  h += '<div style="margin-top:14px;padding:10px 14px;background:rgba(100,100,100,0.1);border-radius:6px;color:#999;font-size:11px;line-height:1.6;">';
  h += '📄 <strong>一次資料</strong>：<a href="https://www.mod.go.jp/j/profile/employ/saisyusyoku/index.html" target="_blank" style="color:#7ec8ff;">防衛省 自衛隊員の再就職状況の公表</a>（R4/R5/R6 全件スキャン済み）　/　各地方防衛局 入札契約情報';
  h += '<br>📊 <strong>Stage 2 Phase 1</strong>：防衛省系3社のサンプル分析。Phase 2では NEC・東芝・他IT系企業へ拡張予定（同ページ R4 PDF P7 で発見：井上剛→NEC、河野順一→東芝インフラシステムズ）';
  h += '</div>';
  
  h += '</div>';
  sec.innerHTML = h;
}

document.addEventListener('DOMContentLoaded', function(){
  renderStage2();
  var sel = document.querySelector('select');
  if (sel) sel.addEventListener('change', renderStage2);
});
</script>
<!-- ===== Stage 2 Phase 1 end ===== -->
'''

SECTION_HTML = '\n<section id="stage2-ob-revenue-section" style="max-width:1400px;margin:0 auto;padding:0 20px;"></section>\n'

for f in FILES:
    if not f.exists(): continue
    print(f"\n--- 処理中: {f.name} ---")
    content = f.read_text(encoding="utf-8")
    
    # 重複削除
    if 'STAGE2_DATA' in content:
        print(f"  既存 STAGE2_DATA あり、削除して再注入")
        content = re.sub(
            r'<!-- ===== Stage 2 Phase 1:.*?<!-- ===== Stage 2 Phase 1 end ===== -->',
            '', content, flags=re.DOTALL)
        content = re.sub(
            r'\n?<section id="stage2-ob-revenue-section"[^>]*></section>\n?',
            '\n', content)
    
    # </body> の直前（v18 cross-companies-section の後ろ）に挿入
    if '</body>' in content:
        content = content.replace('</body>', SECTION_HTML + INJECTION + '\n</body>', 1)
        print(f"  ✓ Stage2セクション + スクリプト挿入完了")
    else:
        content += SECTION_HTML + INJECTION
    
    f.write_text(content, encoding="utf-8")
    print(f"  ✓ 書き込み完了")

print("\n=== 検証 ===")
for f in FILES:
    if not f.exists(): continue
    c = f.read_text(encoding="utf-8")
    print(f"[{f.name}]")
    print(f"  STAGE2_DATA: {c.count('STAGE2_DATA')}")
    print(f"  stage2-ob-revenue-section: {c.count('stage2-ob-revenue-section')}")
    print(f"  落合健: {c.count('落合健')}")
    print(f"  18倍 / R5→R7: {c.count('R5→R7') if 'R5→R7' in c else c.count('R5\\u2192R7')}")

print("\n✓ v19 完了。ブラウザ確認:")
print("  open /Volumes/SN0W8ALL/tokubetsu-kaikei/index.html")
