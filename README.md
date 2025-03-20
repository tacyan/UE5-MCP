# Model Context Protocol (MCP)

## 概要
Model Context Protocol (MCP) は、Blenderと Unreal Engine 5 (UE5) にAI駆動の自動化機能を統合するフレームワークです。プロシージャル生成、アセット管理、ゲームプレイプログラミング支援などを可能にします。

## 主な機能
- **AIによる自動化**: 自然言語コマンドを使用したシーン生成とアセット作成（OpenAI APIキーが設定されていない場合はモックレスポンスを返します）
- **Blender-MCP**: Blenderでのモデリング、テクスチャリング、最適化の自動化
- **UE5-MCP**: UE5でのレベルデザイン、Blueprint自動化、デバッグのサポート
- **シームレスな統合**: BlenderからUE5へのアセット移行を効率化

## インストール

### 前提条件
- Python 3.x
- Blender 3.x以降（Blender-MCPを使用する場合）
- Unreal Engine 5.1以降（UE5-MCPを使用する場合）

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 設定
1. `.env.example`ファイルを`.env`にコピーし、必要に応じて値を設定します。
   ```bash
   cp .env.example .env
   ```
2. OpenAI APIキー（オプション）:
   - AI機能を完全に使用する場合は、OpenAI APIキーを設定します
   - キーが設定されていない場合は、自動的にモックモードで実行されます
3. 必要に応じて`config.yml`の設定を調整します。

## 使用方法

### 起動方法（オールインワン）
一度にすべてのコンポーネントを起動するには、以下のコマンドを使用します：
```bash
python run_mcp.py all
```
このコマンドは、MCPサーバー、Blender-MCP、UE5-MCPをすべて起動します。

### 特定のコンポーネントを起動
```bash
# MCPサーバーのみを起動
python run_mcp.py server

# MCPサーバーとBlender-MCPを起動
python run_mcp.py blender

# MCPサーバーとUE5-MCPを起動
python run_mcp.py ue5
```

### 個別に起動（上級ユーザー向け）
```bash
# MCPサーバーを起動
python server.py

# Blender-MCPモジュールを起動
python blender_mcp.py

# UE5-MCPモジュールを起動
python ue5_mcp.py
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
- AI生成エラー: 
  - モックモードの場合: 正常に機能します、実際のAI生成は行われません
  - OpenAIモードの場合: OpenAI APIキーが正しく設定されていることを確認してください

## ライセンス
MITライセンス
