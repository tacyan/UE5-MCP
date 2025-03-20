#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プレイヤーキャラクター作成スクリプト

Blenderでシンプルなプレイヤーキャラクターを作成し、UE5に転送するスクリプトです。
MCPフレームワークを使用して、Blenderとの連携を行います。

主な機能:
- ロボット型プレイヤーキャラクターのモデル作成
- テクスチャとマテリアルの適用
- UE5へのエクスポートと転送
"""

import logging
import sys
import time
import os
import json

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("character_creation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("character_creation")

# UE5クライアントのモック化
try:
    if 'unreal' not in sys.modules:
        class MockUnreal:
            class SystemLibrary:
                @staticmethod
                def get_engine_version():
                    return "5.5.0 (モックバージョン)"
            
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
except ImportError as e:
    logger.error(f"必要なモジュールのインポートに失敗しました: {str(e)}")
    sys.exit(1)

def create_robot_character():
    """
    ロボット型プレイヤーキャラクターを作成する
    """
    logger.info("=== ロボット型プレイヤーキャラクターの作成開始 ===")
    
    # MCPサーバーに接続
    logger.info("MCPサーバーに接続...")
    client = connect_to_mcp()
    
    # 1. Blenderでロボットのベース（胴体）を作成
    logger.info("1. ロボットの胴体を作成...")
    body_result = client.execute_blender_command("create_model", {
        "model_type": "cylinder",
        "name": "RobotBody",
        "parameters": {
            "radius": 0.5,
            "height": 1.5,
            "location": [0, 0, 0.75]
        }
    })
    log_result("胴体作成", body_result)
    
    # 2. 頭部を作成
    logger.info("2. ロボットの頭部を作成...")
    head_result = client.execute_blender_command("create_model", {
        "model_type": "sphere",
        "name": "RobotHead",
        "parameters": {
            "radius": 0.3,
            "location": [0, 0, 1.8]
        }
    })
    log_result("頭部作成", head_result)
    
    # 3. 腕を作成（左）
    logger.info("3. ロボットの左腕を作成...")
    left_arm_result = client.execute_blender_command("create_model", {
        "model_type": "cylinder",
        "name": "RobotLeftArm",
        "parameters": {
            "radius": 0.15,
            "height": 0.8,
            "location": [-0.7, 0, 0.8],
            "rotation": [0, 90, 0]
        }
    })
    log_result("左腕作成", left_arm_result)
    
    # 4. 腕を作成（右）
    logger.info("4. ロボットの右腕を作成...")
    right_arm_result = client.execute_blender_command("create_model", {
        "model_type": "cylinder",
        "name": "RobotRightArm",
        "parameters": {
            "radius": 0.15,
            "height": 0.8,
            "location": [0.7, 0, 0.8],
            "rotation": [0, 90, 0]
        }
    })
    log_result("右腕作成", right_arm_result)
    
    # 5. 脚を作成（左）
    logger.info("5. ロボットの左脚を作成...")
    left_leg_result = client.execute_blender_command("create_model", {
        "model_type": "cylinder",
        "name": "RobotLeftLeg",
        "parameters": {
            "radius": 0.2,
            "height": 0.9,
            "location": [-0.3, 0, -0.45]
        }
    })
    log_result("左脚作成", left_leg_result)
    
    # 6. 脚を作成（右）
    logger.info("6. ロボットの右脚を作成...")
    right_leg_result = client.execute_blender_command("create_model", {
        "model_type": "cylinder",
        "name": "RobotRightLeg",
        "parameters": {
            "radius": 0.2,
            "height": 0.9,
            "location": [0.3, 0, -0.45]
        }
    })
    log_result("右脚作成", right_leg_result)
    
    # 7. すべてのパーツを選択してジョインする
    logger.info("7. 全パーツを結合...")
    join_result = client.execute_blender_command("join_objects", {
        "objects": ["RobotBody", "RobotHead", "RobotLeftArm", "RobotRightArm", "RobotLeftLeg", "RobotRightLeg"],
        "target_name": "PlayerRobot"
    })
    log_result("パーツ結合", join_result)
    
    # 8. マテリアルを適用
    logger.info("8. マテリアルを適用...")
    material_result = client.execute_blender_command("apply_material", {
        "object_name": "PlayerRobot",
        "material_name": "RobotMaterial",
        "properties": {
            "metallic": 0.8,
            "roughness": 0.2,
            "base_color": [0.2, 0.6, 0.8, 1.0]
        }
    })
    log_result("マテリアル適用", material_result)
    
    # 9. FBXとしてエクスポート
    logger.info("9. FBXとしてエクスポート...")
    export_result = client.execute_blender_command("export_model", {
        "model_name": "PlayerRobot",
        "export_format": "fbx",
        "export_path": "./exports/PlayerRobot.fbx"
    })
    log_result("FBXエクスポート", export_result)
    
    # 10. UE5にインポート
    logger.info("10. UE5にインポート...")
    import_result = client.import_asset_from_blender("PlayerRobot", "fbx")
    log_result("UE5インポート", import_result)
    
    logger.info("=== ロボット型プレイヤーキャラクターの作成完了 ===")
    return client

def create_game_level(client):
    """
    ゲームレベルを作成する
    
    引数:
        client: MCPクライアントインスタンス
    """
    logger.info("=== ゲームレベルの作成開始 ===")
    
    # 1. 新しいレベルを作成
    logger.info("1. 新しいレベルを作成...")
    level_result = client.execute_unreal_command("create_level", {
        "name": "RobotGameLevel",
        "template": "ThirdPerson"
    })
    log_result("レベル作成", level_result)
    
    # 2. 地形を生成
    logger.info("2. 地形を生成...")
    terrain_result = client.execute_unreal_command("generate_terrain", {
        "size_x": 4096, 
        "size_y": 4096,
        "height_variation": "medium",
        "terrain_type": "plains"
    })
    log_result("地形生成", terrain_result)
    
    # 3. プレイヤーキャラクターモデルを配置
    logger.info("3. ロボットキャラクターを配置...")
    place_result = client.execute_unreal_command("place_asset", {
        "asset_path": "/Game/Assets/PlayerRobot",
        "location": [0, 0, 100],
        "rotation": [0, 0, 0],
        "scale": [1, 1, 1]
    })
    log_result("キャラクター配置", place_result)
    
    # 4. コレクティブルアイテムを作成
    logger.info("4. 収集アイテムBlueprintを作成...")
    bp_result = client.generate_blueprint_from_ai(
        "BP_CollectibleCoin", 
        "Actor", 
        "プレイヤーが近づくと収集できる回転するコイン。収集するとスコアが加算される。"
    )
    log_result("収集アイテム作成", bp_result)
    
    # 5. ゲームモードBlueprintを作成
    logger.info("5. ゲームモードBlueprintを作成...")
    gm_result = client.generate_blueprint_from_ai(
        "BP_RobotGameMode", 
        "GameModeBase", 
        "プレイヤーのスコアを管理し、すべてのコインを集めるとゲームクリアになるゲームモード。"
    )
    log_result("ゲームモード作成", gm_result)
    
    # 6. 植生を配置
    logger.info("6. 植生を配置...")
    foliage_result = client.execute_unreal_command("place_foliage", {
        "foliage_type": "Trees",
        "density": 0.1,
        "area": [0, 0, 4096, 4096]
    })
    log_result("植生配置", foliage_result)
    
    # 7. ライティングビルド
    logger.info("7. ライティングをビルド...")
    light_result = client.execute_unreal_command("build_lighting", {
        "quality": "Medium"
    })
    log_result("ライティングビルド", light_result)
    
    logger.info("=== ゲームレベルの作成完了 ===")
    return client

def log_result(action, result):
    """
    実行結果をログに記録する
    
    引数:
        action (str): 実行したアクション名
        result (dict): 実行結果
    """
    if isinstance(result, dict):
        status = result.get("status", "unknown")
        success = status == "success"
        message = result.get("message", "結果メッセージなし")
        
        if success:
            logger.info(f"{action}: 成功 - {message}")
        else:
            logger.error(f"{action}: 失敗 - {message}")
            if "error" in result:
                logger.error(f"エラー詳細: {result['error']}")
    else:
        logger.warning(f"{action}: 不明な結果形式 - {str(result)}")

if __name__ == "__main__":
    try:
        # ロボットキャラクターを作成
        client = create_robot_character()
        
        # ゲームレベルを作成
        create_game_level(client)
        
        print("\n🎮 ロボットゲーム作成完了!")
        print("作成内容:")
        print("- ロボット型プレイヤーキャラクター (PlayerRobot)")
        print("- 収集アイテムのBlueprintロジック (BP_CollectibleCoin)")
        print("- ゲームモード (BP_RobotGameMode)")
        print("- 平原タイプの地形と木々")
        print("\n👉 UE5エディタでRobotGameLevelを開いてゲームをプレイできます")
        
    except Exception as e:
        logger.exception(f"実行中にエラーが発生しました: {str(e)}")
        print(f"❌ エラーが発生しました: {str(e)}")
        sys.exit(1) 
