#!/bin/bash
# UE5とMCPフレームワークを連携させて起動するスクリプト

# 現在のディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 環境変数をロード
source "$SCRIPT_DIR/.env"

# パスの確認
if [ ! -f "$UE5_PATH" ]; then
    echo "エラー: UE5実行ファイルが見つかりません: $UE5_PATH"
    echo "環境変数 UE5_PATH を確認してください。"
    exit 1
fi

if [ ! -f "$UE5_PROJECT_PATH" ]; then
    echo "警告: UE5プロジェクトファイルが見つかりません: $UE5_PROJECT_PATH"
    echo "新しいプロジェクトを作成します。"
fi

# MCPサーバーをバックグラウンドで起動
echo "MCPサーバーを起動しています..."
python "$SCRIPT_DIR/mcp_server.py" &
MCP_SERVER_PID=$!
sleep 2

# MCPサーバーが起動したか確認
if ! curl -s "http://${MCP_SERVER_HOST:-127.0.0.1}:${MCP_SERVER_PORT:-8080}/api/status" > /dev/null; then
    echo "警告: MCPサーバーの起動確認ができませんでした。サーバーは別のポートで実行されている可能性があります。"
else
    echo "MCPサーバーの起動を確認しました。"
fi

# UE5プラグインディレクトリを作成
PLUGIN_DEST_DIR="$(dirname "$UE5_PROJECT_PATH")/Plugins/MCP"
mkdir -p "$PLUGIN_DEST_DIR"

# プラグインファイルをコピー
echo "UE5プラグインファイルをプロジェクトにコピーしています..."
cp -r "$SCRIPT_DIR/ue5_plugin/"* "$PLUGIN_DEST_DIR/"

# UE5を起動
echo "Unreal Engineを起動しています..."
"$UE5_PATH" "$UE5_PROJECT_PATH"

# 終了時にMCPサーバーを停止
echo "MCPサーバーを停止しています..."
kill $MCP_SERVER_PID

echo "完了しました。" 
