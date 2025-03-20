# MCP フレームワーク クイックスタートガイド

## 1. 環境設定

このフレームワークを使用するには、以下の準備が必要です：

- Python 3.8以上
- Blender 4.0以上（オプション、Blender連携を使用する場合）
- Unreal Engine 5.1以上（オプション、UE5連携を使用する場合）
- OpenAI APIキー（AI機能を使用する場合）

## 2. セットアップ

1. 依存関係をインストールします：

```bash
pip install -r requirements.txt
```

2. 設定ファイルを編集します：

```bash
# 設定を自動生成（パスを自動検出）
python setup_mcp.py

# または、パスを指定して生成
python setup_mcp.py --blender-path /path/to/blender --ue-path /path/to/unrealEditor --openai-key YOUR_API_KEY
```

3. `mcp_settings.json` ファイルを確認し、必要に応じて調整してください。

## 3. MCPサーバーの起動

```bash
python run_mcp.py all
```

## 4. 使用例

### BlenderからUE5へのアセット転送

```bash
python run_mcp_workflow.py blender_to_ue5
```

### トレジャーハントゲームの作成

```bash
python run_mcp_workflow.py treasure_hunt
```

### ロボットゲームの作成

```bash
python run_mcp_workflow.py robot_game
```

### AIアシスタントの起動

```bash
python run_mcp_workflow.py ai_assistant
```

## 5. 自然言語によるゲーム開発

AIアシスタントを使用することで、自然言語を使ったゲーム開発が可能です：

1. AIアシスタントを起動します：

```bash
python ai_ue5_assistant.py
```

2. 例えば、以下のような指示を英語または日本語で入力できます：

- 「シンプルな3Dプラットフォーマーゲームを作成して」
- 「剣と盾を持った騎士のキャラクターモデルを作成して」
- 「自動生成された地形に木と岩を配置して」

## 6. 詳細ドキュメント

詳細な使用方法とAPIリファレンスについては、`docs/` ディレクトリ内のドキュメントを参照してください。
