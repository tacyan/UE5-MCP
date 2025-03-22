#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲームアセットインポートスクリプト

このスクリプトは、Blenderで作成した宇宙船や弾丸などのモデルを
UE5プロジェクトにインポートします。MCPフレームワークを使用して
UE5とBlenderの連携を行います。

使用方法:
  python import_shooter_assets.py
"""

import os
import sys
import time
import logging
from typing import Dict, Any, List
from ue5_mcp_client import UE5MCPClient

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("import_shooter_assets.log")
    ]
)
logger = logging.getLogger("import_shooter_assets")

# エクスポート・インポートディレクトリ
EXPORT_DIR = "./exports"
IMPORT_DIR = "./imports"
UE5_ASSET_PATH = "/Game/ShooterGame/Assets"

# アセット定義
ASSETS = [
    {"name": "PlayerShip", "description": "プレイヤーの宇宙船モデル"},
    {"name": "EnemyShip", "description": "敵の宇宙船モデル"},
    {"name": "Projectile", "description": "弾丸モデル"},
    {"name": "PowerUp", "description": "パワーアップアイテムモデル"}
]

def import_assets_to_ue5():
    """アセットをUE5にインポートする"""
    logger.info("MCPサーバーに接続しています...")
    
    # MCPクライアントを初期化
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # サーバーステータスを確認
    status = client.check_server_status()
    logger.info(f"サーバーステータス: {status}")
    
    # ステータスチェックを修正（'status'キーが'running'であることを確認）
    if status.get("status") != "running":
        logger.error(f"MCPサーバーが実行中ではありません: {status}")
        return False
    
    logger.info("MCPサーバーに接続しました。アセットをインポートします...")
    
    # 各アセットをインポート
    for asset in ASSETS:
        asset_name = asset["name"]
        export_path = os.path.join(EXPORT_DIR, f"{asset_name}.fbx")
        
        # エクスポートファイルが存在するか確認
        if not os.path.exists(export_path):
            logger.warning(f"アセットファイルが見つかりません: {export_path}")
            continue
        
        logger.info(f"アセットをインポートしています: {asset_name}")
        
        # フルパスに変換
        abs_export_path = os.path.abspath(export_path)
        logger.info(f"フルパス: {abs_export_path}")
        
        # UE5コマンドを実行してアセットをインポート
        params = {
            "path": abs_export_path,
            "destination": UE5_ASSET_PATH
        }
        
        logger.info(f"インポートパラメータ: {params}")
        result = client.execute_unreal_command("import_asset", params)
        
        if result.get("status") == "success":
            logger.info(f"アセットのインポートに成功しました: {asset_name}")
        else:
            logger.error(f"アセットのインポートに失敗しました: {asset_name} - {result}")
    
    logger.info("すべてのアセットのインポート処理が完了しました")
    return True

def create_materials():
    """アセット用のマテリアルを作成する"""
    logger.info("マテリアルを作成しています...")
    
    # MCPクライアントを初期化
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # マテリアル定義
    materials = [
        {"name": "PlayerShipMaterial", "color": [0.0, 0.5, 1.0], "target": "PlayerShip"},
        {"name": "EnemyShipMaterial", "color": [1.0, 0.2, 0.2], "target": "EnemyShip"},
        {"name": "ProjectileMaterial", "color": [1.0, 0.8, 0.0], "target": "Projectile"},
        {"name": "PowerUpMaterial", "color": [0.0, 1.0, 0.5], "target": "PowerUp"}
    ]
    
    # 各マテリアルを作成して適用
    for material in materials:
        logger.info(f"マテリアルを作成しています: {material['name']}")
        
        # UE5コマンドを実行してマテリアルを作成
        params = {
            "name": material["name"],
            "path": f"{UE5_ASSET_PATH}/Materials",
            "color": material["color"]
        }
        
        result = client.execute_unreal_command("create_material", params)
        
        if result.get("status") == "success":
            logger.info(f"マテリアルの作成に成功しました: {material['name']}")
            
            # マテリアルをアセットに適用
            apply_params = {
                "asset": f"{UE5_ASSET_PATH}/{material['target']}",
                "material": f"{UE5_ASSET_PATH}/Materials/{material['name']}"
            }
            
            apply_result = client.execute_unreal_command("apply_material", apply_params)
            
            if apply_result.get("status") == "success":
                logger.info(f"マテリアルの適用に成功しました: {material['target']} -> {material['name']}")
            else:
                logger.error(f"マテリアルの適用に失敗しました: {material['target']} -> {material['name']} - {apply_result}")
        else:
            logger.error(f"マテリアルの作成に失敗しました: {material['name']} - {result}")
    
    logger.info("すべてのマテリアル処理が完了しました")
    return True

def direct_import_fbx():
    """UE5プロジェクトにFBXを直接インポートする"""
    logger.info("FBXファイルを直接インポートしています...")
    
    # MCPクライアントを初期化
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # 各アセットをインポート
    for asset in ASSETS:
        asset_name = asset["name"]
        export_path = os.path.join(EXPORT_DIR, f"{asset_name}.fbx")
        
        # エクスポートファイルが存在するか確認
        if not os.path.exists(export_path):
            logger.warning(f"アセットファイルが見つかりません: {export_path}")
            continue
        
        logger.info(f"アセットをインポートしています: {asset_name}")
        
        # フルパスに変換
        abs_export_path = os.path.abspath(export_path)
        # パスのバックスラッシュをフォワードスラッシュに変換
        clean_path = abs_export_path.replace("\\", "/")
        logger.info(f"フルパス: {clean_path}")
        
        # Pythonスクリプトを実行してアセットをインポート
        python_script = """
import unreal
import os

# アセットをインポート
def import_fbx_asset():
    # インポート設定
    import_task = unreal.AssetImportTask()
    import_task.filename = "{0}"
    import_task.destination_path = "{1}"
    import_task.replace_existing = True
    import_task.automated = True
    import_task.save = True
    
    # インポート実行
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
    return "インポート完了: {2}"

# 実行
result = import_fbx_asset()
print(result)
""".format(clean_path, UE5_ASSET_PATH, asset_name)
        
        # UE5コマンドを実行してPythonスクリプトを実行
        params = {
            "script": python_script
        }
        
        result = client.execute_unreal_command("execute_python", params)
        
        if result.get("status") == "success":
            logger.info(f"アセットのインポートに成功しました: {asset_name}")
        else:
            logger.error(f"アセットのインポートに失敗しました: {asset_name} - {result}")
    
    logger.info("すべてのアセットのインポート処理が完了しました")
    return True

def main():
    """メイン実行関数"""
    logger.info("===== シューティングゲームアセットのインポートを開始します =====")
    
    # アセットをインポート
    if direct_import_fbx():
        logger.info("アセットが正常にインポートされました")
        
        # マテリアルを作成
        if create_materials():
            logger.info("マテリアルが正常に作成されました")
        else:
            logger.error("マテリアル作成中にエラーが発生しました")
    else:
        logger.error("アセットのインポート中にエラーが発生しました")
    
    logger.info("===== アセットインポート処理が完了しました =====")

if __name__ == "__main__":
    main() 
