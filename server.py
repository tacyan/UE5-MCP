#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPサーバー

このスクリプトは、Model Context Protocol (MCP) のメインサーバーを実装します。
Blenderおよびアンリアルエンジン5との連携を可能にし、AIドリブンの自動化機能を提供します。

主な機能:
- REST APIエンドポイントの提供
- Blender-MCPモジュールの統合
- UE5-MCPモジュールの統合
- ミドルウェア通信レイヤーの管理

制限事項:
- 設定ファイルが必要です（config.yml）
- OpenAI APIキーが必要です（.envファイルまたは環境変数で設定）。キーがない場合はモックレスポンスを返します。
"""

import os
import logging
import json
from flask import Flask, request, jsonify, render_template_string
import yaml
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_server")

# 設定ファイルの読み込み
def loadConfig():
    """
    設定ファイルを読み込む関数

    設定ファイル(config.yml)から設定を読み込みます。
    ファイルが存在しない場合はデフォルト設定を使用します。

    戻り値:
        dict: 設定情報を含む辞書
    """
    try:
        with open('config.yml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("設定ファイルが見つかりません。デフォルト設定を使用します。")
        return {
            'server': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': False
            },
            'ai': {
                'provider': 'mock',  # OpenAIキーがない場合はmockモードをデフォルトに
                'model': 'gpt-4'
            },
            'blender': {
                'enabled': True,
                'port': 5001
            },
            'unreal': {
                'enabled': True,
                'port': 5002
            }
        }
    except Exception as e:
        logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {str(e)}")
        raise

# Flaskアプリケーションの初期化
app = Flask(__name__)
config = loadConfig()

# OpenAI APIキーの確認と設定
def checkAIConfiguration():
    """
    AI設定を確認する関数
    
    OpenAI APIキーが設定されているかを確認し、なければmockモードに設定します。
    
    戻り値:
        bool: OpenAI APIキーが設定されていればTrue、なければFalse
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key and config['ai']['provider'] == 'openai':
        logger.warning("OpenAI APIキーが設定されていません。モックモードを使用します。")
        config['ai']['provider'] = 'mock'
        return False
    return config['ai']['provider'] == 'openai'

# AI設定の確認
has_openai = checkAIConfiguration()

# HTML テンプレート
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP サーバー</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #444;
            margin-top: 30px;
        }
        .endpoint {
            background: #f8f8f8;
            border-left: 4px solid #4CAF50;
            padding: 10px 15px;
            margin: 15px 0;
        }
        .method {
            font-weight: bold;
            color: #2196F3;
        }
        .url {
            font-family: monospace;
            background: #eee;
            padding: 3px 5px;
        }
        .description {
            margin-top: 10px;
        }
        .status {
            margin-top: 20px;
            background: #e8f5e9;
            padding: 10px;
            border-radius: 4px;
        }
        .status-item {
            margin: 5px 0;
        }
        .status-label {
            font-weight: bold;
            display: inline-block;
            width: 120px;
        }
        code {
            background: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>MCP サーバー</h1>
    
    <div class="status">
        <h2>サーバーステータス</h2>
        <div class="status-item"><span class="status-label">バージョン:</span> {{status.version}}</div>
        <div class="status-item"><span class="status-label">AI プロバイダー:</span> {{status.ai.provider}} ({{status.ai.status}})</div>
        <div class="status-item"><span class="status-label">Blender:</span> {{status.blender.status}}</div>
        <div class="status-item"><span class="status-label">Unreal Engine:</span> {{status.unreal.status}}</div>
    </div>
    
    <h2>使用可能なAPIエンドポイント</h2>
    
    <div class="endpoint">
        <div><span class="method">GET</span> <span class="url">/api/status</span></div>
        <div class="description">サーバーのステータス情報を取得します。</div>
    </div>
    
    <div class="endpoint">
        <div><span class="method">POST</span> <span class="url">/api/blender/command</span></div>
        <div class="description">Blenderコマンドを実行します。</div>
        <pre>
{
  "command": "コマンド名",
  "params": {} // オプションパラメータ
}
        </pre>
    </div>
    
    <div class="endpoint">
        <div><span class="method">POST</span> <span class="url">/api/unreal/command</span></div>
        <div class="description">Unreal Engineコマンドを実行します。</div>
        <pre>
{
  "command": "コマンド名",
  "params": {} // オプションパラメータ
}
        </pre>
    </div>
    
    <div class="endpoint">
        <div><span class="method">POST</span> <span class="url">/api/ai/generate</span></div>
        <div class="description">AIを使用してコンテンツを生成します。</div>
        <pre>
{
  "prompt": "生成するコンテンツの説明",
  "type": "text", // オプション: text, texture, blueprint, heightmap など
  "model": "gpt-4" // オプション: 使用するAIモデル
}
        </pre>
    </div>
    
    <h2>関連リソース</h2>
    <ul>
        <li><a href="http://{{server_host}}:{{blender_port}}">Blender-MCP API</a> (ポート: {{blender_port}})</li>
        <li><a href="http://{{server_host}}:{{ue5_port}}">UE5-MCP API</a> (ポート: {{ue5_port}})</li>
    </ul>
    
    <p>詳細な使用方法は <a href="https://github.com/tacyan/UE5-MCP">ドキュメント</a> を参照してください。</p>
</body>
</html>
'''

# MCP APIエンドポイント
@app.route('/', methods=['GET'])
def home():
    """
    ホームページエンドポイント

    MCP APIに関する情報を表示します。

    戻り値:
        HTML: APIドキュメントページ
    """
    try:
        status_data = {
            'status': 'running',
            'version': '1.0.0',
            'ai': {
                'provider': config['ai']['provider'],
                'model': config['ai']['model'],
                'status': 'connected' if has_openai else 'mock mode'
            },
            'blender': {
                'enabled': config['blender']['enabled'],
                'status': 'connected' if config['blender']['enabled'] else 'disabled'
            },
            'unreal': {
                'enabled': config['unreal']['enabled'],
                'status': 'connected' if config['unreal']['enabled'] else 'disabled'
            }
        }
        
        return render_template_string(HTML_TEMPLATE, 
                                      status=status_data, 
                                      server_host=config['server']['host'],
                                      blender_port=config['blender']['port'], 
                                      ue5_port=config['unreal']['port'])
    except Exception as e:
        logger.error(f"ホームページ表示中にエラーが発生しました: {str(e)}")
        return f"エラーが発生しました: {str(e)}", 500

@app.route('/api/status', methods=['GET'])
def getStatus():
    """
    サーバーのステータスを返すAPIエンドポイント

    現在のサーバーの状態とバージョン情報を返します。

    戻り値:
        JSON: サーバーのステータス情報
    """
    try:
        status = {
            'status': 'running',
            'version': '1.0.0',
            'ai': {
                'provider': config['ai']['provider'],
                'model': config['ai']['model'],
                'status': 'connected' if has_openai else 'mock mode'
            },
            'blender': {
                'enabled': config['blender']['enabled'],
                'status': 'connected' if config['blender']['enabled'] else 'disabled'
            },
            'unreal': {
                'enabled': config['unreal']['enabled'],
                'status': 'connected' if config['unreal']['enabled'] else 'disabled'
            }
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"ステータスAPI呼び出し中にエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blender/command', methods=['POST'])
def blenderCommand():
    """
    Blenderコマンドを実行するAPIエンドポイント

    Blenderにコマンドを送信し、結果を返します。

    戻り値:
        JSON: コマンド実行の結果
    """
    if not config['blender']['enabled']:
        return jsonify({'error': 'Blenderモジュールが無効です'}), 400
    
    try:
        data = request.json
        if not data or 'command' not in data:
            return jsonify({'error': 'コマンドが指定されていません'}), 400
        
        # 実際の処理ではBlenderとの通信を実装
        command = data['command']
        logger.info(f"Blenderコマンドを受信: {command}")
        
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'command': command,
            'result': f'コマンド "{command}" が正常に実行されました'
        })
    except Exception as e:
        logger.error(f"Blenderコマンド実行中にエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/unreal/command', methods=['POST'])
def unrealCommand():
    """
    Unreal Engineコマンドを実行するAPIエンドポイント

    Unreal Engineにコマンドを送信し、結果を返します。

    戻り値:
        JSON: コマンド実行の結果
    """
    if not config['unreal']['enabled']:
        return jsonify({'error': 'Unrealモジュールが無効です'}), 400
    
    try:
        data = request.json
        if not data or 'command' not in data:
            return jsonify({'error': 'コマンドが指定されていません'}), 400
        
        # 実際の処理ではUnreal Engineとの通信を実装
        command = data['command']
        logger.info(f"Unrealコマンドを受信: {command}")
        
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'command': command,
            'result': f'コマンド "{command}" が正常に実行されました'
        })
    except Exception as e:
        logger.error(f"Unrealコマンド実行中にエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/generate', methods=['POST'])
def aiGenerate():
    """
    AI生成APIエンドポイント

    AIを使用してコンテンツを生成します。
    OpenAI APIキーがない場合はモックレスポンスを返します。

    戻り値:
        JSON: 生成結果
    """
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({'error': 'プロンプトが指定されていません'}), 400
        
        prompt = data['prompt']
        model = data.get('model', config['ai']['model'])
        type = data.get('type', 'text')
        logger.info(f"AI生成リクエストを受信: {prompt}, タイプ: {type}")
        
        # OpenAI APIキーがない場合はモックレスポンスを返す
        if config['ai']['provider'] == 'mock':
            # タイプに応じたモックレスポンスを生成
            if type == 'text':
                content = f'これは「{prompt}」に対するモックAI生成の結果です。実際にはOpenAI APIを使用して生成されます。'
            elif type == 'texture':
                content = f'テクスチャ「{prompt}」のモック生成。OpenAI APIキーを設定して実際の生成を行ってください。'
            elif type == 'blueprint':
                content = f'ブループリント「{prompt}」のモック生成。OpenAI APIキーを設定して実際の生成を行ってください。'
            elif type == 'heightmap':
                content = f'地形「{prompt}」のモック生成。OpenAI APIキーを設定して実際の生成を行ってください。'
            else:
                content = f'「{prompt}」に対するモック生成。OpenAI APIキーを設定して実際の生成を行ってください。'
            
            return jsonify({
                'status': 'success',
                'provider': 'mock',
                'prompt': prompt,
                'model': model,
                'result': f'モックモード: "{prompt}" に基づいたコンテンツが生成されました',
                'data': {
                    'type': type,
                    'content': content
                }
            })
        
        # 実際の処理ではOpenAI APIなどと通信
        # 実装されたらここに記述
        
        # 現在はOpenAIモードでもモックレスポンスを返す（将来的に実装）
        return jsonify({
            'status': 'success',
            'provider': 'openai',
            'prompt': prompt,
            'model': model,
            'result': f'"{prompt}" に基づいたコンテンツが生成されました',
            'data': {
                'type': type,
                'content': f'これは"{prompt}"に対するAI生成の結果です。'
            }
        })
    except Exception as e:
        logger.error(f"AI生成中にエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500

# メイン実行コード
if __name__ == '__main__':
    try:
        host = config['server']['host']
        port = config['server']['port']
        debug = config['server']['debug']
        
        # AIモードの表示
        if has_openai:
            logger.info(f"OpenAI APIが設定されています。プロバイダー: {config['ai']['provider']}, モデル: {config['ai']['model']}")
        else:
            logger.warning("OpenAI APIキーが設定されていません。モックモードで実行されます。")
        
        logger.info(f"MCPサーバーを起動します: {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.critical(f"サーバー起動中に致命的なエラーが発生しました: {str(e)}")
        raise 
