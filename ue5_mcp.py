#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5-MCPモジュール

このモジュールは、Model Context Protocol (MCP) のUnreal Engine 5連携機能を実装します。
UE5との通信を行い、レベルデザイン、Blueprint自動化、デバッグなどの機能を提供します。

主な機能:
- UE5 Python APIとBlueprintsを使用した自動化
- AI駆動のツールによる地形生成、植生配置、環境構築
- Blenderからのアセット移行

制限事項:
- Unreal Engine 5.1以降が必要です
- Python Editor Script Pluginが有効になっている必要があります
- UnrealCV Pluginが必要です
- Procedural Content Generation (PCG) Frameworkが必要です
"""

import os
import sys
import logging
import json
import requests
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
        logging.FileHandler("ue5_mcp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ue5_mcp")

# HTML テンプレート
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UE5-MCP API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #0050b3;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #0050b3;
            margin-top: 30px;
        }
        .endpoint {
            background: #f8f8f8;
            border-left: 4px solid #0050b3;
            padding: 10px 15px;
            margin: 15px 0;
        }
        .method {
            font-weight: bold;
            color: #0050b3;
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
            background: #e6f7ff;
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
        .command {
            background: #f5f5f5;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }
        .command-name {
            font-weight: bold;
            color: #0050b3;
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
    <h1>UE5-MCP API</h1>
    
    <div class="status">
        <h2>UE5-MCPステータス</h2>
        <div class="status-item"><span class="status-label">バージョン:</span> {{status.version}}</div>
        <div class="status-item"><span class="status-label">UE5バージョン:</span> {{status.ue_version}}</div>
        <div class="status-item"><span class="status-label">MCP URL:</span> <a href="http://{{mcp_server_host}}:{{mcp_server_port}}">http://{{mcp_server_host}}:{{mcp_server_port}}</a></div>
    </div>
    
    <h2>使用可能なAPIエンドポイント</h2>
    
    <div class="endpoint">
        <div><span class="method">GET</span> <span class="url">/api/status</span></div>
        <div class="description">UE5-MCPのステータス情報を取得します。</div>
    </div>
    
    <div class="endpoint">
        <div><span class="method">POST</span> <span class="url">/api/command</span></div>
        <div class="description">UE5コマンドを実行します。</div>
        <pre>
{
  "command": "コマンド名",
  "params": {} // コマンド固有のパラメータ
}
        </pre>
    </div>
    
    <h2>使用可能なコマンド</h2>
    
    <div class="command">
        <div class="command-name">create_level</div>
        <div class="description">新しいレベルを作成します</div>
        <pre>
{
  "command": "create_level",
  "params": {
    "name": "レベル名",
    "template": "Empty" // オプション: レベルテンプレート
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">import_asset</div>
        <div class="description">アセットをインポートします</div>
        <pre>
{
  "command": "import_asset",
  "params": {
    "path": "アセットパス",
    "destination": "/Game/Assets" // オプション: インポート先
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">create_blueprint</div>
        <div class="description">Blueprintを作成します</div>
        <pre>
{
  "command": "create_blueprint",
  "params": {
    "name": "Blueprint名",
    "class": "クラス名",
    "description": "説明", // オプション
    "ai_generate": true, // オプション: AI生成を使用するか
    "path": "/Game/Blueprints" // オプション: 保存先
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">generate_terrain</div>
        <div class="description">地形を生成します</div>
        <pre>
{
  "command": "generate_terrain",
  "params": {
    "size": 1024, // 地形サイズ
    "resolution": 1.0, // オプション: 解像度
    "height_map": "height_map.png", // オプション: 高さマップパス
    "description": "山岳地帯" // オプション: AI生成用の説明
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">place_foliage</div>
        <div class="description">植生を配置します</div>
        <pre>
{
  "command": "place_foliage",
  "params": {
    "foliage_type": "植生タイプ",
    "density": 1.0, // オプション: 密度
    "area": [0, 0, 1000, 1000] // オプション: 配置エリア [x, y, width, height]
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">build_lighting</div>
        <div class="description">ライティングをビルドします</div>
        <pre>
{
  "command": "build_lighting",
  "params": {
    "quality": "Production" // オプション: ビルド品質
  }
}
        </pre>
    </div>
    
    <h2>関連リソース</h2>
    <ul>
        <li><a href="http://{{mcp_server_host}}:{{mcp_server_port}}">MCP サーバー</a></li>
        <li><a href="http://{{mcp_server_host}}:{{blender_port}}">Blender-MCP API</a></li>
    </ul>
</body>
</html>
'''

class UE5MCP:
    """
    UE5-MCPクラス
    
    Unreal Engine 5との通信や操作を行うためのクラス
    """
    
    def __init__(self, config_path=None):
        """
        初期化メソッド
        
        引数:
            config_path (str): 設定ファイルのパス
        """
        self.config = self.loadConfig(config_path)
        self.app = Flask(__name__)
        self.setupRoutes()
        self.mcp_server_url = f"http://{self.config['mcp_server']['host']}:{self.config['mcp_server']['port']}"
        logger.info("UE5-MCPモジュールが初期化されました")
    
    def loadConfig(self, config_path=None):
        """
        設定ファイルを読み込む
        
        引数:
            config_path (str): 設定ファイルのパス
            
        戻り値:
            dict: 設定情報
        """
        try:
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            elif os.path.exists('ue5_mcp_config.yml'):
                with open('ue5_mcp_config.yml', 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("設定ファイルが見つかりません。デフォルト設定を使用します。")
                return {
                    'ue5_mcp': {
                        'host': '127.0.0.1',
                        'port': 5002,
                        'debug': False
                    },
                    'mcp_server': {
                        'host': '127.0.0.1',
                        'port': 5000
                    },
                    'blender_mcp': {
                        'port': 5001
                    }
                }
        except Exception as e:
            logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {str(e)}")
            raise
    
    def setupRoutes(self):
        """
        Flaskルートの設定
        """
        self.app.route('/')(self.home)
        self.app.route('/api/status', methods=['GET'])(self.getStatus)
        self.app.route('/api/command', methods=['POST'])(self.executeCommand)
    
    def home(self):
        """
        ホームページエンドポイント
        
        UE5-MCP APIに関する情報を表示します。
        
        戻り値:
            HTML: APIドキュメントページ
        """
        try:
            # ステータス情報を取得
            status_data = {
                'status': 'running',
                'version': '1.0.0',
                'ue_version': '5.3',  # 実際のUE5バージョンを取得するコードに置き換え
                'available_commands': [
                    'create_level',
                    'import_asset',
                    'create_blueprint',
                    'generate_terrain',
                    'place_foliage',
                    'build_lighting'
                ]
            }
            
            # サーバー設定を取得
            mcp_server_host = self.config['mcp_server']['host']
            mcp_server_port = self.config['mcp_server']['port']
            blender_port = self.config.get('blender_mcp', {}).get('port', 5001)
            
            # HTMLテンプレートを描画
            return render_template_string(HTML_TEMPLATE, 
                                         status=status_data,
                                         mcp_server_host=mcp_server_host,
                                         mcp_server_port=mcp_server_port,
                                         blender_port=blender_port)
        except Exception as e:
            logger.error(f"ホームページ表示中にエラーが発生しました: {str(e)}")
            return f"エラーが発生しました: {str(e)}", 500
    
    def getStatus(self):
        """
        ステータスを取得するAPIエンドポイント
        
        戻り値:
            JSON: ステータス情報
        """
        try:
            # UE5の状態を確認するコードをここに実装
            status = {
                'status': 'running',
                'version': '1.0.0',
                'ue_version': '5.3',  # 実際のUE5バージョンを取得するコードに置き換え
                'available_commands': [
                    'create_level',
                    'import_asset',
                    'create_blueprint',
                    'generate_terrain',
                    'place_foliage',
                    'build_lighting'
                ]
            }
            return jsonify(status)
        except Exception as e:
            logger.error(f"ステータス取得中にエラーが発生しました: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    def executeCommand(self):
        """
        コマンドを実行するAPIエンドポイント
        
        戻り値:
            JSON: コマンド実行結果
        """
        try:
            data = request.json
            if not data or 'command' not in data:
                return jsonify({'error': 'コマンドが指定されていません'}), 400
            
            command = data['command']
            params = data.get('params', {})
            logger.info(f"コマンドを受信: {command}, パラメータ: {params}")
            
            # コマンドの実行
            if command == 'create_level':
                return self.createLevel(params)
            elif command == 'import_asset':
                return self.importAsset(params)
            elif command == 'create_blueprint':
                return self.createBlueprint(params)
            elif command == 'generate_terrain':
                return self.generateTerrain(params)
            elif command == 'place_foliage':
                return self.placeFoliage(params)
            elif command == 'build_lighting':
                return self.buildLighting(params)
            else:
                return jsonify({'error': f'未知のコマンド: {command}'}), 400
        except Exception as e:
            logger.error(f"コマンド実行中にエラーが発生しました: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # 以下、各コマンドの実装
    
    def createLevel(self, params):
        """
        レベルを作成する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'name' not in params:
            return jsonify({'error': 'レベル名が指定されていません'}), 400
        
        name = params['name']
        template = params.get('template', 'Empty')
        logger.info(f"レベル作成: {name}, テンプレート: {template}")
        
        # ここに実際のUE5 APIを使用したレベル作成コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'レベル "{name}" が作成されました',
            'level_info': {
                'name': name,
                'template': template,
                'path': f'/Game/Levels/{name}'
            }
        })
    
    def importAsset(self, params):
        """
        アセットをインポートする
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'path' not in params:
            return jsonify({'error': 'アセットパスが指定されていません'}), 400
        
        path = params['path']
        destination = params.get('destination', '/Game/Assets')
        logger.info(f"アセットインポート: {path}, 保存先: {destination}")
        
        # ファイルが存在するか確認
        if not os.path.exists(path):
            logger.warning(f"インポートするファイルが見つかりません: {path}")
            return jsonify({
                'status': 'error',
                'message': f'ファイルが見つかりません: {path}'
            }), 404
        
        # ここに実際のUE5 APIを使用したアセットインポートコードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'アセット "{os.path.basename(path)}" がインポートされました',
            'asset_info': {
                'source_path': path,
                'destination': destination,
                'asset_name': os.path.splitext(os.path.basename(path))[0],
                'asset_path': f"{destination}/{os.path.splitext(os.path.basename(path))[0]}"
            }
        })
    
    def createBlueprint(self, params):
        """
        Blueprintを作成する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'name' not in params or 'class' not in params:
            return jsonify({'error': 'Blueprint名またはクラスが指定されていません'}), 400
        
        name = params['name']
        blueprint_class = params['class']
        path = params.get('path', '/Game/Blueprints')
        description = params.get('description', '')
        
        logger.info(f"Blueprint作成: {name}, クラス: {blueprint_class}")
        
        # AI生成の場合、AIに処理を依頼
        if 'ai_generate' in params and params['ai_generate']:
            try:
                ai_response = self.requestAIGeneration(
                    prompt=f"Create a Blueprint named {name} of class {blueprint_class} that does the following: {description}",
                    type="blueprint"
                )
                # AI生成の応答処理
                # モックモードでもエラーなく処理を続行できるようにする
            except Exception as e:
                # エラーをログに記録するが、処理は続行する
                logger.warning(f"Blueprint AI生成中にエラーが発生しましたが、処理を続行します: {str(e)}")
        
        # ここに実際のUE5 APIを使用したBlueprint作成コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'Blueprint "{name}" が作成されました',
            'blueprint_info': {
                'name': name,
                'class': blueprint_class,
                'path': f"{path}/{name}",
                'description': description,
                'ai_generated': 'ai_response' in locals()
            }
        })
    
    def generateTerrain(self, params):
        """
        地形を生成する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'size' not in params:
            return jsonify({'error': '地形サイズが指定されていません'}), 400
        
        size = params['size']
        resolution = params.get('resolution', 1.0)
        height_map = params.get('height_map', None)
        description = params.get('description', None)
        
        logger.info(f"地形生成: サイズ: {size}, 解像度: {resolution}")
        
        # AI生成の地形の場合
        height_map_generated = False
        if description and not height_map:
            try:
                ai_response = self.requestAIGeneration(
                    prompt=f"Generate a terrain heightmap based on the description: {description}",
                    type="heightmap"
                )
                # AI生成の応答から地形データを取得（実装はダミー）
                height_map = "ai_generated_heightmap.png"  # 実際には生成された画像のパス
                height_map_generated = True
            except Exception as e:
                # エラーをログに記録するが、処理は続行する
                logger.warning(f"地形AI生成中にエラーが発生しましたが、処理を続行します: {str(e)}")
                height_map = "default_heightmap.png"
        
        # ここに実際のUE5 APIを使用した地形生成コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': '地形が生成されました',
            'terrain_info': {
                'size': size,
                'resolution': resolution,
                'height_map': height_map,
                'description': description,
                'ai_generated': height_map_generated
            }
        })
    
    def placeFoliage(self, params):
        """
        植生を配置する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'foliage_type' not in params:
            return jsonify({'error': '植生タイプが指定されていません'}), 400
        
        foliage_type = params['foliage_type']
        density = params.get('density', 1.0)
        area = params.get('area', [0, 0, 1000, 1000])  # [x, y, width, height]
        
        logger.info(f"植生配置: タイプ: {foliage_type}, 密度: {density}")
        
        # ここに実際のUE5 APIを使用した植生配置コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'植生 "{foliage_type}" が配置されました',
            'foliage_info': {
                'type': foliage_type,
                'density': density,
                'area': area,
                'instances': int(density * area[2] * area[3] / 10000)  # 概算の配置数
            }
        })
    
    def buildLighting(self, params):
        """
        ライティングをビルドする
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        quality = params.get('quality', 'Production')
        logger.info(f"ライティングビルド: 品質: {quality}")
        
        # ここに実際のUE5 APIを使用したライティングビルドコードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': 'ライティングがビルドされました',
            'build_info': {
                'quality': quality,
                'duration_seconds': 120,  # 仮の所要時間
                'status': 'completed'
            }
        })
    
    def requestAIGeneration(self, prompt, type="text"):
        """
        AIによる生成を要求する
        
        引数:
            prompt (str): 生成プロンプト
            type (str): 生成タイプ
            
        戻り値:
            dict: AI生成結果
        """
        try:
            url = f"{self.mcp_server_url}/api/ai/generate"
            data = {
                'prompt': prompt,
                'type': type
            }
            
            logger.info(f"MCPサーバーにAI生成要求を送信: {prompt}")
            response = requests.post(url, json=data, timeout=10)  # タイムアウトを設定
            
            if response.status_code == 200:
                logger.info("AI生成が成功しました")
                return response.json()
            else:
                logger.warning(f"AI生成要求中にサーバーエラーが発生しました: {response.text}")
                # エラーでも処理を続行できるようにレスポンスを返す
                return {
                    'status': 'error',
                    'provider': 'fallback',
                    'prompt': prompt,
                    'result': f'エラーが発生しましたが、処理を続行します',
                    'data': {
                        'type': type,
                        'content': f'フォールバックコンテンツ: {prompt}'
                    }
                }
        except requests.exceptions.RequestException as e:
            logger.warning(f"MCPサーバーへのリクエスト中にエラーが発生しました: {str(e)}")
            # リクエストエラーでも処理を続行できるようにレスポンスを返す
            return {
                'status': 'error',
                'provider': 'fallback',
                'prompt': prompt,
                'result': f'サーバー接続エラーが発生しましたが、処理を続行します',
                'data': {
                    'type': type,
                    'content': f'フォールバックコンテンツ: {prompt}'
                }
            }
        except Exception as e:
            logger.error(f"AI生成要求中に予期しないエラーが発生しました: {str(e)}")
            # その他のエラーでも処理を続行できるようにレスポンスを返す
            return {
                'status': 'error',
                'provider': 'fallback',
                'prompt': prompt,
                'result': f'予期しないエラーが発生しましたが、処理を続行します',
                'data': {
                    'type': type,
                    'content': f'フォールバックコンテンツ: {prompt}'
                }
            }
    
    def run(self):
        """
        UE5-MCPサーバーを実行する
        """
        try:
            host = self.config['ue5_mcp']['host']
            port = self.config['ue5_mcp']['port']
            debug = self.config['ue5_mcp']['debug']
            
            logger.info(f"UE5-MCPサーバーを起動します: {host}:{port}")
            self.app.run(host=host, port=port, debug=debug)
        except Exception as e:
            logger.critical(f"サーバー起動中に致命的なエラーが発生しました: {str(e)}")
            raise

# メイン実行部分
if __name__ == '__main__':
    try:
        # コマンドライン引数からの設定ファイルパスの取得
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        
        # UE5-MCPインスタンスの作成と実行
        ue5_mcp = UE5MCP(config_path)
        ue5_mcp.run()
    except Exception as e:
        logger.critical(f"UE5-MCPの起動中に致命的なエラーが発生しました: {str(e)}")
        sys.exit(1) 
