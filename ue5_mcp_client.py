#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5-MCPクライアントモジュール

このモジュールは、MCPサーバーと通信して、BlenderおよびUE5との
連携を行うためのクライアントクラスを提供します。

主な機能:
- MCPサーバーへの接続
- Blenderコマンドの実行
- UE5コマンドの実行
- AI機能の利用
"""

import requests
import json
import os
import sys
import logging
import time
from typing import Dict, Any, List, Optional, Union

# ロギングの設定
logger = logging.getLogger("ue5_mcp_client")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class UE5MCPClient:
    """
    MCPサーバーと通信するクライアントクラス
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        """
        クライアントを初期化する
        
        引数:
            host (str): MCPサーバーのホスト
            port (int): MCPサーバーのポート
        """
        self.base_url = f"http://{host}:{port}"
        self.unreal_version = "Unknown"
        
        try:
            # Unrealモジュールがある場合は、バージョンを取得
            if 'unreal' in sys.modules:
                import unreal
                self.unreal_version = unreal.SystemLibrary.get_engine_version()
        except:
            pass
            
        logger.info(f"MCPサーバーURL: {self.base_url}")
        logger.info(f"Unreal Engine バージョン: {self.unreal_version}")
    
    def check_server_status(self) -> Dict[str, Any]:
        """
        MCPサーバーの状態を確認する
        
        戻り値:
            dict: サーバーのステータス情報
        """
        try:
            response = requests.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                status_data = response.json()
                return status_data
            else:
                logger.error(f"サーバーステータス取得エラー: {response.status_code}")
                return {"status": "error", "message": f"HTTP error: {response.status_code}"}
        except Exception as e:
            logger.error(f"サーバーステータス取得中に例外が発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}

    def execute_blender_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Blenderコマンドを実行する
        
        引数:
            command (str): 実行するコマンド
            params (dict): コマンドのパラメータ
            
        戻り値:
            dict: コマンドの実行結果
        """
        if params is None:
            params = {}
            
        try:
            # Unrealモジュールがある場合は通知を表示
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                style = notification.notification_style
                style.fade_in_duration = 0.5
                style.fade_out_duration = 0.5
                style.expire_duration = 3.0
                
                notification.display_notification(f"Blenderコマンド開始: {command}", style)
                
            # APIを呼び出す
            endpoint = f"{self.base_url}/api/blender/execute"
            data = {
                "command": command,
                "params": params
            }
            response = requests.post(endpoint, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Unrealモジュールがある場合は通知を表示
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(f"Blenderコマンド完了: {command}", style)
                
                return result
            else:
                error_msg = f"Blenderコマンド実行エラー: {response.status_code}"
                logger.error(error_msg)
                
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(error_msg, style)
                
                return {"status": "error", "message": f"HTTP error: {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Blenderコマンド実行中に例外が発生しました: {str(e)}"
            logger.error(error_msg)
            
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                notification.display_notification(error_msg, style)
            
            return {"status": "error", "message": str(e)}

    def execute_unreal_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        UE5コマンドを実行する
        
        引数:
            command (str): 実行するコマンド
            params (dict): コマンドのパラメータ
            
        戻り値:
            dict: コマンドの実行結果
        """
        if params is None:
            params = {}
            
        try:
            # Unrealモジュールがある場合は通知を表示
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                style = notification.notification_style
                notification.display_notification(f"UE5コマンド開始: {command}", style)
            
            # APIを呼び出す
            endpoint = f"{self.base_url}/api/unreal/execute"
            data = {
                "command": command,
                "params": params
            }
            response = requests.post(endpoint, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Unrealモジュールがある場合は通知を表示
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(f"UE5コマンド完了: {command}", style)
                
                return result
            else:
                error_msg = f"UE5コマンド実行エラー: {response.status_code}"
                logger.error(error_msg)
                
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(error_msg, style)
                
                return {"status": "error", "message": f"HTTP error: {response.status_code}"}
                
        except Exception as e:
            error_msg = f"UE5コマンド実行中に例外が発生しました: {str(e)}"
            logger.error(error_msg)
            
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                notification.display_notification(error_msg, style)
            
            return {"status": "error", "message": str(e)}

    def generate_blueprint_from_ai(self, blueprint_name: str, blueprint_type: str, description: str) -> Dict[str, Any]:
        """
        AIを使用してBlueprint生成する
        
        引数:
            blueprint_name (str): Blueprintの名前
            blueprint_type (str): Blueprintの種類（Actor、GameModeBase等）
            description (str): Blueprintの機能説明
            
        戻り値:
            dict: 生成結果
        """
        try:
            # Unrealモジュールがある場合は通知を表示
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                style = notification.notification_style
                notification.display_notification(f"AI生成開始: {blueprint_name[:20]}...", style)
            
            # APIを呼び出す
            endpoint = f"{self.base_url}/api/ai/generate"
            data = {
                "type": "blueprint",
                "prompt": f"Create a Blueprint named {blueprint_name} based on {blueprint_type} that {description}",
                "params": {
                    "name": blueprint_name,
                    "parent_class": blueprint_type,
                    "description": description
                }
            }
            response = requests.post(endpoint, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Unrealモジュールがある場合は通知を表示
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(f"AI生成完了: blueprint", style)
                
                # AIの生成が成功したら、実際にBlueprintを作成
                blueprint_data = result.get("result", {})
                return self.execute_unreal_command("create_blueprint", {
                    "name": blueprint_name,
                    "parent": blueprint_type,
                    "script": blueprint_data.get("script", ""),
                    "components": blueprint_data.get("components", []),
                    "variables": blueprint_data.get("variables", [])
                })
            else:
                error_msg = f"AI Blueprint生成エラー: {response.status_code}"
                logger.error(error_msg)
                
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(error_msg, style)
                
                return {"status": "error", "message": f"HTTP error: {response.status_code}"}
                
        except Exception as e:
            error_msg = f"AI Blueprint生成中に例外が発生しました: {str(e)}"
            logger.error(error_msg)
            
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                notification.display_notification(error_msg, style)
            
            return {"status": "error", "message": str(e)}

    def import_asset_from_blender(self, asset_name: str, file_format: str = "fbx") -> Dict[str, Any]:
        """
        BlenderからエクスポートされたアセットをUE5にインポートする
        
        引数:
            asset_name (str): アセット名
            file_format (str): ファイル形式（fbx, obj等）
            
        戻り値:
            dict: インポート結果
        """
        try:
            # Unrealモジュールがある場合は通知を表示
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                style = notification.notification_style
                notification.display_notification(f"Blenderコマンド開始: export_asset", style)
            
            # 1. エクスポートされたファイルを確認
            export_path = f"./exports/{asset_name}.{file_format.lower()}"
            if not os.path.exists(export_path):
                error_msg = f"エクスポートされたファイルが見つかりません: {export_path}"
                logger.error(error_msg)
                
                if 'unreal' in sys.modules:
                    import unreal
                    notification = unreal.EditorNotificationController()
                    notification.display_notification(error_msg, style)
                
                return {"status": "error", "error": "File not found", "path": export_path}
            
            # 2. UE5にインポート
            notification.display_notification(f"Blenderコマンド完了: export_asset", style)
            
            return self.execute_unreal_command("import_asset", {
                "path": os.path.abspath(export_path),
                "destination": f"/Game/Assets/{asset_name}"
            })
                
        except Exception as e:
            error_msg = f"アセットインポート中に例外が発生しました: {str(e)}"
            logger.error(error_msg)
            
            if 'unreal' in sys.modules:
                import unreal
                notification = unreal.EditorNotificationController()
                notification.display_notification(error_msg, style)
            
            return {"status": "error", "message": str(e)}

def connect_to_mcp(host: str = "127.0.0.1", port: int = 8000) -> UE5MCPClient:
    """
    MCPサーバーに接続する
    
    引数:
        host (str): MCPサーバーのホスト
        port (int): MCPサーバーのポート
        
    戻り値:
        UE5MCPClient: MCPクライアントインスタンス
    """
    client = UE5MCPClient(host, port)
    
    # サーバーステータスを確認
    status = client.check_server_status()
    
    # Unrealモジュールがある場合は通知を表示
    if 'unreal' in sys.modules:
        import unreal
        notification = unreal.EditorNotificationController()
        style = notification.notification_style
        
        if status.get("status") == "running":
            notification.display_notification(f"MCPサーバー接続成功: {status.get('status')}", style)
            unreal.log(f"サーバーステータス: {json.dumps(status, indent=2)}")
        else:
            notification.display_notification(f"MCPサーバー接続失敗: {status.get('status')}", style)
    
    logger.info(f"サーバーステータス: {status}")
    return client 
