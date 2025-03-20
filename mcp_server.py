#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPサーバー

MCPシステムの中核となるサーバーアプリケーションです。
BlenderとUE5のモジュールとの通信を管理し、APIエンドポイントを提供します。
"""

import os
import sys
import json
import time
import logging
import platform
import importlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_server")

# サーバー設定
SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# Flaskアプリ初期化
app = Flask(__name__)
CORS(app)

# AIサービスの設定
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# AI利用可能フラグ
ai_available = False

# OpenAI APIが設定されているか確認
if OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        ai_available = True
        logger.info(f"OpenAI APIが設定されています。プロバイダー: {AI_PROVIDER}, モデル: {AI_MODEL}")
    except ImportError:
        logger.warning("openaiモジュールがインストールされていません。AIアシスト機能は無効化されます。")
else:
    logger.warning("OpenAI APIキーが設定されていません。AIアシスト機能は無効化されます。")

# ステータスエンドポイント
@app.route("/status", methods=["GET"])
@app.route("/api/status", methods=["GET"])
def get_status():
    """システムのステータスを取得する"""
    system_info = {
        "status": "running",
        "version": "1.0.0",
        "system": {
            "os": platform.system(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "is_windows": platform.system() == "Windows",
            "is_mac": platform.system() == "Darwin",
            "is_linux": platform.system() == "Linux"
        },
        "ai": {
            "provider": AI_PROVIDER,
            "model": AI_MODEL,
            "status": "connected" if ai_available else "disconnected"
        },
        "blender": {
            "enabled": os.getenv("BLENDER_ENABLED", "true").lower() == "true",
            "status": "connected"  # 仮の値、実際には確認ロジックが必要
        },
        "unreal": {
            "enabled": os.getenv("UE5_ENABLED", "true").lower() == "true",
            "status": "connected"  # 仮の値、実際には確認ロジックが必要
        }
    }
    return jsonify(system_info)

# Blenderコマンド実行エンドポイント
@app.route("/blender/command", methods=["POST"])
@app.route("/api/blender/command", methods=["POST"])
@app.route("/api/blender/execute", methods=["POST"])
def execute_blender_command():
    """Blenderコマンドを実行する"""
    data = request.json
    command = data.get("command")
    params = data.get("params", {})
    
    logger.info(f"Blenderコマンド受信: {command}, パラメータ: {params}")
    
    # ここでBlenderモジュールと通信するコードを実装
    # 実装例: モック応答
    response = {
        "status": "success",
        "command": command,
        "result": {
            "message": "コマンドが正常に実行されました",
            "data": params
        }
    }
    
    return jsonify(response)

# UE5コマンド実行エンドポイント
@app.route("/unreal/command", methods=["POST"])
@app.route("/api/unreal/command", methods=["POST"])
@app.route("/api/unreal/execute", methods=["POST"])
def execute_unreal_command():
    """UE5コマンドを実行する"""
    data = request.json
    command = data.get("command")
    params = data.get("params", {})
    
    logger.info(f"UE5コマンド受信: {command}, パラメータ: {params}")
    
    # モックレスポンスを詳細化
    mock_responses = {
        "import_asset": {
            "status": "success",
            "command": command,
            "result": {
                "message": f"アセット '{params.get('path', '')}' を '{params.get('destination', '')}' にインポートしました",
                "data": params,
                "asset_info": {
                    "path": params.get("destination", ""),
                    "name": os.path.basename(params.get("path", "unknown")).split(".")[0]
                }
            }
        },
        "place_actor": {
            "status": "success",
            "command": command,
            "result": {
                "message": f"アクター '{params.get('blueprint', params.get('type', 'Actor'))}' を配置しました",
                "data": params,
                "actor_info": {
                    "name": params.get("name", "Actor"),
                    "location": params.get("location", [0, 0, 0]),
                    "rotation": params.get("rotation", [0, 0, 0]),
                    "scale": params.get("scale", [1, 1, 1])
                }
            }
        },
        "create_level": {
            "status": "success",
            "command": command,
            "result": {
                "message": f"レベル '{params.get('name', 'NewLevel')}' を作成しました",
                "data": params,
                "level_info": {
                    "name": params.get("name", "NewLevel"),
                    "template": params.get("template", "Default")
                }
            }
        },
        "create_blueprint": {
            "status": "success",
            "command": command,
            "result": {
                "message": f"ブループリント '{params.get('name', 'NewBlueprint')}' を作成しました",
                "data": params,
                "blueprint_info": {
                    "name": params.get("name", "NewBlueprint"),
                    "parent_class": params.get("parent_class", "Actor")
                }
            }
        },
        "set_game_mode": {
            "status": "success",
            "command": command,
            "result": {
                "message": f"ゲームモード '{params.get('game_mode', 'GameModeBase')}' を設定しました",
                "data": params
            }
        },
        "save_level": {
            "status": "success",
            "command": command,
            "result": {
                "message": "レベルを保存しました",
                "data": params
            }
        }
    }
    
    # コマンドに対応するモックレスポンスを返す
    response = mock_responses.get(command, {
        "status": "success",
        "command": command,
        "result": {
            "message": f"コマンド '{command}' が正常に実行されました",
            "data": params
        }
    })
    
    return jsonify(response)

# AI生成エンドポイント
@app.route("/api/ai/generate", methods=["POST"])
def generate_ai_content():
    """OpenAI APIを使用してコンテンツを生成する"""
    data = request.json
    prompt = data.get("prompt", "")
    content_type = data.get("type", "text")
    
    logger.info(f"AI生成リクエストを受信: {prompt}, タイプ: {content_type}")
    
    if not ai_available:
        return jsonify({
            "status": "error",
            "message": "AI機能が利用できません。OpenAI APIキーを設定してください。"
        }), 400
    
    try:
        # OpenAI APIを使用してコンテンツを生成
        try:
            # 新しいAPIスタイル (openai >= 1.0.0)
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": f"You are an expert game developer assistant that helps create content for games. Generate {content_type} based on the user's request."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
                content = response.choices[0].message.content
            except (ImportError, AttributeError):
                # 旧APIスタイル (openai < 1.0.0)
                response = openai.ChatCompletion.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": f"You are an expert game developer assistant that helps create content for games. Generate {content_type} based on the user's request."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
                content = response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API呼び出しエラー: {str(e)}")
            # フォールバックモード: モック応答
            logger.warning("モック応答を使用します")
            content = f"This is a mock response for: {prompt}"
        
        # コンテンツタイプに応じた処理
        result = {}
        if content_type == "blueprint":
            # Blueprintの場合はJSON形式に変換
            try:
                result = {
                    "name": data.get("params", {}).get("name", "Blueprint"),
                    "parent": data.get("params", {}).get("parent_class", "Actor"),
                    "description": data.get("params", {}).get("description", ""),
                    "script": content,
                    "components": [],
                    "variables": []
                }
            except:
                result = {"script": content}
        else:
            # その他のタイプはテキストとして処理
            result = {"text": content}
        
        return jsonify({
            "status": "success",
            "type": content_type,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"AI生成中にエラーが発生しました: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"AI生成エラー: {str(e)}"
        }), 500

# メイン処理
if __name__ == "__main__":
    logger.info(f"実行環境: {platform.system()} ({platform.platform()})")
    logger.info(f"Python バージョン: {platform.python_version()}")
    
    if ai_available:
        logger.info(f"OpenAI APIが設定されています。プロバイダー: {AI_PROVIDER}, モデル: {AI_MODEL}")
    else:
        logger.warning("OpenAI API設定が見つからないか、無効です。AIアシスト機能は利用できません。")
    
    if MOCK_MODE:
        logger.info("モックモードが有効: UE5/Blenderの実際の接続をシミュレートします")
    
    server_host = SERVER_HOST
    server_port = 8080  # 直接8080ポートを使用
    debug_mode = DEBUG_MODE
    
    logger.info(f"MCPサーバーを起動します: {server_host}:{server_port}")
    app.run(host=server_host, port=server_port, debug=debug_mode) 
