#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シンプルなトレジャーハントゲーム作成スクリプト

MCPフレームワークを使用してシンプルなトレジャーハントゲームを作成するスクリプト。
Blenderで作成したアセットをインポートし、ゲームプレイに必要なブループリントを生成します。

使用法:
  python simple_treasure_game.py
"""

import os
import sys
import json
import time
import requests
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("simple_treasure_game")

# MCPサーバーURL
MCP_SERVER = f"http://127.0.0.1:8080"

class TreasureGameCreator:
    """シンプルなトレジャーハントゲームを作成するクラス"""
    
    def __init__(self):
        """初期化"""
        self.server_url = MCP_SERVER
        self.exports_dir = os.path.join(os.getcwd(), "exports")
        
        # サーバー接続確認
        self.check_connection()
    
    def check_connection(self):
        """サーバー接続確認"""
        try:
            response = requests.get(f"{self.server_url}/api/status")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    logger.info("MCPサーバーに接続しました")
                    return True
            logger.error("MCPサーバーに接続できません")
            return False
        except Exception as e:
            logger.error(f"サーバー接続エラー: {str(e)}")
            return False
    
    def import_assets(self):
        """アセットをインポート"""
        logger.info("アセットのインポートを開始します...")
        
        asset_list = [
            "TreasureChest",
            "Coin",
            "HealthPotion"
        ]
        
        for asset_name in asset_list:
            asset_path = os.path.join(self.exports_dir, f"{asset_name}.fbx")
            if not os.path.exists(asset_path):
                logger.warning(f"アセットが見つかりません: {asset_path}")
                continue
                
            logger.info(f"アセットをインポート: {asset_name}")
            
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "import_asset",
                    "params": {
                        "path": asset_path,
                        "destination": f"/Game/Assets/{asset_name}"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"インポート結果: {result.get('status', 'unknown')}")
            else:
                logger.error(f"インポートエラー: {response.status_code}")
    
    def create_blueprints(self):
        """ブループリントを作成"""
        logger.info("ブループリントの作成を開始します...")
        
        blueprints = [
            {
                "name": "BP_TreasureChest",
                "parent_class": "Actor",
                "description": "プレイヤーが近づくと開く宝箱。コインとアイテムを含む。"
            },
            {
                "name": "BP_Coin",
                "parent_class": "Actor",
                "description": "回転するコイン。収集するとスコアが増える。"
            },
            {
                "name": "BP_HealthPotion",
                "parent_class": "Actor",
                "description": "ヘルスポーション。収集するとプレイヤーのヘルスが回復する。"
            },
            {
                "name": "BP_TreasureGameMode",
                "parent_class": "GameModeBase",
                "description": "トレジャーハントゲームのルールを管理するゲームモード。"
            }
        ]
        
        for bp in blueprints:
            logger.info(f"ブループリント作成: {bp['name']}")
            
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "create_blueprint",
                    "params": {
                        "name": bp["name"],
                        "parent_class": bp["parent_class"],
                        "description": bp["description"]
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"作成結果: {result.get('status', 'unknown')}")
            else:
                logger.error(f"ブループリント作成エラー: {response.status_code}")
    
    def create_level(self):
        """ゲームレベルを作成"""
        logger.info("ゲームレベルの作成を開始します...")
        
        # 新しいレベルを作成
        response = requests.post(
            f"{self.server_url}/api/unreal/execute",
            json={
                "command": "create_level",
                "params": {
                    "name": "TreasureHuntMap",
                    "template": "Default"
                }
            }
        )
        
        if response.status_code != 200:
            logger.error(f"レベル作成エラー: {response.status_code}")
            return
        
        # 宝箱を配置
        chest_positions = [
            [500, 500, 50],
            [-500, 500, 50],
            [500, -500, 50],
            [-500, -500, 50]
        ]
        
        for i, position in enumerate(chest_positions):
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "place_actor",
                    "params": {
                        "blueprint": "/Game/Blueprints/BP_TreasureChest",
                        "name": f"TreasureChest_{i+1}",
                        "location": position,
                        "rotation": [0, 0, 0],
                        "scale": [1, 1, 1]
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info(f"宝箱を配置しました: TreasureChest_{i+1}")
            else:
                logger.error(f"宝箱配置エラー: {response.status_code}")
        
        # コインを配置
        coin_positions = [
            [300, 300, 50],
            [-300, 300, 50],
            [300, -300, 50],
            [-300, -300, 50],
            [0, 0, 50]
        ]
        
        for i, position in enumerate(coin_positions):
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "place_actor",
                    "params": {
                        "blueprint": "/Game/Blueprints/BP_Coin",
                        "name": f"Coin_{i+1}",
                        "location": position,
                        "rotation": [0, 0, 0],
                        "scale": [1, 1, 1]
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info(f"コインを配置しました: Coin_{i+1}")
            else:
                logger.error(f"コイン配置エラー: {response.status_code}")
        
        # ヘルスポーションを配置
        potion_positions = [
            [200, 200, 50],
            [-200, 200, 50]
        ]
        
        for i, position in enumerate(potion_positions):
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "place_actor",
                    "params": {
                        "blueprint": "/Game/Blueprints/BP_HealthPotion",
                        "name": f"HealthPotion_{i+1}",
                        "location": position,
                        "rotation": [0, 0, 0],
                        "scale": [1, 1, 1]
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info(f"ヘルスポーションを配置しました: HealthPotion_{i+1}")
            else:
                logger.error(f"ヘルスポーション配置エラー: {response.status_code}")
        
        # プレイヤースタート位置を設定
        response = requests.post(
            f"{self.server_url}/api/unreal/execute",
            json={
                "command": "place_actor",
                "params": {
                    "type": "PlayerStart",
                    "name": "PlayerStart",
                    "location": [0, 0, 100],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1]
                }
            }
        )
        
        if response.status_code == 200:
            logger.info("プレイヤースタート位置を設定しました")
        else:
            logger.error(f"プレイヤースタート位置設定エラー: {response.status_code}")
        
        # ゲームモードを設定
        response = requests.post(
            f"{self.server_url}/api/unreal/execute",
            json={
                "command": "set_game_mode",
                "params": {
                    "game_mode": "/Game/Blueprints/BP_TreasureGameMode"
                }
            }
        )
        
        if response.status_code == 200:
            logger.info("ゲームモードを設定しました")
        else:
            logger.error(f"ゲームモード設定エラー: {response.status_code}")
        
        # レベルを保存
        response = requests.post(
            f"{self.server_url}/api/unreal/execute",
            json={
                "command": "save_level",
                "params": {}
            }
        )
        
        if response.status_code == 200:
            logger.info("レベルを保存しました")
        else:
            logger.error(f"レベル保存エラー: {response.status_code}")
    
    def run(self):
        """ゲーム作成プロセスを実行"""
        logger.info("シンプルなトレジャーハントゲームの作成を開始します...")
        
        # アセットをインポート
        self.import_assets()
        
        # ブループリントを作成
        self.create_blueprints()
        
        # レベルを作成
        self.create_level()
        
        logger.info("ゲーム作成が完了しました！")

# メイン実行
if __name__ == "__main__":
    creator = TreasureGameCreator()
    creator.run() 
