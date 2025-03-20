# Model Context Protocol (MCP)

## 概要
Model Context Protocol (MCP) は、Blenderと Unreal Engine 5 (UE5) にAI駆動の自動化機能を統合するフレームワークです。プロシージャル生成、アセット管理、ゲームプレイプログラミング支援などを可能にします。

## 主な機能
- **AIによる自動化**: 自然言語コマンドを使用したシーン生成とアセット作成（OpenAI APIキーが設定されていない場合はモックレスポンスを返します）
- **Blender-MCP**: Blenderでのモデリング、テクスチャリング、最適化の自動化
- **UE5-MCP**: UE5でのレベルデザイン、Blueprint自動化、デバッグのサポート
- **シームレスな統合**: BlenderからUE5へのアセット移行を効率化
- **クロスプラットフォーム**: Windows、macOS、Linuxでの動作をサポート

## インストール

### 前提条件
- Python 3.x
- Node.js 12.x以上（UVコマンドでのインストールに必要）
- Blender 3.x以降（Blender-MCPを使用する場合）
- Unreal Engine 5.1以降（UE5-MCPを使用する場合）

### 簡単インストール（推奨）

#### 方法1: UVコマンドでインストール
```bash
# リポジトリをクローン
git clone https://github.com/tacyan/UE5-MCP.git
cd UE5-MCP

# Node.jsでインストール (Windows/Mac/Linux共通)
npm install
```

#### 方法2: プラットフォーム別のスクリプトでインストール
**Windows:**
```bash
# install.batをダブルクリックするか、コマンドラインで以下を実行:
install.bat
```

**macOS/Linux:**
```bash
# ターミナルで実行:
chmod +x install.sh
./install.sh
```

### 手動インストール
```bash
# 依存関係のインストール
pip install -r requirements.txt

# 設定
cp .env.example .env
# 必要に応じて.envを編集
```

## 設定

### JSON設定ファイル
MCPは`mcp_settings.json`ファイルを使用して設定を管理します。このファイルはインストール時に自動的に作成されますが、手動で編集することもできます。

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 5000,
    "autoStart": true
  },
  "modules": {
    "blender": {
      "enabled": true,
      "port": 5001
    },
    "unreal": {
      "enabled": true,
      "port": 5002
    }
  },
  "ai": {
    "provider": "mock",
    "model": "gpt-4"
  },
  "paths": {
    "blender": "",
    "unreal": "",
    "exports": "./exports"
  },
  "logging": {
    "level": "info",
    "file": "mcp.log"
  },
  "version": "1.0.0"
}
```

### 環境変数
`.env`ファイルで以下の環境変数を設定できます：

```
# OpenAI API設定（オプション）
OPENAI_API_KEY=your_openai_api_key_here

# サーバー設定のオーバーライド
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=5000
DEBUG=false
```

## 使用方法

### NPM スクリプト（UVコマンド）
```bash
# すべてのコンポーネントを起動
npm start

# 個別コンポーネントを起動
npm run start:server   # サーバーのみ
npm run start:blender  # サーバー + Blender-MCP
npm run start:ue5      # サーバー + UE5-MCP
```

### Python スクリプト
```bash
# すべてのコンポーネントを起動
python run_mcp.py all

# 個別コンポーネントを起動
python run_mcp.py server   # サーバーのみ
python run_mcp.py blender  # サーバー + Blender-MCP
python run_mcp.py ue5      # サーバー + UE5-MCP
```

## API リファレンス

### MCPサーバーAPI
- `GET /api/status`: サーバーのステータスを取得
- `POST /api/blender/command`: Blenderコマンドを実行
- `POST /api/unreal/command`: UE5コマンドを実行
- `POST /api/ai/generate`: AIによるコンテンツ生成

### Blender-MCP API
- `GET /api/status`: Blender-MCPのステータスを取得
- `POST /api/command`: Blenderコマンドを実行
  - コマンド例: `generate_scene`, `add_object`, `generate_texture`, `export_asset`など

### UE5-MCP API
- `GET /api/status`: UE5-MCPのステータスを取得
- `POST /api/command`: UE5コマンドを実行
  - コマンド例: `create_level`, `import_asset`, `create_blueprint`, `generate_terrain`など

## AIモード

### モックモード (デフォルト)
OpenAI APIキーが設定されていない場合、システムは自動的にモックモードで動作します。このモードでは、AIコンテンツ生成のリクエストに対して事前に設定されたレスポンスを返します。開発とテストに適しています。

### OpenAIモード
OpenAI APIキーを設定すると、システムはOpenAI APIを使用してAIコンテンツを生成します。本番環境での使用に適しています。

## 使用例

### Blenderでのシーン生成
```bash
curl -X POST http://localhost:5001/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "generate_scene", "params": {"description": "A sci-fi spaceship interior with neon lighting"}}'
```

### UE5でのBlueprintの作成
```bash
curl -X POST http://localhost:5002/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "create_blueprint", "params": {"name": "EnemyAI", "class": "Character", "ai_generate": true, "description": "An enemy AI that patrols and attacks the player"}}'
```

## トラブルシューティング
- サーバー接続エラー: ポート設定とファイアウォールの設定を確認してください
- Blender/UE5連携エラー: 必要なプラグインが有効になっていることを確認してください
- Python関連エラー: 
  - Windowsでは`python`コマンドが使用可能か確認してください
  - Mac/Linuxでは`python3`コマンドが使用可能か確認してください
- AI生成エラー: 
  - モックモードの場合: 正常に機能します、実際のAI生成は行われません
  - OpenAIモードの場合: OpenAI APIキーが正しく設定されていることを確認してください

## ライセンス
MITライセンス
