#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5トレジャーハントゲーム作成スクリプト

このスクリプトは、UE5で宝探しゲームを作成します。
Blenderからエクスポートされたアセットをインポートして
ゲームレベルを構築します。

主な機能:
- サードパーソンのプレイヤーキャラクター設定
- 宝箱やアイテムなどのゲームオブジェクト配置
- 収集・スコアシステムの構築
- ゲーム進行の制御

使用方法:
1. Blenderでblender_direct_script.pyを実行しアセットを作成
2. このスクリプトを実行してUE5ゲームを構築
"""

import logging
import sys
import os
import json
import time
import random

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("treasure_game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("treasure_game")

# UE5クライアントモックの設定
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

def create_treasure_hunt_game():
    """
    トレジャーハントゲームを作成する
    """
    logger.info("=== トレジャーハントゲーム作成開始 ===")
    
    # MCPサーバーに接続
    logger.info("MCPサーバーに接続...")
    client = connect_to_mcp()
    
    # 1. 新しいレベルを作成（サードパーソンテンプレート）
    logger.info("1. 新しいレベルを作成...")
    level_result = client.execute_unreal_command("create_level", {
        "name": "TreasureHuntLevel",
        "template": "ThirdPerson"
    })
    log_result("レベル作成", level_result)
    
    # 2. 島のような地形を生成
    logger.info("2. 島の地形を生成...")
    terrain_result = client.execute_unreal_command("generate_terrain", {
        "size_x": 5000, 
        "size_y": 5000,
        "height_variation": "medium",
        "terrain_type": "island"
    })
    log_result("地形生成", terrain_result)
    
    # 3. Blenderで作成したアセットをインポート
    logger.info("3. ゲームアセットをインポート...")
    
    # 宝箱をインポート
    chest_import_result = client.execute_unreal_command("import_asset", {
        "path": f"{os.path.abspath('./exports/TreasureChest.fbx')}",
        "destination": "/Game/Assets/TreasureChest"
    })
    log_result("宝箱インポート", chest_import_result)
    
    # ポーション瓶をインポート
    potion_import_result = client.execute_unreal_command("import_asset", {
        "path": f"{os.path.abspath('./exports/PotionBottle.fbx')}",
        "destination": "/Game/Assets/PotionBottle"
    })
    log_result("ポーションインポート", potion_import_result)
    
    # コインをインポート
    coin_import_result = client.execute_unreal_command("import_asset", {
        "path": f"{os.path.abspath('./exports/GameCoin.fbx')}",
        "destination": "/Game/Assets/GameCoin"
    })
    log_result("コインインポート", coin_import_result)
    
    # 4. ゲームアイテムの収集機能を持つBlueprintを作成
    logger.info("4. 収集アイテムBlueprintを作成...")
    
    # 宝箱Blueprint
    chest_bp_result = client.generate_blueprint_from_ai(
        "BP_TreasureChest", 
        "Actor", 
        "プレイヤーが近づくと開く宝箱。開くとコインや他のアイテムが出現する。"
    )
    log_result("宝箱Blueprint作成", chest_bp_result)
    
    # ポーションBottle
    potion_bp_result = client.generate_blueprint_from_ai(
        "BP_HealthPotion", 
        "Actor", 
        "プレイヤーが収集するとヘルスが回復するポーション。回転して光る効果がある。"
    )
    log_result("ポーションBlueprint作成", potion_bp_result)
    
    # コインBlueprint
    coin_bp_result = client.generate_blueprint_from_ai(
        "BP_Coin", 
        "Actor", 
        "プレイヤーが収集するとスコアが増えるコイン。回転しながら上下に浮遊する。"
    )
    log_result("コインBlueprint作成", coin_bp_result)
    
    # 5. ゲームモードを作成
    logger.info("5. ゲームモードを作成...")
    gamemode_result = client.generate_blueprint_from_ai(
        "BP_TreasureHuntGameMode", 
        "GameModeBase", 
        "プレイヤーのスコアとヘルスを管理し、すべての宝箱を見つけるとゲームクリアになるゲームモード。"
    )
    log_result("ゲームモード作成", gamemode_result)
    
    # 6. HUDを作成
    logger.info("6. ゲームHUDを作成...")
    hud_result = client.generate_blueprint_from_ai(
        "BP_TreasureHuntHUD", 
        "HUD", 
        "プレイヤーのスコア、ヘルス、見つけた宝箱の数を表示するHUD。"
    )
    log_result("HUD作成", hud_result)
    
    # 7. アイテムをレベルに配置
    logger.info("7. ゲームアイテムを配置...")
    
    # 宝箱を配置（5個）
    chest_locations = [
        (1000, 500, 150),
        (-800, 700, 120),
        (600, -900, 100),
        (-500, -600, 200),
        (1200, -300, 180)
    ]
    
    for i, loc in enumerate(chest_locations):
        chest_place_result = client.execute_unreal_command("place_asset", {
            "asset_path": "/Game/Blueprints/BP_TreasureChest",
            "location": loc,
            "rotation": (0, random.randint(0, 360), 0),
            "scale": (2.0, 2.0, 2.0)
        })
        log_result(f"宝箱{i+1}配置", chest_place_result)
    
    # ポーションを配置（8個）
    potion_locations = [
        (300, 400, 150),
        (-200, 500, 120),
        (700, -300, 100),
        (-600, -200, 150),
        (900, 200, 160),
        (-400, 800, 130),
        (500, -700, 110),
        (-300, -500, 140)
    ]
    
    for i, loc in enumerate(potion_locations):
        potion_place_result = client.execute_unreal_command("place_asset", {
            "asset_path": "/Game/Blueprints/BP_HealthPotion",
            "location": loc,
            "rotation": (0, 0, 0),
            "scale": (1.5, 1.5, 1.5)
        })
        log_result(f"ポーション{i+1}配置", potion_place_result)
    
    # コインを配置（ランダムに20個）
    for i in range(20):
        x = random.randint(-1200, 1200)
        y = random.randint(-1200, 1200)
        z = random.randint(120, 200)
        
        coin_place_result = client.execute_unreal_command("place_asset", {
            "asset_path": "/Game/Blueprints/BP_Coin",
            "location": (x, y, z),
            "rotation": (0, 0, 0),
            "scale": (1.0, 1.0, 1.0)
        })
        log_result(f"コイン{i+1}配置", coin_place_result)
    
    # 8. 植生を配置
    logger.info("8. 植生を配置...")
    trees_result = client.execute_unreal_command("place_foliage", {
        "foliage_type": "Trees",
        "density": 0.2,
        "area": [-2000, -2000, 4000, 4000]
    })
    log_result("木の配置", trees_result)
    
    rocks_result = client.execute_unreal_command("place_foliage", {
        "foliage_type": "Rocks",
        "density": 0.1,
        "area": [-2000, -2000, 4000, 4000]
    })
    log_result("岩の配置", rocks_result)
    
    grass_result = client.execute_unreal_command("place_foliage", {
        "foliage_type": "Grass",
        "density": 0.5,
        "area": [-2000, -2000, 4000, 4000]
    })
    log_result("草の配置", grass_result)
    
    # 9. 環境設定（時間、天気など）
    logger.info("9. 環境設定...")
    environment_result = client.execute_unreal_command("set_environment", {
        "sky_type": "dynamic",
        "time_of_day": "evening",
        "weather": "clear"
    })
    log_result("環境設定", environment_result)
    
    # 10. ライティングをビルド
    logger.info("10. ライティングをビルド...")
    light_result = client.execute_unreal_command("build_lighting", {
        "quality": "Medium"
    })
    log_result("ライティングビルド", light_result)
    
    logger.info("=== トレジャーハントゲーム作成完了 ===")
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
        # トレジャーハントゲームを作成
        client = create_treasure_hunt_game()
        
        print("\n🎮 トレジャーハントゲーム作成完了!")
        print("作成内容:")
        print("- 島型のオープンワールド地形")
        print("- 宝箱、ポーション、コインなどの収集アイテム")
        print("- スコアシステムとHUD表示")
        print("- 豊かな自然環境（木、岩、草）")
        print("- 美しい夕方の照明効果")
        print("\n👉 UE5エディタでTreasureHuntLevelを開いてゲームをプレイできます")
        
    except Exception as e:
        logger.exception(f"実行中にエラーが発生しました: {str(e)}")
        print(f"❌ エラーが発生しました: {str(e)}")
        sys.exit(1) 
