#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPクライアント for Unreal Engine 5

このスクリプトは、Unreal Engine 5からMCPサーバーに接続し、APIを呼び出すためのクライアントを提供します。
UE5のPythonインタープリタを使用して、AIドリブンのゲーム開発機能を実現します。

主な機能:
- MCPサーバーとの接続
- APIリクエストの送信と処理
- UE5へのフィードバック提供
- 自動化ワークフローの実行

制限事項:
- UE5のPython Editor Script Pluginが有効になっている必要があります
- MCPサーバーが実行されていることが前提です
"""

import unreal
import requests
import json
import logging
import os
import time

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ue5_mcp_client")

class UE5MCPClient:
    """
    UE5 MCP クライアントクラス
    
    MCPサーバーとの通信を処理するクラス
    """
    
    def __init__(self, server_host="127.0.0.1", server_port=5000):
        """
        初期化メソッド
        
        引数:
            server_host (str): MCPサーバーのホスト
            server_port (int): MCPサーバーのポート
        """
        self.server_url = f"http://{server_host}:{server_port}"
        self.ue_version = unreal.SystemLibrary.get_engine_version()
        logger.info(f"MCPサーバーURL: {self.server_url}")
        logger.info(f"Unreal Engine バージョン: {self.ue_version}")
        
        # UE5通知システムの初期化
        self.notification_style = unreal.EditorNotificationController().notification_style
        self.notification_style.fade_in_duration = 0.5
        self.notification_style.fade_out_duration = 0.5
        self.notification_style.expire_duration = 5.0
    
    def show_notification(self, message, success=True):
        """
        UE5に通知を表示する
        
        引数:
            message (str): 表示するメッセージ
            success (bool): 成功メッセージかどうか
        """
        try:
            controller = unreal.EditorNotificationController()
            self.notification_style.text_color = unreal.LinearColor(0.0, 1.0, 0.0, 1.0) if success else unreal.LinearColor(1.0, 0.0, 0.0, 1.0)
            controller.display_notification(message, self.notification_style)
        except Exception as e:
            logger.error(f"通知表示中にエラーが発生しました: {str(e)}")
    
    def check_server_status(self):
        """
        サーバーのステータスを確認する
        
        戻り値:
            dict: サーバーのステータス情報
        """
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            response.raise_for_status()
            result = response.json()
            self.show_notification(f"MCPサーバー接続成功: {result['status']}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"サーバーステータス確認中にエラーが発生しました: {str(e)}")
            self.show_notification(f"MCPサーバー接続エラー: {str(e)}", False)
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
            self.show_notification(f"AI生成開始: {prompt[:30]}...")
            
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
            result = response.json()
            
            self.show_notification(f"AI生成完了: {content_type}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"AI生成中にエラーが発生しました: {str(e)}")
            self.show_notification(f"AI生成エラー: {str(e)}", False)
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
            self.show_notification(f"Blenderコマンド開始: {command}")
            
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
            result = response.json()
            
            self.show_notification(f"Blenderコマンド完了: {command}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Blenderコマンド実行中にエラーが発生しました: {str(e)}")
            self.show_notification(f"Blenderコマンドエラー: {str(e)}", False)
            return {"status": "error", "error": str(e)}
    
    def execute_unreal_command(self, command, params=None):
        """
        Unrealコマンド（UE5-MCP API経由）を実行する
        
        引数:
            command (str): 実行するコマンド
            params (dict): コマンドパラメータ
            
        戻り値:
            dict: コマンド実行結果
        """
        try:
            self.show_notification(f"UE5コマンド開始: {command}")
            
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
            result = response.json()
            
            self.show_notification(f"UE5コマンド完了: {command}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"UE5コマンド実行中にエラーが発生しました: {str(e)}")
            self.show_notification(f"UE5コマンドエラー: {str(e)}", False)
            return {"status": "error", "error": str(e)}
    
    def import_asset_from_blender(self, asset_name, asset_type="fbx"):
        """
        Blenderからアセットをインポートする
        
        引数:
            asset_name (str): アセット名
            asset_type (str): アセットタイプ
            
        戻り値:
            dict: インポート結果
        """
        # Blenderにエクスポートコマンドを送信
        export_result = self.execute_blender_command("export_asset", {
            "asset_name": asset_name,
            "format": asset_type
        })
        
        if export_result.get("status") != "success":
            self.show_notification(f"Blenderからのエクスポートに失敗しました: {asset_name}", False)
            return export_result
        
        # エクスポートされたファイルパスを取得
        export_path = export_result.get("export_info", {}).get("path")
        if not export_path or not os.path.exists(export_path):
            self.show_notification(f"エクスポートされたファイルが見つかりません: {export_path}", False)
            return {"status": "error", "error": f"File not found: {export_path}"}
        
        # UE5へのインポートコマンドを送信
        import_result = self.execute_unreal_command("import_asset", {
            "path": export_path,
            "destination": f"/Game/Assets/{asset_name}"
        })
        
        return import_result
    
    def generate_blueprint_from_ai(self, name, class_name, description):
        """
        AIを使用してBlueprintを生成する
        
        引数:
            name (str): Blueprint名
            class_name (str): クラス名
            description (str): 説明
            
        戻り値:
            dict: 生成結果
        """
        # AIに依頼
        ai_result = self.generate_ai_content(
            f"Create a Blueprint named {name} of class {class_name} that does the following: {description}",
            "blueprint"
        )
        
        # UE5でのBlueprint作成
        blueprint_result = self.execute_unreal_command("create_blueprint", {
            "name": name,
            "class": class_name,
            "description": description,
            "ai_generate": True
        })
        
        return blueprint_result


# UE5のPythonインタープリタから実行できるサンプル関数
def connect_to_mcp():
    """
    MCPサーバーに接続し、テストを行う
    
    UE5エディタのPythonスクリプトから呼び出すことができる
    """
    client = UE5MCPClient()
    
    # サーバーステータスの確認
    status = client.check_server_status()
    unreal.log(f"サーバーステータス: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    return client 
