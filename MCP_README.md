# Model Context Protocol (MCP)

## システム概要

MCPはBlender 4.4.0とUnreal Engine 5.5を連携させ、OpenAI APIを活用してゲーム開発を効率化するフレームワークです。サーバー-クライアントアーキテクチャに基づいており、以下のコンポーネントで構成されています：

- **MCPサーバー**: 中央制御システム（APIサーバー）
- **Blender-MCP**: Blenderとの連携モジュール
- **UE5-MCP**: Unreal Engine 5との連携モジュール
- **AI統合**: OpenAI APIを使用したコンテンツ生成機能

## 主な機能

### Blender連携機能
- 3Dモデル作成（基本形状・カスタム形状）
- マテリアル適用と編集
- アセットのエクスポート（FBX、OBJ、GLBなど）
- UE5へのアセット転送

### UE5連携機能
- レベル作成（ThirdPersonなど各種テンプレート）
- 地形生成（山岳、平地、砂漠など）
- Blueprint自動生成・編集
- アセットインポートと配置
- ライティングビルドなどのワークフロー自動化

### AI支援機能
- 自然言語コマンド解析
- ゲームコンセプト・キャラクター設定の生成
- バックグラウンドストーリー作成
- アセットデザイン提案

## セットアップ

### 必要環境
- Python 3.x
- Blender 4.4.0以降
- Unreal Engine 5.5以降
- OpenAI APIキー

### 設定ファイル
- `.env`: 環境変数設定ファイル
- `mcp_settings.json`: システム設定ファイル

## 使用方法

### サーバー起動
```bash
python run_mcp.py all
```

### シンプルなゲーム作成
```bash
python simple_ue5_game.py
```

### Blender-UE5アセット連携
```bash
python blender_to_ue5_asset.py
```

### AI開発アシスタント
```bash
python ai_ue5_assistant.py
```

### バッチワークフロー実行
```bash
python run_mcp_workflow.py blender_to_ue5
python run_mcp_workflow.py simple_game
python run_mcp_workflow.py ai_assistant
```

## プログラミングインターフェース

### Blender-MCP API
```python
# Blender内で実行
from blender_integration import BlenderMCPIntegration

integration = BlenderMCPIntegration()
integration.create_simple_model("sword", "GameSword")
integration.send_to_ue5("GameSword")
```

### UE5-MCP API
```python
# UE5内で実行
from ue5_integration import UE5MCPIntegration

integration = UE5MCPIntegration()
integration.create_level("MCPTestLevel", "ThirdPerson")
integration.generate_terrain(terrain_type="mountainous")
```

## メンテナンス・開発

### ログファイル
- `mcp_server.log`
- `blender_mcp.log`
- `ue5_mcp.log`
- `ai_ue5_assistant.log`
- `simple_ue5_game.log`
- `blender_to_ue5_asset.log`

### デバッグ
設定ファイル`mcp_settings.json`の`debug`フラグを`true`に設定するとデバッグモードで実行されます。

### OpenAI API
キーが設定されていればOpenAI APIを使用し、未設定の場合はモックモードで動作します。

## ライセンス
MITライセンス 
