# Model Context Protocol (MCP)

## 概要
Model Context Protocol (MCP) は、Blenderと Unreal Engine 5 (UE5) にAI駆動の自動化機能を統合するフレームワークです。プロシージャル生成、アセット管理、ゲームプレイプログラミング支援などを可能にします。

## 主な機能
- **AIによる自動化**: 自然言語コマンドを使用したシーン生成とアセット作成
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
1. `.env.example`ファイルを`.env`にコピーし、適切な値を設定します。
2. OpenAI APIキーを設定します（AI機能を使用する場合）。
3. 必要に応じて`config.yml`の設定を調整します。

## 使用方法

### MCPサーバーの起動
```bash
python server.py
```

### Blender-MCPモジュールの起動
```bash
python blender_mcp.py
```

### UE5-MCPモジュールの起動
```bash
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
- AI生成エラー: OpenAI APIキーが正しく設定されていることを確認してください

## ライセンス
MITライセンス 
