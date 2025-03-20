# Model Context Protocol (MCP) フレームワーク

MCPは、BlenderとUnreal Engine 5を連携させ、AIによるゲーム開発を支援するフレームワークです。自然言語コマンドを使用して3Dモデルを作成し、ゲームを構築できます。

## 主な機能

- **Blender-UE5連携**: Blenderで作成したモデルをUE5に直接転送
- **AIアシスタント**: OpenAI GPT-4を活用した自然言語インターフェース
- **3Dアセット生成**: 自然言語から3Dモデルを生成
- **クロスプラットフォーム**: Windows、macOS、Linuxに対応

## 必要条件

- Python 3.9以上
- Blender 3.6以上
- Unreal Engine 5.3以上
- OpenAI API キー（AIアシスト機能を使用する場合）

## クイックスタート

1. リポジトリをクローン:
   ```bash
   git clone https://github.com/yourusername/UE5-MCP.git
   cd UE5-MCP
   ```

2. 依存パッケージのインストール:
   ```bash
   pip install -r requirements.txt
   ```

3. 設定ファイルのセットアップ:
   ```bash
   # 設定ファイルのテンプレートをコピー
   cp .env.example .env
   cp mcp_settings.json.example mcp_settings.json
   
   # 自動セットアップスクリプトを実行（推奨）
   python setup_mcp.py
   ```

4. 手動で設定する場合は、`.env`と`mcp_settings.json`を編集:
   - OpenAI APIキーを設定
   - BlenderとUE5の実行ファイルパスを設定
   - UE5プロジェクトパスを設定

## 使用方法

### MCPシステムの起動

```bash
python run_mcp.py all
```

オプション:
- `all`: すべてのコンポーネントを起動
- `server`: サーバーのみ起動
- `blender`: サーバーとBlender連携を起動
- `ue5`: サーバーとUE5連携を起動

### Web UIへのアクセス

MCPサーバーが起動したら、ブラウザで以下のURLにアクセスします:
```
http://localhost:8080
```

### シューティングゲームの作成例

1. UE5プロジェクトを新規作成
2. MCPサーバーを起動
3. Web UIから「シューティングゲーム生成」を選択
4. 生成が完了したら、UE5エディタでプロジェクトを開く

## Docker環境での実行

MCPはDockerコンテナでも実行できます。これにより環境構築が簡単になります。

### Dockerで実行

1. Docker環境を構築:
   ```bash
   # イメージをビルドして実行
   docker build -t mcp-server .
   docker run -p 8080:8080 -v $(pwd)/exports:/app/exports -v $(pwd)/imports:/app/imports mcp-server
   ```

2. Docker Composeで実行（推奨）:
   ```bash
   # 環境変数を設定
   echo "OPENAI_API_KEY=your_api_key_here" > .env.docker
   
   # Docker Composeで起動
   docker-compose up -d
   ```

3. ブラウザで以下のURLにアクセス:
   ```
   http://localhost:8080
   ```

### APIキーの安全な設定

セキュリティ上の理由から、APIキーはリポジトリに含めないでください。以下のスクリプトを使用して安全に設定できます:

```bash
# APIキー設定ツールの実行
python set_api_key.py
```

## セキュリティ注意事項

- **APIキー**: `.env`ファイルに記載するAPIキーはGitHubにプッシュしないでください
- **ローカル使用**: 基本的にローカルネットワークでの利用を推奨します
- **パブリック公開**: インターネットに公開する場合は、適切なセキュリティ対策を施してください

## ディレクトリ構造

- `blender_scripts/`: Blender連携スクリプト
- `exports/`: Blenderからのエクスポートディレクトリ
- `imports/`: UE5へのインポートディレクトリ
- `assets/`: 共有アセット
- `logs/`: ログファイル
- `templates/`: WebUIテンプレート

## トラブルシューティング

- **Blender/UE5接続エラー**: 実行ファイルのパスが正しいか確認してください
- **APIエラー**: OpenAI APIキーの有効性と制限を確認してください
- **ポート競合**: 別のアプリケーションが同じポートを使用していないか確認してください

## 貢献

貢献は歓迎します！以下の方法で参加できます:
1. このリポジトリをフォーク
2. 機能追加やバグ修正のブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## ライセンス

[MIT](LICENSE)

## 謝辞

- OpenAI - GPT-4 API
- Blender Foundation - Blender
- Epic Games - Unreal Engine 5
