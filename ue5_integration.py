#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5-MCP統合スクリプト

このスクリプトは、Unreal Engine 5.5のPythonインタプリタから実行され、
MCPサーバーと連携してMCPフレームワークを使用できるようにします。

主な機能:
- MCPサーバーへの接続
- UE5でのアセット管理（インポート、配置など）
- AIを活用したゲームロジックの生成
- Blenderからのアセット移行のサポート

使用方法:
1. UE5エディタを起動
2. Python スクリプトエディタでこのファイルを開く
3. 実行ボタンを押してスクリプトを実行

制限事項:
- Unreal Engine 5.1以上が必要です
- Python Editor Script Pluginが有効になっている必要があります
- MCPサーバーが事前に起動している必要があります
"""

import unreal
import json
import os
import sys
import requests
import time
import logging
import tempfile
from pathlib import Path

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ue5_integration")

class UE5MCPIntegration:
    """
    UE5とMCP連携のためのクラス
    """
    
    def __init__(self, server_host="127.0.0.1", server_port=8000):
        """
        初期化メソッド
        
        引数:
            server_host (str): MCPサーバーのホスト
            server_port (int): MCPサーバーのポート
        """
        self.server_url = f"http://{server_host}:{server_port}"
        self.import_dir = os.path.join(tempfile.gettempdir(), "ue5_mcp_imports")
        
        # インポートディレクトリが存在しなければ作成
        if not os.path.exists(self.import_dir):
            os.makedirs(self.import_dir)
        
        # UE5バージョンを取得
        self.ue_version = unreal.SystemLibrary.get_engine_version()
        
        logger.info(f"MCPサーバーURL: {self.server_url}")
        logger.info(f"インポートディレクトリ: {self.import_dir}")
        logger.info(f"Unreal Engine バージョン: {self.ue_version}")
        
        # 通知スタイルの設定
        self.notification_style = unreal.EditorNotificationController().notification_style
        self.notification_style.fade_in_duration = 0.5
        self.notification_style.fade_out_duration = 0.5
        self.notification_style.expire_duration = 5.0
    
    def connect_to_server(self):
        """
        MCPサーバーへの接続を確認する
        
        戻り値:
            bool: 接続成功したかどうか
        """
        try:
            logger.info("MCPサーバーへの接続を確認しています...")
            self.show_notification("MCPサーバーへの接続を確認中...")
            
            response = requests.get(f"{self.server_url}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                server_status = status_data.get("status", "unknown")
                
                if server_status == "running":
                    logger.info("MCPサーバーに正常に接続しました")
                    self.show_notification("MCPサーバーに正常に接続しました", success=True)
                    return True
                else:
                    logger.warning(f"MCPサーバーのステータスが異常: {server_status}")
                    self.show_notification(f"MCPサーバーのステータスが異常: {server_status}", success=False)
                    return False
            else:
                logger.error(f"MCPサーバーへの接続に失敗しました: {response.status_code}")
                self.show_notification(f"MCPサーバーへの接続に失敗しました: HTTP {response.status_code}", success=False)
                return False
        except Exception as e:
            logger.exception(f"MCPサーバーへの接続中にエラーが発生しました: {str(e)}")
            self.show_notification(f"MCPサーバーへの接続中にエラーが発生しました", success=False)
            return False
    
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
            unreal.log(message)
        except Exception as e:
            logger.error(f"通知表示中にエラーが発生しました: {str(e)}")
    
    def create_level(self, level_name, template="Empty"):
        """
        新しいレベルを作成する
        
        引数:
            level_name (str): レベル名
            template (str): テンプレート名（"Empty", "VR-Basic", "ThirdPerson"など）
            
        戻り値:
            dict: 作成結果
        """
        try:
            self.show_notification(f"レベル '{level_name}' を作成中...")
            
            # テンプレートのマッピング
            template_map = {
                "Empty": "/Engine/Maps/Templates/Template_Default",
                "ThirdPerson": "/Engine/Maps/Templates/ThirdPerson",
                "FirstPerson": "/Engine/Maps/Templates/FirstPerson",
                "TopDown": "/Engine/Maps/Templates/TopDown",
                "Puzzle": "/Engine/Maps/Templates/Puzzle",
                "VR-Basic": "/Engine/Maps/Templates/VR-Basic"
            }
            
            # テンプレートが存在するか確認
            template_path = template_map.get(template)
            if not template_path:
                error_msg = f"未知のテンプレート: {template}"
                logger.error(error_msg)
                self.show_notification(error_msg, success=False)
                return {"status": "error", "message": error_msg}
            
            # 新しいレベルを作成
            level_path = f"/Game/Levels/{level_name}"
            
            # すでに存在する場合は警告
            asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            existing_asset = asset_registry.get_asset_by_object_path(level_path)
            
            if existing_asset:
                warning_msg = f"レベル '{level_name}' は既に存在します。"
                logger.warning(warning_msg)
                self.show_notification(warning_msg, success=False)
                return {"status": "warning", "message": warning_msg}
            
            # 実際のレベル作成ロジック
            # UE5のPythonではエディタレベルの作成APIが制限されているため、
            # 通常はC++側のAPIを呼び出すか、エディタコマンドを実行する
            
            # ここではエディタコマンドレットを使用
            unreal.log(f"レベル '{level_name}' をテンプレート '{template}' から作成しています...")
            
            unreal.EditorLevelLibrary.new_level(level_path)
            
            # 成功を通知
            success_msg = f"レベル '{level_name}' を作成しました"
            logger.info(success_msg)
            self.show_notification(success_msg, success=True)
            
            return {
                "status": "success",
                "message": success_msg,
                "level_info": {
                    "name": level_name,
                    "path": level_path,
                    "template": template
                }
            }
        
        except Exception as e:
            error_msg = f"レベル作成中にエラーが発生しました: {str(e)}"
            logger.exception(error_msg)
            self.show_notification(error_msg, success=False)
            return {"status": "error", "message": error_msg}
    
    def import_asset(self, file_path, destination_path="/Game/Assets"):
        """
        アセットをインポートする
        
        引数:
            file_path (str): インポートするファイルのパス
            destination_path (str): インポート先のパス
            
        戻り値:
            dict: インポート結果
        """
        try:
            # ファイルが存在するか確認
            if not os.path.exists(file_path):
                error_msg = f"インポートするファイルが見つかりません: {file_path}"
                logger.error(error_msg)
                self.show_notification(error_msg, success=False)
                return {"status": "error", "message": error_msg}
            
            # ファイル情報を取得
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            base_name = os.path.splitext(file_name)[0]
            
            # サポートされているファイル形式か確認
            supported_extensions = [".fbx", ".obj", ".gltf", ".glb", ".uasset"]
            if file_extension not in supported_extensions:
                error_msg = f"未サポートのファイル形式: {file_extension}"
                logger.error(error_msg)
                self.show_notification(error_msg, success=False)
                return {"status": "error", "message": error_msg}
            
            # インポート先のディレクトリが存在することを確認
            # UE5では必要に応じて自動的に作成されるので、ここでのチェックは不要
            
            # インポート処理
            self.show_notification(f"アセット '{file_name}' をインポート中...")
            
            import_task = unreal.AssetImportTask()
            import_task.filename = file_path
            import_task.destination_path = destination_path
            import_task.replace_existing = True
            import_task.automated = True
            import_task.save = True
            
            # インポートを実行
            unreal.AssetTools.get_asset_tools().import_asset_tasks([import_task])
            
            # インポートされたアセットへのパス
            asset_path = f"{destination_path}/{base_name}"
            
            # 成功を通知
            success_msg = f"アセット '{file_name}' をインポートしました"
            logger.info(success_msg)
            self.show_notification(success_msg, success=True)
            
            return {
                "status": "success",
                "message": success_msg,
                "asset_info": {
                    "name": base_name,
                    "original_path": file_path,
                    "asset_path": asset_path,
                    "type": file_extension[1:]  # 先頭の'.'を除去
                }
            }
        
        except Exception as e:
            error_msg = f"アセットインポート中にエラーが発生しました: {str(e)}"
            logger.exception(error_msg)
            self.show_notification(error_msg, success=False)
            return {"status": "error", "message": error_msg}
    
    def place_asset(self, asset_path, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        """
        アセットをレベルに配置する
        
        引数:
            asset_path (str): 配置するアセットのパス
            location (tuple): 位置座標 (X, Y, Z)
            rotation (tuple): 回転 (Pitch, Yaw, Roll)
            scale (tuple): スケール (X, Y, Z)
            
        戻り値:
            dict: 配置結果
        """
        try:
            # アセットが存在するか確認
            asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            asset = asset_registry.get_asset_by_object_path(asset_path)
            
            if not asset:
                error_msg = f"アセット '{asset_path}' が見つかりません"
                logger.error(error_msg)
                self.show_notification(error_msg, success=False)
                return {"status": "error", "message": error_msg}
            
            # アセットをロード
            self.show_notification(f"アセット '{asset_path}' を配置中...")
            
            # アセットを配置
            actor_location = unreal.Vector(location[0], location[1], location[2])
            actor_rotation = unreal.Rotator(rotation[0], rotation[1], rotation[2])
            actor_scale = unreal.Vector(scale[0], scale[1], scale[2])
            
            # アセットクラスをロード
            asset_data = asset_registry.get_asset_data(asset.get_path_name())
            asset_class = unreal.load_class(None, asset_data.asset_class_path)
            
            # エディタの現在のレベルに追加
            actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
                asset, 
                actor_location,
                actor_rotation
            )
            
            # スケールを設定
            if actor:
                actor.set_actor_scale3d(actor_scale)
            
            # 成功を通知
            success_msg = f"アセット '{asset_path}' を配置しました"
            logger.info(success_msg)
            self.show_notification(success_msg, success=True)
            
            return {
                "status": "success",
                "message": success_msg,
                "placement_info": {
                    "asset_path": asset_path,
                    "location": location,
                    "rotation": rotation,
                    "scale": scale,
                    "actor_name": actor.get_name() if actor else "Unknown"
                }
            }
        
        except Exception as e:
            error_msg = f"アセット配置中にエラーが発生しました: {str(e)}"
            logger.exception(error_msg)
            self.show_notification(error_msg, success=False)
            return {"status": "error", "message": error_msg}
    
    def generate_terrain(self, size_x=4096, size_y=4096, height_variation="medium", terrain_type="plains"):
        """
        地形を生成する
        
        引数:
            size_x (int): X方向のサイズ
            size_y (int): Y方向のサイズ
            height_variation (str): 高さのバリエーション ("low", "medium", "high")
            terrain_type (str): 地形タイプ ("plains", "mountainous", "desert", etc.)
            
        戻り値:
            dict: 生成結果
        """
        try:
            self.show_notification(f"{terrain_type}地形を生成中...")
            
            # 高さバリエーションのマッピング
            height_map = {
                "low": 100,
                "medium": 500,
                "high": 1000
            }
            
            max_height = height_map.get(height_variation.lower(), 500)
            
            # 地形ツールを使用して地形を生成
            # UE5のPythonではランドスケープ操作のAPIが制限されているため、
            # 簡易的な実装になります
            
            # ランドスケープを作成
            unreal.log(f"地形を生成しています: サイズ ({size_x}x{size_y}), 高さ {height_variation}, タイプ {terrain_type}")
            
            # コマンドレットを使用してランドスケープを作成
            landscape = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.Landscape, 
                unreal.Vector(0, 0, 0),
                unreal.Rotator(0, 0, 0)
            )
            
            # 地形タイプに応じたマテリアルを適用
            terrain_material_map = {
                "plains": "/Engine/EngineMaterials/Landscape/M_Landscape",
                "mountainous": "/Engine/EngineMaterials/Landscape/M_Landscape_Mountain",
                "desert": "/Engine/EngineMaterials/Landscape/M_Landscape_Desert"
            }
            
            material_path = terrain_material_map.get(terrain_type.lower(), "/Engine/EngineMaterials/Landscape/M_Landscape")
            material = unreal.load_object(None, material_path)
            
            if material and landscape:
                landscape.landscape_material = material
            
            # 成功を通知
            success_msg = f"{terrain_type}地形の生成が完了しました"
            logger.info(success_msg)
            self.show_notification(success_msg, success=True)
            
            return {
                "status": "success",
                "message": success_msg,
                "terrain_info": {
                    "size_x": size_x,
                    "size_y": size_y,
                    "height_variation": height_variation,
                    "max_height": max_height,
                    "terrain_type": terrain_type
                }
            }
        
        except Exception as e:
            error_msg = f"地形生成中にエラーが発生しました: {str(e)}"
            logger.exception(error_msg)
            self.show_notification(error_msg, success=False)
            return {"status": "error", "message": error_msg}
    
    def create_blueprint(self, name, parent_class="Actor", description=None):
        """
        Blueprintを作成する
        
        引数:
            name (str): Blueprint名
            parent_class (str): 親クラス名
            description (str): Blueprint説明文
            
        戻り値:
            dict: 作成結果
        """
        try:
            self.show_notification(f"Blueprint '{name}' を作成中...")
            
            # Blueprint Factory を作成
            factory = unreal.BlueprintFactory()
            factory.parent_class = unreal.load_class(None, f"Engine.{parent_class}")
            
            # Blueprint を作成
            blueprint_path = f"/Game/Blueprints/{name}"
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            blueprint = asset_tools.create_asset(
                name,
                "/Game/Blueprints",
                unreal.Blueprint,
                factory
            )
            
            # 説明文があれば、コメントとして追加
            if description and blueprint:
                # この部分はUE5 Pythonでは直接サポートされていないため、
                # 実際の実装では別の方法が必要
                pass
            
            # 保存
            if blueprint:
                package = unreal.load_package(None, blueprint.get_outer().get_path_name())
                unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
            
            # 成功を通知
            success_msg = f"Blueprint '{name}' を作成しました"
            logger.info(success_msg)
            self.show_notification(success_msg, success=True)
            
            return {
                "status": "success",
                "message": success_msg,
                "blueprint_info": {
                    "name": name,
                    "path": blueprint_path,
                    "parent_class": parent_class,
                    "description": description
                }
            }
        
        except Exception as e:
            error_msg = f"Blueprint作成中にエラーが発生しました: {str(e)}"
            logger.exception(error_msg)
            self.show_notification(error_msg, success=False)
            return {"status": "error", "message": error_msg}
    
    def execute_mcp_command(self, command, params=None):
        """
        MCPサーバーにコマンドを送信する
        
        引数:
            command (str): コマンド名
            params (dict): コマンドパラメータ
            
        戻り値:
            dict: 実行結果
        """
        try:
            self.show_notification(f"MCPコマンド '{command}' を実行中...")
            
            # パラメータのデフォルト値
            if params is None:
                params = {}
            
            # MCPサーバーにコマンドを送信
            response = requests.post(
                f"{self.server_url}/command",
                json={"command": command, "params": params}
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                
                if status == "success":
                    success_msg = f"MCPコマンド '{command}' が成功しました"
                    logger.info(success_msg)
                    self.show_notification(success_msg, success=True)
                    return result
                else:
                    error_msg = f"MCPコマンド '{command}' が失敗しました: {result.get('message', '')}"
                    logger.error(error_msg)
                    self.show_notification(error_msg, success=False)
                    return result
            else:
                error_msg = f"MCPサーバーへのコマンド送信に失敗しました: HTTP {response.status_code}"
                logger.error(error_msg)
                self.show_notification(error_msg, success=False)
                return {
                    "status": "error",
                    "message": error_msg
                }
        
        except Exception as e:
            error_msg = f"MCPコマンド実行中にエラーが発生しました: {str(e)}"
            logger.exception(error_msg)
            self.show_notification(error_msg, success=False)
            return {
                "status": "error",
                "message": error_msg
            }

# UE5のメインスクリプト実行関数
def run():
    """
    統合をテストするための実行関数
    """
    integration = UE5MCPIntegration()
    
    # MCPサーバーへの接続をテスト
    if not integration.connect_to_server():
        return
    
    # 新しいレベルを作成
    level_result = integration.create_level("MCPTestLevel", "ThirdPerson")
    
    if level_result["status"] != "success":
        return
    
    # 地形を生成
    terrain_result = integration.generate_terrain(4096, 4096, "medium", "mountainous")
    
    if terrain_result["status"] != "success":
        return
    
    # Blueprintを作成
    bp_result = integration.create_blueprint("BP_CollectibleItem", "Actor", "プレイヤーが収集できるアイテム")
    
    unreal.log(f"\nUE5-MCP統合テスト結果:")
    unreal.log(f"レベル作成: {level_result['status']}")
    unreal.log(f"地形生成: {terrain_result['status']}")
    unreal.log(f"Blueprint作成: {bp_result['status']}")

# スクリプトが直接実行された場合にのみ実行
if __name__ == "__main__":
    run() 
