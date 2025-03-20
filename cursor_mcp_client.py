#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPクライアント for Cursor

このスクリプトは、Cursor IDEからMCPサーバーに接続し、APIを呼び出すためのクライアントを提供します。
コード自動生成、補完、自然言語からのコマンド実行など、AI駆動の開発機能をCursorに提供します。

主な機能:
- MCPサーバーとの接続
- APIリクエストの送信
- レスポンス処理
- エラーハンドリング

制限事項:
- MCPサーバーが実行されていることが前提です
- Cursorの拡張機能として使用する場合は、Cursorの要件に合わせて調整が必要です
"""

import requests
import json
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cursor_mcp_client")

class CursorMCPClient:
    """
    Cursor MCP クライアントクラス
    
    MCPサーバーとの通信を処理するクラス
    """
    
    def __init__(self, server_host="127.0.0.1", server_port=8000):
        """
        初期化メソッド
        
        引数:
            server_host (str): MCPサーバーのホスト
            server_port (int): MCPサーバーのポート
        """
        self.server_url = f"http://{server_host}:{server_port}"
        logger.info(f"MCPサーバーURL: {self.server_url}")
    
    def check_server_status(self):
        """
        サーバーのステータスを確認する
        
        戻り値:
            dict: サーバーのステータス情報
        """
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"サーバーステータス確認中にエラーが発生しました: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def generate_ai_content(self, prompt, content_type="text"):
        """
        AIコンテンツを生成する
        
        引数:
            prompt (str): 生成するコンテンツの説明
            content_type (str): コンテンツタイプ
            
        戻り値:
            dict: 生成されたコンテンツの情報
        """
        try:
            data = {
                "prompt": prompt,
                "type": content_type
            }
            response = requests.post(
                f"{self.server_url}/api/ai/generate", 
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"AI生成中にエラーが発生しました: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def execute_blender_command(self, command, params=None):
        """
        Blenderコマンドを実行する
        
        引数:
            command (str): 実行するコマンド
            params (dict): コマンドパラメータ
            
        戻り値:
            dict: コマンド実行結果
        """
        try:
            data = {
                "command": command,
                "params": params or {}
            }
            response = requests.post(
                f"{self.server_url}/api/blender/command", 
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Blenderコマンド実行中にエラーが発生しました: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def execute_unreal_command(self, command, params=None):
        """
        Unrealコマンドを実行する
        
        引数:
            command (str): 実行するコマンド
            params (dict): コマンドパラメータ
            
        戻り値:
            dict: コマンド実行結果
        """
        try:
            data = {
                "command": command,
                "params": params or {}
            }
            response = requests.post(
                f"{self.server_url}/api/unreal/command", 
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Unrealコマンド実行中にエラーが発生しました: {str(e)}")
            return {"status": "error", "error": str(e)}


# 使用例
if __name__ == "__main__":
    client = CursorMCPClient()
    
    # サーバーステータスの確認
    status = client.check_server_status()
    logger.info(f"サーバーステータス: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # AI生成の例
    prompt = "ゲームのメインキャラクターの設定を考えてください"
    ai_result = client.generate_ai_content(prompt)
    logger.info(f"AI生成結果: {json.dumps(ai_result, indent=2, ensure_ascii=False)}")
    
    # Blenderコマンドの例
    blender_result = client.execute_blender_command("add_object", {"type": "cube", "name": "MyCube"})
    logger.info(f"Blender実行結果: {json.dumps(blender_result, indent=2, ensure_ascii=False)}")
    
    # Unrealコマンドの例
    unreal_result = client.execute_unreal_command("create_blueprint", {"name": "GameCharacter", "class": "Character"})
    logger.info(f"Unreal実行結果: {json.dumps(unreal_result, indent=2, ensure_ascii=False)}") 
