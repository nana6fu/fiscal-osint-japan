#!/usr/bin/env python3
"""
復興庁 公共調達・補助金データ自動スクレイパー v0.1
- HEADリクエストでサイズ比較 → 変更があれば再DL
- 404は「まだ公表されていない」として静かにスキップ
- 既存命名規則(R{NN}_xxx)に合わせてローカル保存
"""
import requests
from pathlib import Path
from datetime import datetime

SAVE_DIR = Path('/Volumes/SN0W8ALL/tokubetsu-kaikei/data/fukko')
BASE = 'https://www.reconstruction.go.jp/files/user/topics/'

# (remote_filename, local_filename) のペア
TARGETS = []
for nn in ['05', '06', '07', '08']:
    for ext in ['xls', 'pdf']:
        TARGETS.append((f'R{nn}_koukyoutyoutatsu_ippan.{ext}', f'R{nn}_koukyoutyoutatsu_ippan.{ext}'))
        TARGETS.append((f'R{nn}_koukyoutyoutatsu_zuii.{ext}',  f'R{nn}_koukyoutyoutatsu_zuii.{ext}'))
    TARGETS.append((f'{nn}hojokin1kamihanki.xlsx', f'R{nn}_hojokin_kami.xlsx'))
    TARGETS.append((f'{nn}hojokin2shimohanki.xlsx', f'R{nn}_hojokin_shimo.xlsx'))

new_files, updated_files, not_yet, errors, skipped = [], [], [], [], []

for remote, local_name in TARGETS:
    url = BASE + remote
    local = SAVE_DIR / local_name
    try:
        r = requests.head(url, allow_redirects=True, timeout=15)
    except Exception as e:
        errors.append((remote, str(e)))
        continue
    
    if r.status_code == 404:
        not_yet.append(remote)
        continue
    if r.status_code != 200:
        errors.append((remote, f'HTTP {r.status_code}'))
        continue
    
    remote_size = int(r.headers.get('content-length', 0))
    if local.exists() and local.stat().st_size == remote_size:
        skipped.append(local_name)
        continue
    
    action = 'updated' if local.exists() else 'new'
    r = requests.get(url, timeout=60)
    local.write_bytes(r.content)
    if action == 'new':
        new_files.append((local_name, len(r.content)))
    else:
        updated_files.append((local_name, len(r.content)))

print(f'=== 復興庁スクレイパー実行結果 ({datetime.now().strftime("%Y-%m-%d %H:%M")}) ===')
print(f'✓  既存と一致(SKIP): {len(skipped)}件')
print(f'⬇  新規DL: {len(new_files)}件')
for f, size in new_files:
    print(f'   + {f} ({size:,} bytes)')
print(f'~  更新DL: {len(updated_files)}件')
for f, size in updated_files:
    print(f'   ~ {f} ({size:,} bytes)')
print(f'⏸  未公表(404): {len(not_yet)}件')
for f in not_yet:
    print(f'   - {f}')
print(f'!  エラー: {len(errors)}件')
for f, err in errors:
    print(f'   ! {f}: {err}')
