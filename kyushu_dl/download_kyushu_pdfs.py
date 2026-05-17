#!/usr/bin/env python3
"""
九州防衛局 令和7年度 発注実績PDFを一括ダウンロード

九州は組織が複雑で4ソース:
- 調達部 工事 (kekka2025_1kouji): 77件
- 管理部 工事 (kekka2025_3tabukouji): 18件
- 調達部 業務 (kekka2025_2gyoumu): 141件
- 企画部・管理部 業務 (kekka2025_4tabugyoumu): 16件
計 252件

使い方:
    python3 download_kyushu_pdfs.py

出力:
    ./kyushu_r7_pdfs/工事_調達部/*.pdf
    ./kyushu_r7_pdfs/工事_管理部/*.pdf
    ./kyushu_r7_pdfs/業務_調達部/*.pdf
    ./kyushu_r7_pdfs/業務_企画部管理部/*.pdf
    ./kyushu_r7_pdfs/_index.txt
"""
import os
import time
import re
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 4ソース
SOURCES = [
    {
        "category": "工事_調達部",
        "url": "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_1kouji/index.html",
        "expected_count": 77,
    },
    {
        "category": "工事_管理部",
        "url": "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_3tabukouji/index.html",
        "expected_count": 18,
    },
    {
        "category": "業務_調達部",
        "url": "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_2gyoumu/index.html",
        "expected_count": 141,
    },
    {
        "category": "業務_企画部管理部",
        "url": "https://www.mod.go.jp/rdb/kyushu/contract/construction/kyushu/kekka2025_4tabugyoumu/index.html",
        "expected_count": 16,
    },
]

OUTPUT_DIR = "./kyushu_r7_pdfs"
SLEEP_SEC = 1.2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}


def safe_filename(s, maxlen=120):
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', s)
    s = re.sub(r'\s+', '_', s)
    s = s.strip('._-')
    return s[:maxlen] if s else "unnamed"


def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    for enc in ('shift_jis', 'cp932', 'utf-8'):
        try:
            return r.content.decode(enc), enc
        except UnicodeDecodeError:
            continue
    r.encoding = r.apparent_encoding
    return r.text, r.encoding


def extract_pdf_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    seen = set()
    pdf_links = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue
        if '.pdf' not in href.lower():
            continue
        abs_url = urllib.parse.urljoin(base_url, href)
        if abs_url in seen:
            continue
        seen.add(abs_url)

        title = a.get_text(strip=True)
        if not title:
            title = os.path.basename(urllib.parse.urlparse(href).path)

        pdf_links.append((title, abs_url))

    return pdf_links


def download_pdf(url, save_path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        size = os.path.getsize(save_path)
        return True, size
    except Exception as e:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        return False, str(e)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    index_lines = []
    overall_summary = []

    for src in SOURCES:
        category = src["category"]
        base_url = src["url"]
        expected = src["expected_count"]

        print(f"\n{'=' * 70}")
        print(f"【{category}】 期待件数: {expected}")
        print(f"  URL: {base_url}")
        print('=' * 70)

        cat_dir = os.path.join(OUTPUT_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)

        print("目次HTML取得中...")
        try:
            html, used_enc = fetch_html(base_url)
            print(f"  エンコーディング: {used_enc}")
        except Exception as e:
            print(f"  ✗ HTML取得失敗: {e}")
            continue

        pdf_links = extract_pdf_links(html, base_url)
        print(f"  PDFリンク発見: {len(pdf_links)}件 (期待: {expected})")

        if not pdf_links:
            debug_path = os.path.join(OUTPUT_DIR, f"_debug_{category}.htm")
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  → {debug_path} に保存（構造確認用）")
            continue

        success = 0
        failure = 0
        for i, (title, url) in enumerate(pdf_links, 1):
            filename = f"{i:03d}_{safe_filename(title)}.pdf"
            save_path = os.path.join(cat_dir, filename)
            index_lines.append(f"[{category}] {i:03d}\t{filename}\t{title}\t{url}")

            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                print(f"  [{i:3d}/{len(pdf_links)}] skip (既存): {filename[:60]}")
                success += 1
                continue

            print(f"  [{i:3d}/{len(pdf_links)}] DL: {filename[:60]}...", end=' ', flush=True)
            ok, info = download_pdf(url, save_path)
            if ok:
                print(f"OK ({info:,}B)")
                success += 1
            else:
                print(f"NG ({info})")
                failure += 1
            time.sleep(SLEEP_SEC)

        overall_summary.append((category, success, failure, len(pdf_links)))

    if index_lines:
        index_path = os.path.join(OUTPUT_DIR, "_index.txt")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("カテゴリ\t連番\tファイル名\t案件名\tURL\n")
            f.write('\n'.join(index_lines))
        print(f"\n→ 対応表: {index_path}")

    print(f"\n{'=' * 70}")
    print("ダウンロード結果サマリ")
    print('=' * 70)
    grand_total = 0
    grand_success = 0
    for cat, s, f, total in overall_summary:
        print(f"  【{cat}】 成功:{s}  失敗:{f}  合計:{total}")
        grand_total += total
        grand_success += s
    print(f"\n  === 全合計: {grand_success}/{grand_total} ===")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n中断しました。再実行すれば未取得分から続行できます。")
        sys.exit(1)
