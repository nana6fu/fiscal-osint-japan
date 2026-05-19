#!/usr/bin/env python3
"""D案 v18: 企業横串ランキングセクションをHTMLに追加（R7主要4省庁・IT系）"""
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
        shutil.copy(f, str(f) + f".bak_v18_{ts}")
        print(f"✓ バックアップ: {f.name}.bak_v18_{ts}")

# === 追加するスクリプトブロック（データ + レンダリング + 自動実行） ===
INJECTION = r'''
<!-- ===== D案 v18: 企業横串ランキング R7 ===== -->
<script id="cross-companies-script">
var CROSS_COMPANIES_R7 = {
  it_individual: [
    {name:"日本電気株式会社（NEC）", total_oku:697.34, ministry_count:4,
     ministries:[
       {name:"デジタル庁", oku:552.9, gyomu:"GSS運用一式¥231億・国税庁等GSS移行端末¥171.6億等"},
       {name:"総務省", oku:65.7, gyomu:"電波監視NEC・関東総合通信局R7等"},
       {name:"厚生労働省", oku:46.1, gyomu:"統計・LAN関連等"},
       {name:"財務省", oku:32.7, gyomu:"財務省行政情報化LAN¥29.01億・行政LAN端末¥2.44億等"}
     ], alert:true, note:"4省庁全制覇・最強の構造的存在。R5公表5人がNECに集中再就職"},
    {name:"東芝デジタルソリューションズ株式会社", total_oku:516.15, ministry_count:1,
     ministries:[{name:"厚生労働省", oku:516.15, gyomu:"厚労省LANシステム47都道府県100%随契¥482億等"}],
     alert:true, note:"厚労省LAN単独独占"},
    {name:"株式会社NTTデータ", total_oku:402.04, ministry_count:3,
     ministries:[
       {name:"デジタル庁", oku:166.3, gyomu:"第二期政府共通プラットフォーム等"},
       {name:"厚生労働省", oku:41.4, gyomu:"労保徴収システムOCR等"},
       {name:"財務省", oku:194.3, gyomu:"官庁会計システム（ADAMS）¥133.9億・運用保守¥33億等"}
     ], alert:true, note:"財務省官庁会計の心臓部を独占"},
    {name:"富士通株式会社", total_oku:322.63, ministry_count:4,
     ministries:[
       {name:"デジタル庁", oku:32.2, gyomu:"GSS関連・東京センチュリーJV"},
       {name:"総務省", oku:16.8, gyomu:"総務省統計関連等"},
       {name:"厚生労働省", oku:74.2, gyomu:"厚労省システム¥74億等"},
       {name:"財務省", oku:199.5, gyomu:"予算編成支援システム8次¥80億・財務省理財局更改¥40億等26件"}
     ], alert:true, note:"4省庁全制覇・財務省ITインフラ完全ロックイン"},
    {name:"NTT東日本", total_oku:149.70, ministry_count:1,
     ministries:[{name:"デジタル庁", oku:149.70, gyomu:"GSS関連¥145億等"}], alert:false, note:""},
    {name:"KDDI株式会社", total_oku:144.50, ministry_count:2,
     ministries:[
       {name:"デジタル庁", oku:141.6, gyomu:"GSS関連¥141億等"},
       {name:"財務省", oku:2.9, gyomu:"財務省理財局情報システム通信回線等6件"}
     ], alert:false, note:""},
    {name:"アクセンチュア株式会社", total_oku:87.41, ministry_count:2,
     ministries:[
       {name:"デジタル庁", oku:39.7, gyomu:"GSS関連等"},
       {name:"厚生労働省", oku:47.7, gyomu:"厚労省関連¥48億等"}
     ], alert:true, note:"⚠ R6で4ヶ月指名停止歴あり（無断再委託）、要追跡"},
    {name:"日本マイクロソフト株式会社", total_oku:79.30, ministry_count:1,
     ministries:[{name:"デジタル庁", oku:79.30, gyomu:"クラウド・ライセンス関連"}], alert:false, note:""},
    {name:"株式会社三菱総合研究所", total_oku:72.90, ministry_count:2,
     ministries:[
       {name:"総務省", oku:22.8, gyomu:"政策調査関連"},
       {name:"厚生労働省", oku:50.1, gyomu:"年金・統計調査関連¥50億"}
     ], alert:false, note:""},
    {name:"NECフィールディング株式会社", total_oku:67.60, ministry_count:1,
     ministries:[{name:"デジタル庁", oku:67.60, gyomu:"NEC子会社・GSS関連保守"}],
     alert:false, note:"NEC本体と合わせるとNEC関連¥765億"},
    {name:"株式会社日立製作所", total_oku:54.01, ministry_count:2,
     ministries:[
       {name:"デジタル庁", oku:20.0, gyomu:"GSS関連・JECC JV含む"},
       {name:"厚生労働省", oku:34.0, gyomu:"厚労省関連システム"}
     ], alert:false, note:""},
    {name:"日本アイ・ビー・エム株式会社", total_oku:39.82, ministry_count:1,
     ministries:[{name:"総務省", oku:39.82, gyomu:"統計・データ関連"}], alert:false, note:""}
  ],
  groups: [
    {name:"NEC関連グループ", total_oku:764.94,
     parts:[{n:"日本電気株式会社", oku:697.34}, {n:"NECフィールディング株式会社", oku:67.60}],
     note:"NEC本体（4省庁全部）+ NECフィールディング（デジタル庁子会社）。R7主要4省庁の17%。"},
    {name:"NTTグループ", total_oku:575.26,
     parts:[{n:"株式会社NTTデータ", oku:402.04}, {n:"NTT東日本", oku:149.70}, {n:"NTTコミュニケーションズ", oku:23.52}],
     note:"NTTデータ+東日本+コミュニケーションズ。デジタル庁・厚労省・財務省にまたがる。"},
    {name:"富士通グループ", total_oku:340.63,
     parts:[{n:"富士通株式会社", oku:322.63}, {n:"富士通ネットワークソリューションズ", oku:18.00}],
     note:"本体（4省庁全制覇）+ ネットワーク子会社。"}
  ],
  totals: {ministries_total:4504, top4_it:1938.16, top4_pct:43.0, top7_it:2206.95, top7_pct:49.0}
};

function renderCrossCompanies() {
  var sec = document.getElementById('cross-companies-section');
  if (!sec) return;
  // 年度がR7（2025）のときだけ表示
  var yearSelect = document.querySelector('select');
  var year = yearSelect && yearSelect.value ? parseInt(yearSelect.value) : 2025;
  if (year !== 2025) { sec.style.display = 'none'; return; }
  sec.style.display = 'block';

  var d = CROSS_COMPANIES_R7;
  var h = '';
  h += '<div style="background:rgba(255,90,90,0.08);border:1px solid #c44;border-radius:8px;padding:20px 24px;margin-top:36px;">';
  h += '<h2 style="color:#ff8080;font-size:22px;margin:0 0 6px 0;">🏢 企業横串ランキング（R7主要4省庁・IT系）</h2>';
  h += '<div style="color:#bbb;font-size:13px;margin-bottom:18px;line-height:1.6;">省庁ごとに見えなかった「単一企業の総受注額」を横串で集計。デジタル庁・総務省・厚労省・財務省の合計¥' + d.totals.ministries_total + '億のうち、<strong style="color:#ffd966;">IT上位7社で¥' + d.totals.top7_it.toFixed(0) + '億（' + d.totals.top7_pct + '%）</strong>を占める構造。</div>';
  
  h += '<h3 style="color:#ffcc66;font-size:15px;margin:20px 0 8px 0;">▼ 個別企業 Top 12（IT省庁横断）</h3>';
  h += '<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:13px;min-width:760px;">';
  h += '<tr style="border-bottom:2px solid #555;color:#aaa;"><th style="padding:8px 6px;text-align:left;">#</th><th style="padding:8px 6px;text-align:left;">企業名</th><th style="padding:8px 6px;text-align:right;">合計</th><th style="padding:8px 6px;text-align:center;">省庁数</th><th style="padding:8px 6px;text-align:left;">内訳</th></tr>';
  d.it_individual.forEach(function(c, i){
    var rowBg = c.alert ? 'background:rgba(255,80,80,0.05);' : '';
    var nc = c.alert ? '#ff9999' : '#fff';
    var ac = c.alert ? '#ff8888' : '#9cdf9c';
    var brk = c.ministries.map(function(m){
      return '<span style="color:#7ec8ff;">' + m.name + '</span><span style="color:#888;"> ¥' + m.oku.toFixed(1) + '</span>';
    }).join(' / ');
    var nh = c.note ? '<div style="color:#ffaa66;font-size:11px;margin-top:3px;line-height:1.4;">' + c.note + '</div>' : '';
    h += '<tr style="border-bottom:1px solid #333;' + rowBg + '">';
    h += '<td style="padding:9px 6px;color:#888;vertical-align:top;">' + (i+1) + '</td>';
    h += '<td style="padding:9px 6px;color:' + nc + ';font-weight:600;vertical-align:top;">' + c.name + nh + '</td>';
    h += '<td style="padding:9px 6px;text-align:right;color:' + ac + ';font-weight:700;vertical-align:top;white-space:nowrap;">¥' + c.total_oku.toFixed(2) + '億</td>';
    var mcColor = c.ministry_count === 4 ? '#ff8888' : '#bbb';
    var mcLabel = c.ministry_count === 4 ? c.ministry_count + ' 🔥全' : c.ministry_count;
    h += '<td style="padding:9px 6px;text-align:center;color:' + mcColor + ';vertical-align:top;font-weight:600;">' + mcLabel + '</td>';
    h += '<td style="padding:9px 6px;color:#aaa;font-size:12px;vertical-align:top;line-height:1.6;">' + brk + '</td></tr>';
  });
  h += '</table></div>';

  h += '<h3 style="color:#ffcc66;font-size:15px;margin:28px 0 10px 0;">▼ 企業グループ合算ハイライト</h3>';
  h += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;">';
  d.groups.forEach(function(g){
    h += '<div style="background:rgba(255,140,80,0.08);border:1px solid #864;border-radius:6px;padding:14px;">';
    h += '<div style="color:#ffaa66;font-size:14px;font-weight:700;">' + g.name + '</div>';
    h += '<div style="color:#ffcccc;font-size:26px;font-weight:800;margin:6px 0;">¥' + g.total_oku.toFixed(2) + '億</div>';
    g.parts.forEach(function(p){
      h += '<div style="color:#bbb;font-size:11px;margin:2px 0;">・' + p.n + '：¥' + p.oku.toFixed(2) + '億</div>';
    });
    h += '<div style="color:#999;font-size:11px;margin-top:8px;border-top:1px solid #555;padding-top:6px;line-height:1.5;">' + g.note + '</div>';
    h += '</div>';
  });
  h += '</div>';

  h += '<div style="margin-top:18px;padding:12px 14px;background:rgba(100,100,100,0.1);border-radius:6px;color:#999;font-size:12px;line-height:1.6;">';
  h += '⚠ <strong>注記</strong>：本ランキングはR7主要4省庁（デジタル庁・総務省・厚労省・財務省）の主要受注企業（houjin採録基準）を集計。';
  h += '小規模業者は含まないため合計¥3,606億（4省庁houjin合算）は省庁合算¥4,504億の約80%カバー。';
  h += '<br>⚠ <strong>防衛省（地方防衛局9局・¥7,906億）は別カテゴリ「ゼネコン横串」として後日追加予定</strong>（IT系と建設系で性質が異なるため分離）。';
  h += '<br>⚠ 法人番号での名寄せはhoujinデータに法人番号が含まれていないため未実施。表記揺れ（NTTデータ全角/半角・富士通JV等）は手動統合。';
  h += '</div></div>';
  sec.innerHTML = h;
}

document.addEventListener('DOMContentLoaded', function(){
  renderCrossCompanies();
  // 年度切替時にも再描画（既存セレクトの change を監視）
  var sel = document.querySelector('select');
  if (sel) sel.addEventListener('change', renderCrossCompanies);
});
</script>
<!-- ===== D案 v18 end ===== -->
'''

# DOM要素（セクション本体）
SECTION_HTML = '\n<section id="cross-companies-section" style="max-width:1400px;margin:0 auto;padding:0 20px;"></section>\n'

for f in FILES:
    if not f.exists(): continue
    print(f"\n--- 処理中: {f.name} ---")
    content = f.read_text(encoding="utf-8")
    
    # 重複チェック
    if 'CROSS_COMPANIES_R7' in content:
        print(f"  既存 CROSS_COMPANIES_R7 あり、削除して再注入")
        # 古いブロックを削除
        content = re.sub(
            r'<!-- ===== D案 v18:.*?<!-- ===== D案 v18 end ===== -->',
            '', content, flags=re.DOTALL)
        # 古いセクションも削除
        content = re.sub(
            r'\n?<section id="cross-companies-section"[^>]*></section>\n?',
            '\n', content)
    
    # セクションを </body> の直前に挿入
    if '</body>' in content:
        content = content.replace('</body>', SECTION_HTML + INJECTION + '\n</body>', 1)
        print(f"  ✓ セクション + スクリプト挿入（</body>の直前）")
    else:
        # </body> がない場合は末尾に追加
        content += SECTION_HTML + INJECTION
        print(f"  ✓ ファイル末尾に追加（</body>未発見）")
    
    f.write_text(content, encoding="utf-8")
    print(f"  ✓ 書き込み完了")

# 検証
print("\n=== 検証 ===")
for f in FILES:
    if not f.exists(): continue
    c = f.read_text(encoding="utf-8")
    print(f"[{f.name}]")
    print(f"  CROSS_COMPANIES_R7: {c.count('CROSS_COMPANIES_R7')}")
    print(f"  企業横串ランキング: {c.count('企業横串ランキング')}")
    print(f"  cross-companies-section: {c.count('cross-companies-section')}")
