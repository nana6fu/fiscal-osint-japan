#!/usr/bin/env python3
"""
復興庁 公共調達・補助金・予算配分データ自動スクレイパー v0.3
- x-kuroco-backend-last-modified ベースで変更検知(Kuroco CMS対応)
- DL後にローカルmtimeをリモートのlast-modifiedに合わせる
- 404は「まだ公表されていない」として静かにスキップ
"""
import requests
import email.utils
import os
from pathlib import Path
from datetime import datetime

SAVE_DIR = Path("/Volumes/SN0W8ALL/tokubetsu-kaikei/data/fukko")
BASE = "https://www.reconstruction.go.jp/files/user/topics/"

# (remote_filename, local_filename) のペア
TARGETS = []
for nn in ["05", "06", "07", "08"]:
    for ext in ["xls", "pdf"]:
        TARGETS.append((f"R{nn}_koukyoutyoutatsu_ippan.{ext}", f"R{nn}_koukyoutyoutatsu_ippan.{ext}"))
        TARGETS.append((f"R{nn}_koukyoutyoutatsu_zuii.{ext}",  f"R{nn}_koukyoutyoutatsu_zuii.{ext}"))
    TARGETS.append((f"{nn}hojokin1kamihanki.xlsx", f"R{nn}_hojokin_kami.xlsx"))
    TARGETS.append((f"{nn}hojokin2shimohanki.xlsx", f"R{nn}_hojokin_shimo.xlsx"))

# R8 予算配分(箇所付け)PDF
for name in ["nousui", "kokkou", "fukushima"]:
    TARGETS.append((f"main-cat8/sub-cat8-3/R8{name}.pdf", f"R8{name}.pdf"))

def get_remote_mtime(headers):
    """KurocoのカスタムヘッダーまたはstandardなLast-Modifiedからmtimeを取得"""
    lm = headers.get("x-kuroco-backend-last-modified") or headers.get("Last-Modified")
    if not lm:
        return None
    try:
        return email.utils.parsedate_to_datetime(lm).timestamp()
    except Exception:
        return None

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
        errors.append((remote, f"HTTP {r.status_code}"))
        continue
    
    remote_mtime = get_remote_mtime(r.headers)
    
    if local.exists() and remote_mtime is not None:
        local_mtime = local.stat().st_mtime
        if remote_mtime <= local_mtime + 1:
            skipped.append(local_name)
            continue
    
    action = "updated" if local.exists() else "new"
    
    try:
        r = requests.get(url, timeout=60)
        local.write_bytes(r.content)
        if remote_mtime is not None:
            os.utime(local, (remote_mtime, remote_mtime))
    except Exception as e:
        errors.append((remote, f"DL error: {e}"))
        continue
    
    if action == "new":
        new_files.append((local_name, len(r.content)))
    else:
        updated_files.append((local_name, len(r.content)))

now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"=== 復興庁スクレイパー v0.3 実行結果 ({now_str}) ===")
print(f"✓  既存と一致(SKIP): {len(skipped)}件")
print(f"⬇  新規DL: {len(new_files)}件")
for f, size in new_files:
    print(f"   + {f} ({size:,} bytes)")
print(f"~  更新DL: {len(updated_files)}件")
for f, size in updated_files:
    print(f"   ~ {f} ({size:,} bytes)")
print(f"⏸  未公表(404): {len(not_yet)}件")
for f in not_yet:
    print(f"   - {f}")
print(f"!  エラー: {len(errors)}件")
for f, err in errors:
    print(f"   ! {f}: {err}")
