#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blender-UE5アセット連携スクリプト

このスクリプトは、Blenderでシンプルなオブジェクトを作成し、
MCPフレームワークを通じてUnreal Engine 5にエクスポートするデモンストレーションです。

主な機能:
- Blender APIを使用したモデル作成
- MCPクライアント接続の確立
- BlenderからUE5へのアセット転送
- UE5におけるアセットの配置

使用方法:
    python blender_to_ue5_asset.py

制限事項:
- MCPサーバーが起動している必要があります
- Blender/UE5の動作はモックされています（未インストール環境でも実行可能）
"""

import json
import logging
import time
import sys
import os

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("blender_to_ue5_asset.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("blender_to_ue5_asset")

# UE5クライアントのモック化の準備（simpleゲームスクリプトと同様）
try:
    # UE5のモックモジュール
    if 'unreal' not in sys.modules:
        class MockUnreal:
            class SystemLibrary:
                @staticmethod
                def get_engine_version():
                    return "5.3.0 (モックバージョン)"
            
            class LinearColor:
                def __init__(self, r, g, b, a):
                    self.r = r
                    self.g = g
                    self.b = b
                    self.a = a
            
            class EditorNotificationController:
                def __init__(self):
                    self.notification_style = self.NotificationStyle()
                
                class NotificationStyle:
                    def __init__(self):
                        self.fade_in_duration = 0.5
                        self.fade_out_duration = 0.5
                        self.expire_duration = 5.0
                        self.text_color = None
                
                def display_notification(self, message, style):
                    logger.info(f"UE5通知: {message}")
            
            @staticmethod
            def log(message):
                logger.info(f"UE5ログ: {message}")

        # モックunrealモジュールをシステムに追加
        sys.modules['unreal'] = MockUnreal()
    
    # 必要なモジュールのインポート
    from ue5_mcp_client import UE5MCPClient, connect_to_mcp
    import requests
except ImportError as e:
    logger.error(f"必要なモジュールのインポートに失敗しました: {str(e)}")
    sys.exit(1)

def create_blender_model_and_export_to_ue5():
    """
    Blenderでモデルを作成し、UE5にエクスポートする
    """
    logger.info("===== Blender-UE5アセット連携開始 =====")
    
    # MCPサーバーに接続
    logger.info("MCPサーバーに接続...")
    client = connect_to_mcp()
    
    # 1. Blenderでシンプルなモデルを作成
    logger.info("1. Blenderでモデルを作成...")
    
    # Blenderモデル作成コマンドを実行
    model_result = client.execute_blender_command("create_model", {
        "model_type": "weapon",
        "name": "GameSword",
        "complexity": "medium"
    })
    log_command_result("Blenderモデル作成", model_result)
    
    # 2. モデルにマテリアルを適用
    logger.info("2. モデルにマテリアルを適用...")
    material_result = client.execute_blender_command("apply_material", {
        "model_name": "GameSword",
        "material_name": "MetalSwordMaterial",
        "properties": {
            "metallic": 0.9,
            "roughness": 0.1,
            "base_color": [0.7, 0.7, 0.8]
        }
    })
    log_command_result("マテリアル適用", material_result)
    
    # 3. モデルをFBX形式でエクスポート
    logger.info("3. モデルをFBXとしてエクスポート...")
    export_result = client.execute_blender_command("export_model", {
        "model_name": "GameSword",
        "export_format": "fbx",
        "export_path": "./exports/GameSword.fbx"
    })
    log_command_result("モデルエクスポート", export_result)
    
    # エクスポートが成功したかどうかをチェック
    if export_result.get("status") != "success":
        logger.error("モデルのエクスポートに失敗しました。処理を中止します。")
        return
    
    # 4. UE5にモデルをインポート
    logger.info("4. UE5にモデルをインポート...")
    
    # BlenderからUE5へのアセット転送
    import_result = client.import_asset_from_blender("GameSword", "fbx")
    log_command_result("UE5へのインポート", import_result)
    
    # 5. UE5でゲームレベルにアセットを配置
    logger.info("5. UE5のレベルにアセットを配置...")
    placement_result = client.execute_unreal_command("place_asset", {
        "asset_path": "/Game/Assets/GameSword",
        "location": [0, 0, 100],
        "rotation": [0, 0, 0],
        "scale": [1, 1, 1]
    })
    log_command_result("アセット配置", placement_result)
    
    logger.info("===== Blender-UE5アセット連携完了 =====")
    logger.info("""
作成・転送したアセットの概要:
- アセット名: GameSword
- モデルタイプ: 武器（剣）
- マテリアル: MetalSwordMaterial (メタリック)
- UE5パス: /Game/Assets/GameSword
- 配置場所: シーン中央、地面から100単位上
""")

def log_command_result(action, result):
    """
    コマンド実行結果をログに記録する
    
    引数:
        action (str): 実行したアクション
        result (dict): 実行結果
    """
    if isinstance(result, dict):
        status = result.get("status", "unknown")
        success = status == "success"
        message = result.get("message", "結果メッセージなし")
        logger.info(f"{action}: {'成功' if success else '失敗'} - {message}")
        if not success and "error" in result:
            logger.error(f"{action}エラー: {result['error']}")
    else:
        logger.warning(f"{action}: 不明な結果形式 - {str(result)}")

if __name__ == "__main__":
    try:
        create_blender_model_and_export_to_ue5()
    except Exception as e:
        logger.exception(f"実行中にエラーが発生しました: {str(e)}") 
