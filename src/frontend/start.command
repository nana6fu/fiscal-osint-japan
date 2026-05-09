#!/bin/bash
# ========================================
# Fiscal OSINT Japan 起動スクリプト
# ダブルクリックで起動できます
# ========================================

cd "$(dirname "$0")"

echo "========================================"
echo " Fiscal OSINT Japan 起動中..."
echo "========================================"

# --- 1. Ollamaが起動しているか確認 ---
echo ""
echo "[1/3] Swallow (Ollama) の確認..."

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "  ✅ Ollama 起動済み"
else
  echo "  ⚠️  Ollama が起動していません。起動します..."
  open -a Ollama 2>/dev/null || ollama serve &
  echo "  ⏳ 起動待機中 (5秒)..."
  sleep 5
  if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  ✅ Ollama 起動完了"
  else
    echo "  ❌ Ollama の起動に失敗しました"
    echo "     手動で Ollama を起動してから再実行してください"
  fi
fi

# --- 2. 既存のポート8080を解放 ---
echo ""
echo "[2/3] ポート 8080 の確認..."

EXISTING=$(lsof -ti:8080 2>/dev/null)
if [ -n "$EXISTING" ]; then
  echo "  既存プロセスを停止します (PID: $EXISTING)"
  kill -9 $EXISTING 2>/dev/null
  sleep 1
fi

# --- 3. ローカルサーバー起動 ---
echo ""
echo "[3/3] ローカルサーバーを起動します (port 8080)..."

python3 -m http.server 8080 > /tmp/fiscal_osint_server.log 2>&1 &
SERVER_PID=$!
echo "  PID: $SERVER_PID"
sleep 1

if kill -0 $SERVER_PID 2>/dev/null; then
  echo "  ✅ サーバー起動完了"
else
  echo "  ❌ サーバーの起動に失敗しました"
  echo "     ログ: $(cat /tmp/fiscal_osint_server.log)"
  read -p "Enterキーで終了..."
  exit 1
fi

# --- Chromeで開く ---
echo ""
echo "========================================"
echo " ブラウザを開きます..."
echo " URL: http://localhost:8080/index.html"
echo "========================================"
echo ""
echo " 終了するにはこのウィンドウを閉じてください"
echo " (サーバーも自動停止します)"
echo "========================================"

open -a "Google Chrome" http://localhost:8080/index.html 2>/dev/null \
  || open http://localhost:8080/index.html

# --- ウィンドウを閉じるまで待機 ---
trap "echo ''; echo 'サーバーを停止します...'; kill $SERVER_PID 2>/dev/null; echo '停止完了'; exit 0" EXIT INT TERM

# Ctrl+C または ウィンドウを閉じるまで待機
while kill -0 $SERVER_PID 2>/dev/null; do
  sleep 2
done
