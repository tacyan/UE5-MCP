# Model Context Protocol (MCP)

## 概要
Model Context Protocol (MCP) は、Blender 4.4.0と Unreal Engine 5.5 (UE5)にAI駆動の自動化機能を統合するフレームワークです。OpenAI APIを活用して、プロシージャル生成、アセット管理、ゲームプレイプログラミング支援などを実現します。

## 主な機能
- **AIによる自動化**: 自然言語コマンドを使用したシーン生成とアセット作成（OpenAI APIを使用）
- **Blender-MCP**: Blenderでのモデリング、テクスチャリング、最適化の自動化
- **UE5-MCP**: UE5でのレベルデザイン、Blueprint自動化、デバッグのサポート
- **シームレスな統合**: BlenderからUE5へのアセット転送ワークフロー
- **クロスプラットフォーム**: Windows、macOS、Linuxでの動作をサポート

## インストール

### 前提条件
- Python 3.x
- Blender 4.4.0以降（Blender-MCPを使用する場合）
- Unreal Engine 5.5以降（UE5-MCPを使用する場合）
- OpenAI APIキー（AIアシスト機能を使用する場合）

### インストール手順
```bash
# リポジトリをクローン
git clone https://github.com/tacyan/UE5-MCP.git
cd UE5-MCP

# 依存関係のインストール
pip install -r requirements.txt

# 設定
cp .env.example .env
cp mcp_settings.json.example mcp_settings.json
# 必要に応じて.envとmcp_settings.jsonを編集
```

## セットアップと設定

### 環境変数の設定
`.env`ファイルで以下の設定を行います：

```
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here

# サーバー設定
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000

# Blender設定
BLENDER_ENABLED=true
BLENDER_PORT=8001
BLENDER_PATH=/path/to/blender

# UE5設定
UE5_ENABLED=true
UE5_PORT=8002
UE5_PATH=/path/to/unreal/editor
```

### MCP設定ファイル
`mcp_settings.json`ファイルでシステム全体の設定を管理します：

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": false
  },
  "modules": {
    "blender": {
      "enabled": true,
      "port": 8001,
      "path": "/path/to/blender",
      "autostart": true
    },
    "unreal": {
      "enabled": true,
      "port": 8002,
      "path": "/path/to/unreal/editor",
      "autostart": true
    }
  },
  "ai": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
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

## 使用方法

### 1. MCPサーバーの起動

MCPサーバーとモジュールを起動するには：

```bash
python run_mcp.py all
```

特定のモジュールのみ起動する場合：

```bash
python run_mcp.py server  # サーバーのみ
python run_mcp.py blender # サーバー + Blender連携
python run_mcp.py ue5     # サーバー + UE5連携
```

### 2. 機能テスト

#### Blender-UE5連携テスト
Blenderでモデルを作成してUE5に転送：

```bash
python blender_to_ue5_asset.py
```

#### UE5ゲーム作成テスト
シンプルな3Dアクションゲームの基本構造を作成：

```bash
python simple_ue5_game.py
```

#### AI駆動ゲーム開発アシスタント
自然言語でUE5の機能を制御するインタラクティブアシスタントを起動：

```bash
python ai_ue5_assistant.py
```

### 3. ワークフロー実行

統合ワークフローを実行するには：

```bash
# BlenderからUE5へのアセット転送ワークフロー
python run_mcp_workflow.py blender_to_ue5

# シンプルなUE5ゲーム作成ワークフロー
python run_mcp_workflow.py simple_game

# AI駆動ゲーム開発アシスタント
python run_mcp_workflow.py ai_assistant
```

Blender内でスクリプトを実行する場合：

```bash
python run_mcp_workflow.py blender_to_ue5 --blender
```

UE5内でスクリプトを実行する場合：

```bash
python run_mcp_workflow.py simple_game --ue5
```

## Blender連携機能

MCPは以下のBlender機能をサポートしています：

- **自動モデル作成**: 基本形状、カスタム形状（剣など）の作成
- **マテリアル適用**: 色、メタリック度、ラフネスなどのプロパティを設定
- **モデルエクスポート**: FBX, OBJ, GLB形式でエクスポート
- **UE5への転送**: モデルをUE5プロジェクトに自動転送

Blender内での使用例：
```python
# Blenderエディタ内でスクリプトを実行
from blender_integration import BlenderMCPIntegration

integration = BlenderMCPIntegration()
integration.create_simple_model("sword", "GameSword")
integration.apply_material("GameSword", "MetalSwordMaterial", metallic=0.9)
integration.send_to_ue5("GameSword", "fbx")
```

## UE5連携機能

MCPは以下のUE5機能をサポートしています：

- **レベル作成**: 様々なテンプレートからの新規レベル作成
- **地形生成**: カスタマイズ可能な地形の自動生成
- **Blueprint自動化**: AI駆動のBlueprint作成
- **アセット管理**: インポート、配置、マテリアル設定
- **ワークフロー自動化**: ライティングビルドなどの自動処理

UE5内での使用例：
```python
# UE5エディタ内でスクリプトを実行
from ue5_integration import UE5MCPIntegration

integration = UE5MCPIntegration()
integration.create_level("MCPTestLevel", "ThirdPerson")
integration.generate_terrain(size_x=4096, terrain_type="mountainous")
integration.create_blueprint("BP_CollectibleItem", "Actor", "収集可能なアイテム")
```

## AIアシスタント機能

自然言語でUE5機能を制御するAIアシスタントを使用できます：

- **コマンド変換**: 自然言語をUE5コマンドに変換
- **コンテンツ生成**: キャラクター、ストーリー、ゲームコンセプトの生成
- **問題解決**: ゲーム開発上の課題に対するAIアシスト

使用例：
```
> コマンドを入力してください: 山と森のある大きなオープンワールドの地形を生成して

🔍 '山と森のある大きなオープンワールドの地形を生成して' を解析しています...
🚀 コマンド 'generate_terrain' を実行しています...
✅ 成功: mountainous地形の生成が完了しました
```

## トラブルシューティング

### サーバー接続エラー
サーバー接続エラーが発生した場合は、サーバーが実行中かを確認し、ポート設定を確認してください：

```bash
# サーバー状態確認
curl http://127.0.0.1:8000/api/status

# 実行中のサーバープロセスを確認
ps aux | grep run_mcp
```

### ポート競合
ポートが既に使用されている場合は、設定ファイルで別のポートを指定するか、競合するプロセスを終了してください：

```bash
# 競合するプロセスの終了
pkill -f "run_mcp.py"
```

### OpenAI APIエラー
APIキーが正しく設定されていることを確認し、`.env`ファイルを確認してください。APIキーにスペースや改行がないことを確認してください。

## 開発資料

詳細なドキュメントは以下の資料を参照してください：

- [アーキテクチャ](./architecture.md)
- [Blender-MCP連携](./blender_mcp.md)
- [UE5-MCP連携](./ue5_mcp.md)
- [AI統合](./ai_integration.md)
- [コマンドリファレンス](./commands.md)

## ライセンス

このプロジェクトは[MITライセンス](./LICENSE.md)の下で公開されています。

## 貢献

プロジェクトへの貢献方法については[CONTRIBUTING.md](./CONTRIBUTING.md)を参照してください。
