#!/bin/bash

echo "MCP (Model Context Protocol) インストーラー"
echo "------------------------------------"

# Pythonが利用可能か確認
if ! command -v python3 &> /dev/null; then
    echo "[エラー] Python3が見つかりません。"
    echo "Python3をインストールしてからもう一度試してください。"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "検出されたPython: $PYTHON_VERSION"

# 依存関係のインストール
echo "Pythonパッケージをインストールしています..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[エラー] パッケージのインストールに失敗しました。"
    exit 1
fi

# 設定ファイルの作成
echo "MCP設定ファイルを作成しています..."
python3 -c "import json; f=open('mcp_settings.json', 'w'); json.dump({'server':{'host':'127.0.0.1','port':5000,'autoStart':True},'modules':{'blender':{'enabled':True,'port':5001},'unreal':{'enabled':True,'port':5002}},'ai':{'provider':'mock','model':'gpt-4'},'paths':{'blender':'','unreal':'','exports':'./exports'},'logging':{'level':'info','file':'mcp.log'},'version':'1.0.0'}, f, indent=2); f.close()"

# .envファイルの作成
if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo ".envファイルを作成しました。"
    else
        echo ".envファイルは既に存在します。"
    fi
fi

# 実行権限の設定
chmod +x run_mcp.py
echo "run_mcp.pyに実行権限を設定しました。"

echo "インストールが完了しました!"
echo ""
echo "MCPサーバーを起動するには、以下のコマンドを実行してください:"
echo "  python3 run_mcp.py all"
echo ""
echo "設定を変更するには、mcp_settings.jsonファイルを編集してください。"
echo "" 
