@echo off
echo MCP (Model Context Protocol) インストーラー
echo ------------------------------------

:: Pythonが利用可能か確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Pythonが見つかりません。
    echo Pythonをインストールしてからもう一度試してください。
    echo https://www.python.org/downloads/
    goto :eof
)

:: 依存関係のインストール
echo Pythonパッケージをインストールしています...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [エラー] パッケージのインストールに失敗しました。
    goto :eof
)

:: 設定ファイルの作成
echo MCP設定ファイルを作成しています...
python -c "import json; f=open('mcp_settings.json', 'w'); json.dump({'server':{'host':'127.0.0.1','port':5000,'autoStart':True},'modules':{'blender':{'enabled':True,'port':5001},'unreal':{'enabled':True,'port':5002}},'ai':{'provider':'mock','model':'gpt-4'},'paths':{'blender':'','unreal':'','exports':'./exports'},'logging':{'level':'info','file':'mcp.log'},'version':'1.0.0'}, f, indent=2); f.close()"

if exist .env.example (
    if not exist .env (
        copy .env.example .env
        echo .envファイルを作成しました。
    ) else (
        echo .envファイルは既に存在します。
    )
)

echo インストールが完了しました!
echo.
echo MCPサーバーを起動するには、以下のコマンドを実行してください:
echo   python run_mcp.py all
echo.
echo 設定を変更するには、mcp_settings.jsonファイルを編集してください。
echo.

pause 
