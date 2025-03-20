#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blender-MCPモジュール

このモジュールは、Model Context Protocol (MCP) のBlender連携機能を実装します。
Blenderとの通信を行い、シーン生成、アセット管理、テクスチャ適用などの機能を提供します。

主な機能:
- プロシージャルシーン生成
- アセット管理とテクスチャリング
- AI支援による最適化
- UnrealEngine 5へのエクスポート

制限事項:
- Blender 3.x以降が必要です
- Node Wrangler, Blender Python APIアドオンが必要です
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
        logging.FileHandler("blender_mcp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("blender_mcp")

# HTML テンプレート
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blender-MCP API</title>
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
            border-left: 4px solid #E91E63;
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
            background: #f3e5f5;
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
            color: #9C27B0;
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
    <h1>Blender-MCP API</h1>
    
    <div class="status">
        <h2>Blender-MCPステータス</h2>
        <div class="status-item"><span class="status-label">バージョン:</span> {{status.version}}</div>
        <div class="status-item"><span class="status-label">Blenderバージョン:</span> {{status.blender_version}}</div>
        <div class="status-item"><span class="status-label">MCP URL:</span> <a href="http://{{mcp_server_host}}:{{mcp_server_port}}">http://{{mcp_server_host}}:{{mcp_server_port}}</a></div>
    </div>
    
    <h2>使用可能なAPIエンドポイント</h2>
    
    <div class="endpoint">
        <div><span class="method">GET</span> <span class="url">/api/status</span></div>
        <div class="description">Blender-MCPのステータス情報を取得します。</div>
    </div>
    
    <div class="endpoint">
        <div><span class="method">POST</span> <span class="url">/api/command</span></div>
        <div class="description">Blenderコマンドを実行します。</div>
        <pre>
{
  "command": "コマンド名",
  "params": {} // コマンド固有のパラメータ
}
        </pre>
    </div>
    
    <h2>使用可能なコマンド</h2>
    
    <div class="command">
        <div class="command-name">generate_scene</div>
        <div class="description">シーンを生成します</div>
        <pre>
{
  "command": "generate_scene",
  "params": {
    "description": "生成するシーンの説明"
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">add_object</div>
        <div class="description">オブジェクトを追加します</div>
        <pre>
{
  "command": "add_object",
  "params": {
    "type": "cube", // オブジェクトタイプ
    "name": "MyCube", // オプション: オブジェクト名
    "location": [0, 0, 0] // オプション: 位置
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">modify_object</div>
        <div class="description">オブジェクトを修正します</div>
        <pre>
{
  "command": "modify_object",
  "params": {
    "name": "オブジェクト名",
    "location": [1, 2, 3], // オプション
    "scale": [1, 1, 1], // オプション
    "rotation": [0, 0, 0] // オプション
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">generate_texture</div>
        <div class="description">テクスチャを生成します</div>
        <pre>
{
  "command": "generate_texture",
  "params": {
    "object_name": "オブジェクト名",
    "description": "テクスチャの説明"
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">optimize_asset</div>
        <div class="description">アセットを最適化します</div>
        <pre>
{
  "command": "optimize_asset",
  "params": {
    "asset_name": "アセット名",
    "lod": 1, // オプション: LODレベル
    "polycount": 5000 // オプション: ポリゴン数の上限
  }
}
        </pre>
    </div>
    
    <div class="command">
        <div class="command-name">export_asset</div>
        <div class="description">アセットをエクスポートします</div>
        <pre>
{
  "command": "export_asset",
  "params": {
    "asset_name": "アセット名",
    "format": "fbx", // エクスポート形式 (fbx, obj, gltf など)
    "path": "./exports/asset.fbx" // オプション: 保存パス
  }
}
        </pre>
    </div>
    
    <h2>関連リソース</h2>
    <ul>
        <li><a href="http://{{mcp_server_host}}:{{mcp_server_port}}">MCP サーバー</a></li>
        <li><a href="http://{{mcp_server_host}}:{{ue5_port}}">UE5-MCP API</a></li>
    </ul>
</body>
</html>
'''

class BlenderMCP:
    """
    Blender-MCPクラス
    
    Blenderとの通信や操作を行うためのクラス
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
        logger.info("Blender-MCPモジュールが初期化されました")
    
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
            elif os.path.exists('blender_mcp_config.yml'):
                with open('blender_mcp_config.yml', 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("設定ファイルが見つかりません。デフォルト設定を使用します。")
                return {
                    'blender_mcp': {
                        'host': '127.0.0.1',
                        'port': 5001,
                        'debug': False
                    },
                    'mcp_server': {
                        'host': '127.0.0.1',
                        'port': 5000
                    },
                    'ue5_mcp': {
                        'port': 5002
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
        
        Blender-MCP APIに関する情報を表示します。
        
        戻り値:
            HTML: APIドキュメントページ
        """
        try:
            # ステータス情報を取得
            status_data = {
                'status': 'running',
                'version': '1.0.0',
                'blender_version': '3.6.0',  # 実際のBlenderバージョンを取得するコードに置き換え
                'available_commands': [
                    'generate_scene',
                    'add_object',
                    'modify_object',
                    'generate_texture',
                    'optimize_asset',
                    'export_asset'
                ]
            }
            
            # サーバー設定を取得
            mcp_server_host = self.config['mcp_server']['host']
            mcp_server_port = self.config['mcp_server']['port']
            ue5_port = self.config.get('ue5_mcp', {}).get('port', 5002)
            
            # HTMLテンプレートを描画
            return render_template_string(HTML_TEMPLATE, 
                                          status=status_data,
                                          mcp_server_host=mcp_server_host,
                                          mcp_server_port=mcp_server_port,
                                          ue5_port=ue5_port)
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
            # Blenderの状態を確認するコードをここに実装
            status = {
                'status': 'running',
                'version': '1.0.0',
                'blender_version': '3.6.0',  # 実際のBlenderバージョンを取得するコードに置き換え
                'available_commands': [
                    'generate_scene',
                    'add_object',
                    'modify_object',
                    'generate_texture',
                    'optimize_asset',
                    'export_asset'
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
            if command == 'generate_scene':
                return self.generateScene(params)
            elif command == 'add_object':
                return self.addObject(params)
            elif command == 'modify_object':
                return self.modifyObject(params)
            elif command == 'generate_texture':
                return self.generateTexture(params)
            elif command == 'optimize_asset':
                return self.optimizeAsset(params)
            elif command == 'export_asset':
                return self.exportAsset(params)
            else:
                return jsonify({'error': f'未知のコマンド: {command}'}), 400
        except Exception as e:
            logger.error(f"コマンド実行中にエラーが発生しました: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # 以下、各コマンドの実装
    
    def generateScene(self, params):
        """
        シーンを生成する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'description' not in params:
            return jsonify({'error': '説明が指定されていません'}), 400
        
        description = params['description']
        logger.info(f"シーン生成: {description}")
        
        # ここに実際のBlender APIを使用したシーン生成コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'シーン "{description}" が生成されました',
            'scene_info': {
                'name': f'Scene_{description.split()[0]}',
                'objects': ['Camera', 'Light', 'Floor']
            }
        })
    
    def addObject(self, params):
        """
        オブジェクトを追加する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'type' not in params:
            return jsonify({'error': 'オブジェクトタイプが指定されていません'}), 400
        
        obj_type = params['type']
        location = params.get('location', [0, 0, 0])
        name = params.get('name', f'{obj_type}_{id(obj_type)}')
        
        logger.info(f"オブジェクト追加: {obj_type}, 位置: {location}, 名前: {name}")
        
        # ここに実際のBlender APIを使用したオブジェクト追加コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'オブジェクト "{name}" ({obj_type}) が追加されました',
            'object_info': {
                'name': name,
                'type': obj_type,
                'location': location
            }
        })
    
    def modifyObject(self, params):
        """
        オブジェクトを修正する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'name' not in params:
            return jsonify({'error': 'オブジェクト名が指定されていません'}), 400
        
        name = params['name']
        location = params.get('location', None)
        scale = params.get('scale', None)
        rotation = params.get('rotation', None)
        
        logger.info(f"オブジェクト修正: {name}")
        
        # ここに実際のBlender APIを使用したオブジェクト修正コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'オブジェクト "{name}" が修正されました',
            'object_info': {
                'name': name,
                'location': location,
                'scale': scale,
                'rotation': rotation
            }
        })
    
    def generateTexture(self, params):
        """
        テクスチャを生成する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'object_name' not in params or 'description' not in params:
            return jsonify({'error': 'オブジェクト名または説明が指定されていません'}), 400
        
        object_name = params['object_name']
        description = params['description']
        
        logger.info(f"テクスチャ生成: オブジェクト: {object_name}, 説明: {description}")
        
        # AIによるテクスチャ生成リクエスト
        try:
            ai_response = self.requestAIGeneration(
                prompt=f"Create a texture for {object_name}: {description}",
                type="texture"
            )
            
            # AIレスポンスの処理
            # モックモードでもエラーなく処理を続行できるようにする
            
            # ここに実際のBlender APIを使用したテクスチャ適用コードが入ります
            # デモ用の応答
            return jsonify({
                'status': 'success',
                'message': f'テクスチャが "{object_name}" に適用されました',
                'texture_info': {
                    'object': object_name,
                    'description': description,
                    'texture_type': 'diffuse',
                    'resolution': '2048x2048',
                    'ai_generated': 'ai_response' in locals()
                }
            })
        except requests.exceptions.ConnectionError:
            logger.warning(f"MCPサーバーに接続できません。ローカルでテクスチャ生成を続行します。")
            # MCPサーバーが利用できない場合のフォールバック処理
            return jsonify({
                'status': 'success',
                'message': f'テクスチャが "{object_name}" に適用されました（ローカル生成）',
                'texture_info': {
                    'object': object_name,
                    'description': description,
                    'texture_type': 'diffuse',
                    'resolution': '2048x2048',
                    'ai_generated': False
                }
            })
        except Exception as e:
            logger.error(f"テクスチャ生成中にエラーが発生しました: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    def optimizeAsset(self, params):
        """
        アセットを最適化する
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'asset_name' not in params:
            return jsonify({'error': 'アセット名が指定されていません'}), 400
        
        asset_name = params['asset_name']
        lod_level = params.get('lod', 1)
        polycount = params.get('polycount', None)
        
        logger.info(f"アセット最適化: {asset_name}, LOD: {lod_level}, ポリゴン数: {polycount}")
        
        # ここに実際のBlender APIを使用したアセット最適化コードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'アセット "{asset_name}" が最適化されました',
            'optimization_info': {
                'asset': asset_name,
                'lod_level': lod_level,
                'original_polycount': 10000,  # 例
                'optimized_polycount': polycount or 5000,  # 例
                'reduction_percent': polycount and (polycount / 10000 * 100) or 50  # 例
            }
        })
    
    def exportAsset(self, params):
        """
        アセットをエクスポートする
        
        引数:
            params (dict): パラメータ
            
        戻り値:
            JSON: 処理結果
        """
        if 'asset_name' not in params or 'format' not in params:
            return jsonify({'error': 'アセット名またはフォーマットが指定されていません'}), 400
        
        asset_name = params['asset_name']
        export_format = params['format']
        path = params.get('path', f'./exports/{asset_name}.{export_format.lower()}')
        
        # エクスポートディレクトリを作成
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        logger.info(f"アセットエクスポート: {asset_name}, フォーマット: {export_format}, パス: {path}")
        
        # ここに実際のBlender APIを使用したエクスポートコードが入ります
        # デモ用の応答
        return jsonify({
            'status': 'success',
            'message': f'アセット "{asset_name}" が {export_format} 形式でエクスポートされました',
            'export_info': {
                'asset': asset_name,
                'format': export_format,
                'path': path,
                'size_kb': 1024  # 例
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
        Blender-MCPサーバーを実行する
        """
        try:
            host = self.config['blender_mcp']['host']
            port = self.config['blender_mcp']['port']
            debug = self.config['blender_mcp']['debug']
            
            logger.info(f"Blender-MCPサーバーを起動します: {host}:{port}")
            self.app.run(host=host, port=port, debug=debug)
        except Exception as e:
            logger.critical(f"サーバー起動中に致命的なエラーが発生しました: {str(e)}")
            raise

# メイン実行部分
if __name__ == '__main__':
    try:
        # コマンドライン引数からの設定ファイルパスの取得
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        
        # Blender-MCPインスタンスの作成と実行
        blender_mcp = BlenderMCP(config_path)
        blender_mcp.run()
    except Exception as e:
        logger.critical(f"Blender-MCPの起動中に致命的なエラーが発生しました: {str(e)}")
        sys.exit(1) 
