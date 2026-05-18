#!/usr/bin/env python3
"""
関東地方整備局 令和7年度 入札結果Excel 一括ダウンロード & 抽出

R7工事12ヶ月 + R7業務12ヶ月 = 24ファイルをダウンロードして統合
出力: kanto_r7_all.json
"""
import os
import sys
import json
import time
import urllib.request
import pandas as pd

OUTPUT_DIR = "./mlit_kanto_r7"
OUTPUT_JSON = "kanto_r7_all.json"

R7_KOUJI_URLS = {
    '4月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000917998.xls',
    '5月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000917999.xls',
    '6月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000923738.xls',
    '7月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000924971.xls',
    '8月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000927469.xls',
    '9月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000930595.xls',
    '10月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000932096.xls',
    '11月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000935478.xls',
    '12月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000937261.xls',
    '1月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000938443.xls',
    '2月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000940906.xls',
    '3月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000944593.xls',
}

R7_GYOUMU_URLS = {
    '4月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000918000.xls',
    '5月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000918002.xls',
    '6月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000923742.xls',
    '7月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000924972.xls',
    '8月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000927470.xls',
    '9月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000930596.xls',
    '10月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000932097.xls',
    '11月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000935480.xls',
    '12月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000937262.xls',
    '1月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000938444.xls',
    '2月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000940907.xls',
    '3月': 'https://www.ktr.mlit.go.jp/ktr_content/content/000944594.xls',
}


def download_excel(url, save_path):
    if os.path.exists(save_path):
        return save_path
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(save_path, 'wb') as f:
        f.write(data)
    return save_path


def download_all():
    os.makedirs(f"{OUTPUT_DIR}/kouji", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/gyoumu", exist_ok=True)
    
    print(f"=== R7 工事 ダウンロード ===")
    for label, url in R7_KOUJI_URLS.items():
        path = f"{OUTPUT_DIR}/kouji/r7_{label}.xls"
        try:
            download_excel(url, path)
            size = os.path.getsize(path)
            print(f"  ✓ {label}: {size:,} bytes")
        except Exception as e:
            print(f"  ✗ {label}: {e}")
        time.sleep(0.5)
    
    print(f"\n=== R7 業務 ダウンロード ===")
    for label, url in R7_GYOUMU_URLS.items():
        path = f"{OUTPUT_DIR}/gyoumu/r7_{label}.xls"
        try:
            download_excel(url, path)
            size = os.path.getsize(path)
            print(f"  ✓ {label}: {size:,} bytes")
        except Exception as e:
            print(f"  ✗ {label}: {e}")
        time.sleep(0.5)


def parse_excel(path, kind):
    """Excelをpandasで読んでレコードリスト化"""
    try:
        # .xls はxlrd必要 / .xlsx はopenpyxl
        if path.endswith('.xls'):
            df = pd.read_excel(path, engine='xlrd', header=None)
        else:
            df = pd.read_excel(path, engine='openpyxl', header=None)
    except Exception as e:
        print(f"  ✗ {path}: {e}")
        return []
    
    return df


def main():
    if not os.path.isdir(OUTPUT_DIR) or len(os.listdir(f"{OUTPUT_DIR}/kouji")) < 12:
        print("Excel未ダウンロード、ダウンロード開始...")
        download_all()
    
    # 構造確認のため、4月分のExcelを表示
    print(f"\n=== R7 4月工事Excelの構造確認 ===")
    df = parse_excel(f"{OUTPUT_DIR}/kouji/r7_4月.xls", '工事')
    if df is not None:
        print(f"  shape: {df.shape}")
        print(f"  最初10行:")
        print(df.head(15).to_string())


if __name__ == "__main__":
    main()
