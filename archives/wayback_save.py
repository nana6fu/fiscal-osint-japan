#!/usr/bin/env python3
"""
Wayback Machine 一括保存スクリプト

Fiscal OSINT Japan の重要URLをWayback Machineに保存し、
保存先URLを対応表として記録する。

使い方:
    python3 wayback_save.py

出力:
    wayback_results.json  ... URL対応表
    wayback_results.txt   ... 人間可読サマリ

レート制限対策:
    - 5秒間隔で投げる
    - 429エラー(Too Many Requests)が出たら30秒待機
    - タイムアウトしたら次のURLへ（後で再実行可能）
"""
import requests
import time
import json
import sys
import os
from datetime import datetime

# ===== 保存対象URL =====
# 優先度1: 個人名カードの一次資料（最重要）
PRIORITY_1_URLS = [
    # 内閣官房 R5年度防衛省OB再就職PDF (10名の出典)
    "https://www.mod.go.jp/j/presiding/saishushoku/pdf/050401-060331.pdf",
    # R4年度（落合健→いであの出典）
    "https://www.mod.go.jp/j/presiding/saishushoku/pdf/040401-050331.pdf",
    # R6年度
    "https://www.mod.go.jp/j/presiding/saishushoku/pdf/060401-070331.pdf",
]

# 優先度2: 各地方防衛局の入札結果トップ
PRIORITY_2_URLS = [
    # 沖縄
    "https://www.mod.go.jp/rdb/okinawa/yosan-keiyaku/nyusatsu/index.html",
    # 北海道
    "https://www.mod.go.jp/rdb/hokkaido/nyuusatu/0103.html",
    # 北関東 工事
    "https://www.mod.go.jp/rdb/n-kanto/nyusatsu-keiyaku/nyusatsu-keiyaku.html",
    # 九州 工事_調達部
    "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_1kouji/index.html",
    # 九州 工事_管理部
    "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_3tabukouji/index.html",
    # 九州 業務_調達部
    "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_2gyoumu/index.html",
    # 九州 業務_企画部管理部
    "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_4tabugyoumu/index.html",
    # 九州 トップ
    "https://www.mod.go.jp/rdb/kyushu/contract/construction/index.html",
]

# 優先度3: 重要案件PDFのサンプル（最重要案件の証拠保全）
# - 築城ECI 2件
# - 佐世保(7)崎辺桟橋¥110.93億
# - 札幌・千歳ECI 2件 (北海道)
# - 下総・朝霞ECI 2件 (北関東)
PRIORITY_3_URLS = [
    # 九州 築城ECI（実URLは現状不明、サイトから手で取得した後追加）
    # "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_1kouji/pdf/k031_xxxx.pdf",
    # 後でMac側で追加可能
]

ALL_URLS = PRIORITY_1_URLS + PRIORITY_2_URLS + PRIORITY_3_URLS

SAVE_API = "https://web.archive.org/save/"
CHECK_API = "https://archive.org/wayback/available?url="
SLEEP_BETWEEN = 5.0
RETRY_WAIT_ON_429 = 30.0
TIMEOUT = 60
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Wayback save script for OSINT preservation)",
}


def save_url(url):
    """Wayback Machine Save Page Now にURLを送信
    
    Returns:
        (success: bool, wayback_url: str|None, message: str)
    """
    try:
        # Save Page Now (POST)
        r = requests.get(SAVE_API + url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        
        if r.status_code == 200:
            # 成功: Locationヘッダや本文から保存先URLを取得
            # Wayback responseの最終URLが /web/[timestamp]/[元URL] の形式
            final_url = r.url
            if '/web/' in final_url and '/web/save/' not in final_url:
                return True, final_url, "saved_new"
            else:
                # 既に保存済みなど
                return True, None, f"status_ok_no_redirect: {final_url[:100]}"
        elif r.status_code == 429:
            return False, None, "rate_limit_429"
        elif r.status_code in (502, 503, 504):
            return False, None, f"server_error_{r.status_code}"
        else:
            return False, None, f"http_{r.status_code}"
    except requests.exceptions.Timeout:
        return False, None, "timeout"
    except Exception as e:
        return False, None, f"exception: {e}"


def get_latest_snapshot(url):
    """Wayback Machine から最新スナップショットURLを取得"""
    try:
        r = requests.get(CHECK_API + url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            d = r.json()
            cs = d.get('archived_snapshots', {}).get('closest', {})
            if cs.get('available'):
                return cs.get('url')
        return None
    except Exception:
        return None


def main():
    print(f"=" * 70)
    print(f"Wayback Machine 一括保存スクリプト")
    print(f"対象URL数: {len(ALL_URLS)}")
    print(f"開始: {datetime.now().isoformat()}")
    print(f"=" * 70)

    results = []
    
    for i, url in enumerate(ALL_URLS, 1):
        print(f"\n[{i}/{len(ALL_URLS)}] {url[:80]}")
        
        # まず既存スナップショットを確認
        existing = get_latest_snapshot(url)
        if existing:
            print(f"  既存スナップショットあり: {existing[:100]}")
        
        # 保存実行
        print(f"  Save Page Now 実行中...")
        success, wayback_url, msg = save_url(url)
        
        if success:
            print(f"  ✓ {msg}")
            if wayback_url:
                print(f"  → {wayback_url[:100]}")
        else:
            print(f"  ✗ {msg}")
            if msg == "rate_limit_429":
                print(f"  → 30秒待機...")
                time.sleep(RETRY_WAIT_ON_429)
        
        # スリープしてから再度snapshot確認（保存が完了するまでの猶予）
        time.sleep(3)
        latest = get_latest_snapshot(url)
        
        results.append({
            "url": url,
            "save_success": success,
            "save_message": msg,
            "wayback_url_from_save": wayback_url,
            "wayback_url_latest": latest,
            "timestamp": datetime.now().isoformat(),
        })
        
        if i < len(ALL_URLS):
            time.sleep(SLEEP_BETWEEN)
    
    # 結果保存
    with open("wayback_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    with open("wayback_results.txt", "w", encoding="utf-8") as f:
        f.write(f"# Wayback Machine 保存結果\n")
        f.write(f"# 実行日時: {datetime.now().isoformat()}\n")
        f.write(f"# 合計: {len(ALL_URLS)} URLs\n\n")
        success_count = sum(1 for r in results if r['save_success'])
        latest_count = sum(1 for r in results if r['wayback_url_latest'])
        f.write(f"## サマリ\n")
        f.write(f"- 保存成功: {success_count}/{len(ALL_URLS)}\n")
        f.write(f"- Wayback最新スナップショット取得: {latest_count}/{len(ALL_URLS)}\n\n")
        f.write(f"## URL対応表\n\n")
        for r in results:
            f.write(f"### {r['url']}\n")
            f.write(f"- 保存結果: {'✓' if r['save_success'] else '✗'} ({r['save_message']})\n")
            if r['wayback_url_latest']:
                f.write(f"- Wayback URL: {r['wayback_url_latest']}\n")
            f.write(f"\n")

    print(f"\n{'=' * 70}")
    print(f"完了")
    print(f"  保存成功: {sum(1 for r in results if r['save_success'])}/{len(ALL_URLS)}")
    print(f"  Wayback最新取得: {sum(1 for r in results if r['wayback_url_latest'])}/{len(ALL_URLS)}")
    print(f"  結果ファイル: wayback_results.json / wayback_results.txt")
    print(f"=" * 70)


if __name__ == "__main__":
    main()
