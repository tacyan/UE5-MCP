#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5シンプルゲーム作成スクリプト

このスクリプトはMCPフレームワークを使用してUnreal Engine 5で
シンプルな3Dアクションゲームを作成するデモンストレーションです。

主な機能:
- MCPクライアント接続の確立
- 新しいレベルの作成
- 地形の生成
- プレイヤーキャラクターの設定
- 基本的なゲームロジックの構築
- 環境アセットの配置

使用方法:
    python simple_ue5_game.py

制限事項:
- MCPサーバーが起動している必要があります
- 実際のUE5の動作はモックされています（UE5未インストール環境でも実行可能）
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
        logging.FileHandler("simple_ue5_game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("simple_ue5_game")

# UE5MCPクライアントをインポート
try:
    # ここでunrealモジュールをモックします（実際のUE5環境でなくても動作するように）
    if 'unreal' not in sys.modules:
        # モックunrealモジュールを定義
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
        
    from ue5_mcp_client import UE5MCPClient, connect_to_mcp
except ImportError as e:
    logger.error(f"必要なモジュールのインポートに失敗しました: {str(e)}")
    sys.exit(1)

def create_simple_game():
    """
    シンプルなゲームを作成する
    """
    logger.info("===== シンプルUE5ゲーム作成開始 =====")
    
    # MCPサーバーに接続
    logger.info("MCPサーバーに接続...")
    client = connect_to_mcp()
    
    # 1. 新しいレベルの作成
    logger.info("1. 新しいレベルを作成...")
    level_result = client.execute_unreal_command("create_level", {
        "name": "SimpleActionGame",
        "template": "ThirdPerson"  # UE5の標準サードパーソンテンプレートを使用
    })
    log_command_result("レベル作成", level_result)
    
    # 2. 地形の生成
    logger.info("2. 地形を生成...")
    terrain_result = client.execute_unreal_command("generate_terrain", {
        "size_x": 8192,
        "size_y": 8192,
        "height_variation": "medium",
        "terrain_type": "mountainous"
    })
    log_command_result("地形生成", terrain_result)
    
    # 3. 基本的なBlueprintロジックを生成
    logger.info("3. 基本的なゲームロジックのBlueprintを生成...")
    
    # プレイヤーキャラクター用のアイテム収集ロジック
    player_bp_result = client.generate_blueprint_from_ai(
        "BP_CollectibleItem",
        "Actor",
        "プレイヤーが近づくと収集できるアイテム。収集するとスコアが加算され、エフェクトが表示される。"
    )
    log_command_result("アイテムBlueprintの生成", player_bp_result)
    
    # ゲームモード用のBlueprintを作成
    gamemode_bp_result = client.generate_blueprint_from_ai(
        "BP_SimpleActionGameMode",
        "GameModeBase",
        "プレイヤーのスコアを管理し、一定時間経過後にゲーム終了を判定するゲームモード。"
    )
    log_command_result("ゲームモードBlueprintの生成", gamemode_bp_result)
    
    # 4. 環境アセットの配置
    logger.info("4. 環境アセットを配置...")
    
    # 植生を追加
    foliage_result = client.execute_unreal_command("place_foliage", {
        "foliage_type": "Trees",
        "density": 0.5,
        "area": [0, 0, 8192, 8192]
    })
    log_command_result("植生配置", foliage_result)
    
    # 岩などのアセットを配置
    rock_result = client.execute_unreal_command("place_foliage", {
        "foliage_type": "Rocks",
        "density": 0.2,
        "area": [1000, 1000, 6000, 6000]
    })
    log_command_result("岩の配置", rock_result)
    
    # 5. ライティングのビルド
    logger.info("5. ライティングをビルド...")
    lighting_result = client.execute_unreal_command("build_lighting", {
        "quality": "Production"
    })
    log_command_result("ライティングビルド", lighting_result)
    
    logger.info("===== シンプルUE5ゲーム作成完了 =====")
    logger.info("""
作成したゲームの概要:
- ゲームタイプ: 3Dアクションゲーム
- レベル名: SimpleActionGame
- 目標: アイテムを収集してスコアを稼ぐ
- 機能: プレイヤーキャラクター、収集アイテム、スコアシステム
- 環境: 山岳地形、森林
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
        create_simple_game()
    except Exception as e:
        logger.exception(f"実行中にエラーが発生しました: {str(e)}") 
