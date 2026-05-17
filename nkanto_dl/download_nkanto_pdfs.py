#!/usr/bin/env python3
"""
北関東防衛局 令和7年度 発注実績PDFを一括ダウンロード

使い方:
    pip install requests beautifulsoup4
    python3 download_nkanto_pdfs.py

出力:
    ./n_kanto_r7_pdfs/工事/*.pdf
    ./n_kanto_r7_pdfs/業務/*.pdf
    ./n_kanto_r7_pdfs/_index.txt  (案件名⇔ファイル名の対応表)
"""
import os
import time
import re
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

BASE_URLS = {
    "工事": "https://www.mod.go.jp/rdb/n-kanto/nyusatsu-keiyaku/kensetu/2025kekka/07kouji.files/sheet001.htm",
    "業務": "https://www.mod.go.jp/rdb/n-kanto/nyusatsu-keiyaku/kensetu/2025kekka/07gyoumu.files/sheet001.htm",
}

OUTPUT_DIR = "./n_kanto_r7_pdfs"
SLEEP_SEC = 1.5  # 連続DLでサーバーに負荷をかけないため

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}


def safe_filename(s, maxlen=120):
    """ファイル名として使えない文字を除去・置換"""
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', s)
    s = re.sub(r'\s+', '_', s)
    s = s.strip('._-')
    return s[:maxlen] if s else "unnamed"


def fetch_html(url):
    """HTML取得（Shift_JIS対応）"""
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    # 防衛省サイトは Shift_JIS
    for enc in ('shift_jis', 'cp932', 'utf-8'):
        try:
            return r.content.decode(enc), enc
        except UnicodeDecodeError:
            continue
    r.encoding = r.apparent_encoding
    return r.text, r.encoding


def extract_pdf_links(html, base_url):
    """HTML中のPDFリンクを抽出して(タイトル, URL)リスト"""
    soup = BeautifulSoup(html, 'html.parser')
    seen = set()
    pdf_links = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue
        # PDF判定（.pdf を含む、クエリ付きも許容）
        if '.pdf' not in href.lower():
            continue
        abs_url = urllib.parse.urljoin(base_url, href)
        if abs_url in seen:
            continue
        seen.add(abs_url)

        # リンクテキスト → なければファイル名
        title = a.get_text(strip=True)
        if not title:
            title = os.path.basename(urllib.parse.urlparse(href).path)

        pdf_links.append((title, abs_url))

    return pdf_links


def download_pdf(url, save_path):
    """PDFを1個ダウンロード（streaming）"""
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
        # 不完全ファイル削除
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

    for category, base_url in BASE_URLS.items():
        print(f"\n{'=' * 70}")
        print(f"【{category}】 {base_url}")
        print('=' * 70)

        cat_dir = os.path.join(OUTPUT_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)

        # HTML取得
        print("目次HTML取得中...")
        try:
            html, used_enc = fetch_html(base_url)
            print(f"  エンコーディング: {used_enc}")
        except Exception as e:
            print(f"  ✗ HTML取得失敗: {e}")
            continue

        # PDFリンク抽出
        pdf_links = extract_pdf_links(html, base_url)
        print(f"  PDFリンク発見: {len(pdf_links)}件")

        if not pdf_links:
            print("  ※ PDFリンクが見つかりません。HTML構造を確認してください。")
            # デバッグ用にHTMLを保存
            debug_path = os.path.join(OUTPUT_DIR, f"_debug_{category}.htm")
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  → {debug_path} に保存（構造確認用）")
            continue

        # ダウンロード
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

    # インデックスファイル
    if index_lines:
        index_path = os.path.join(OUTPUT_DIR, "_index.txt")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("カテゴリ\t連番\tファイル名\t案件名\tURL\n")
            f.write('\n'.join(index_lines))
        print(f"\n→ 対応表: {index_path}")

    # 結果サマリ
    print(f"\n{'=' * 70}")
    print("ダウンロード結果サマリ")
    print('=' * 70)
    for cat, s, f, total in overall_summary:
        print(f"  【{cat}】 成功:{s}  失敗:{f}  合計:{total}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n中断しました。再実行すれば未取得分から続行できます。")
        sys.exit(1)
