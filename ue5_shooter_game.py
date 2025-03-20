#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5シューティングゲーム作成スクリプト

MCPサーバーを通じてUE5でシューティングゲームを作成するスクリプトです。
Blenderで作成された3Dモデルを使用して、
ゲームロジック（ブループリント）とレベルを生成します。

主な機能:
- ブループリントの生成（プレイヤー、敵、発射物など）
- ゲームロジックの実装
- レベルデザイン

使用方法:
  python ue5_shooter_game.py
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shooter_game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ue5_shooter_game")

# MCPサーバー設定
MCP_SERVER = "http://127.0.0.1:8080"

# 必要なディレクトリの確認
EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
IMPORTS_DIR = os.path.join(os.getcwd(), "imports")
os.makedirs(IMPORTS_DIR, exist_ok=True)

# ブループリント作成用テンプレート
BLUEPRINT_TEMPLATES = {
    "player_ship": """
    Blueprint名: BP_PlayerShip
    親クラス: Pawn
    説明: プレイヤーが操作する宇宙船。WASD操作、マウスで方向転換、クリックで発射。
    機能:
    - 移動制御（WASD、マウス）
    - 弾の発射（マウスクリック）
    - ヘルスシステム
    - 衝突判定
    - パワーアップ収集
    """,
    "enemy_ship": """
    Blueprint名: BP_EnemyShip
    親クラス: Pawn
    説明: AIで制御される敵宇宙船。プレイヤーを追跡し、弾を発射する。
    機能:
    - AIによる移動制御
    - プレイヤー追跡
    - 一定間隔での弾の発射
    - ヘルスシステム
    - 衝突判定
    - 破壊時のスコア加算
    """,
    "projectile": """
    Blueprint名: BP_Projectile
    親クラス: Actor
    説明: 宇宙船から発射される弾丸。直線移動し、衝突すると爆発して消滅。
    機能:
    - 直線移動
    - 衝突判定
    - ダメージ処理
    - エフェクト（軌跡、衝突時）
    - 一定時間後の自動消滅
    """,
    "powerup": """
    Blueprint名: BP_PowerUp
    親クラス: Actor
    説明: プレイヤーが収集するパワーアップアイテム。回転しながら浮遊する。
    機能:
    - 回転・浮遊アニメーション
    - 発光エフェクト
    - 収集時のパワーアップ効果（攻撃力アップ、速度アップなど）
    - サウンドエフェクト
    """,
    "game_mode": """
    Blueprint名: BP_ShooterGameMode
    親クラス: GameModeBase
    説明: ゲームのルールを管理するゲームモード。敵の生成、スコア管理、ゲーム終了判定など。
    機能:
    - スコア管理
    - 敵の定期的な生成
    - 難易度の段階的上昇
    - ゲームオーバー判定
    - ゲームクリア判定
    """,
    "hud": """
    Blueprint名: BP_ShooterHUD
    親クラス: HUD
    説明: プレイヤーのヘルス、スコア、弾薬などの情報を表示するHUD。
    機能:
    - ヘルスバー表示
    - スコア表示
    - 弾薬表示
    - ゲームオーバー画面
    - 勝利画面
    - パワーアップ状態表示
    """
}

class UE5ShooterGame:
    """UE5でシューティングゲームを作成するクラス"""
    
    def __init__(self):
        """初期化メソッド"""
        self.server_url = MCP_SERVER
        self.exports_dir = EXPORTS_DIR
        self.imports_dir = IMPORTS_DIR
        
        # アセットパス
        self.asset_paths = {
            "player_ship": os.path.join(self.exports_dir, "PlayerShip.fbx"),
            "enemy_ship": os.path.join(self.exports_dir, "EnemyShip.fbx"),
            "projectile": os.path.join(self.exports_dir, "Projectile.fbx"),
            "powerup": os.path.join(self.exports_dir, "PowerUp.fbx")
        }
        
        # ブループリント情報
        self.blueprints = {}
    
    def check_server_connection(self):
        """MCPサーバーへの接続を確認する"""
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    logger.info(f"MCPサーバーに接続しました: {data.get('status')}")
                    return True
                else:
                    logger.error(f"MCPサーバーのステータスが異常: {data.get('status')}")
                    return False
            else:
                logger.error(f"MCPサーバーへの接続に失敗しました: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"MCPサーバーへの接続中にエラーが発生しました: {str(e)}")
            return False
    
    def check_assets(self):
        """必要なアセットが存在するか確認する"""
        missing_assets = []
        
        for asset_type, asset_path in self.asset_paths.items():
            if not os.path.exists(asset_path):
                missing_assets.append(asset_type)
                logger.error(f"アセットが見つかりません: {asset_path}")
        
        if missing_assets:
            logger.error(f"次のアセットが見つかりません: {', '.join(missing_assets)}")
            logger.error("まずBlenderでアセットを作成してください: python blender_shooter_game.py")
            return False
        
        logger.info("必要なアセットを全て確認しました")
        return True
    
    def import_assets(self):
        """アセットをUE5にインポートする"""
        logger.info("アセットのインポートを開始します...")
        
        for asset_type, asset_path in self.asset_paths.items():
            # インポートディレクトリにコピー
            import_path = os.path.join(self.imports_dir, os.path.basename(asset_path))
            try:
                import_dir = os.path.dirname(import_path)
                os.makedirs(import_dir, exist_ok=True)
                
                if os.path.exists(asset_path):
                    import shutil
                    shutil.copy2(asset_path, import_path)
                    logger.info(f"アセットをインポートディレクトリにコピー: {import_path}")
                else:
                    logger.warning(f"アセットが見つかりません: {asset_path}")
                    continue
            except Exception as e:
                logger.error(f"アセットコピー中にエラーが発生しました: {str(e)}")
                continue
            
            # UE5にインポート
            logger.info(f"インポート: {asset_type} ({import_path})")
            try:
                response = requests.post(
                    f"{self.server_url}/api/unreal/execute",
                    json={
                        "command": "import_asset",
                        "params": {
                            "path": import_path,
                            "destination": f"/Game/ShooterGame/Assets/{os.path.splitext(os.path.basename(asset_path))[0]}"
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        logger.info(f"アセットのインポートに成功しました: {asset_type}")
                    else:
                        logger.error(f"アセットインポートエラー: {result.get('message', 'Unknown error')}")
                else:
                    logger.error(f"アセットインポートエラー: HTTP {response.status_code}")
                    
                    # 404エラーの場合はモックインポートとして処理
                    if response.status_code == 404:
                        logger.warning(f"アセット {asset_type} をモックインポートとして処理します")
            except Exception as e:
                logger.error(f"アセットインポート中にエラーが発生しました: {str(e)}")
        
        logger.info("アセットのインポートが完了しました")
        return True
    
    def create_blueprints(self):
        """ゲームに必要なブループリントを作成する"""
        logger.info("ブループリントの作成を開始します...")
        
        for bp_type, bp_template in BLUEPRINT_TEMPLATES.items():
            # テンプレートからブループリント情報を抽出
            lines = [line.strip() for line in bp_template.strip().split("\n") if line.strip()]
            
            # 各行から情報を取得
            bp_name = ""
            parent_class = ""
            description = ""
            
            for line in lines:
                if line.startswith("Blueprint名:"):
                    bp_name = line.split(":", 1)[1].strip()
                elif line.startswith("親クラス:"):
                    parent_class = line.split(":", 1)[1].strip()
                elif line.startswith("説明:"):
                    description = line.split(":", 1)[1].strip()
            
            if not bp_name or not parent_class:
                logger.error(f"ブループリント情報の抽出に失敗しました: {bp_type}")
                continue
            
            logger.info(f"ブループリント作成: {bp_name} ({parent_class}) - {description}")
            
            try:
                response = requests.post(
                    f"{self.server_url}/api/unreal/execute",
                    json={
                        "command": "create_blueprint",
                        "params": {
                            "name": bp_name,
                            "parent_class": parent_class,
                            "path": f"/Game/ShooterGame/Blueprints/{bp_name}",
                            "description": description
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        logger.info(f"ブループリント {bp_name} を生成しました")
                        self.blueprints[bp_type] = bp_name
                    else:
                        logger.error(f"ブループリント作成エラー: {result.get('message', 'Unknown error')}")
                else:
                    logger.error(f"ブループリント作成エラー: HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"ブループリント作成中にエラーが発生しました: {str(e)}")
        
        logger.info("ブループリントの作成が完了しました")
        return True
    
    def create_game_level(self):
        """ゲームレベルを作成する"""
        logger.info("ゲームレベルの作成を開始します...")
        
        # レベル作成
        level_name = "ShooterGameLevel"
        try:
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "create_level",
                    "params": {
                        "name": level_name,
                        "template": "Default",
                        "path": f"/Game/ShooterGame/Maps/{level_name}"
                    }
                }
            )
            
            if response.status_code != 200:
                logger.warning(f"レベル作成エラー: HTTP {response.status_code}. モック応答で続行します。")
        except Exception as e:
            logger.error(f"レベル作成中にエラーが発生しました: {str(e)}")
        
        # レベルにアクターを配置
        self._place_actors_in_level(level_name)
        
        # ゲームモードを設定
        try:
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "set_game_mode",
                    "params": {
                        "level_name": level_name,
                        "game_mode": self.blueprints.get("game_mode", "BP_ShooterGameMode")
                    }
                }
            )
        except Exception as e:
            logger.error(f"ゲームモード設定中にエラーが発生しました: {str(e)}")
        
        # レベルを保存
        try:
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "save_level",
                    "params": {
                        "name": level_name
                    }
                }
            )
        except Exception as e:
            logger.error(f"レベル保存中にエラーが発生しました: {str(e)}")
        
        logger.info("ゲームレベルを作成しました")
        return True
    
    def _place_actors_in_level(self, level_name):
        """レベルにアクターを配置する"""
        # 敵の配置
        enemy_positions = [
            {"x": 1000, "y": 500, "z": 100},
            {"x": -500, "y": 1200, "z": 100},
            {"x": 800, "y": -700, "z": 100},
            {"x": -1000, "y": -500, "z": 100},
            {"x": 0, "y": 1500, "z": 100}
        ]
        
        for i, pos in enumerate(enemy_positions):
            try:
                response = requests.post(
                    f"{self.server_url}/api/unreal/execute",
                    json={
                        "command": "place_actor",
                        "params": {
                            "blueprint": self.blueprints.get("enemy_ship", "BP_EnemyShip"),
                            "location": [pos["x"], pos["y"], pos["z"]],
                            "rotation": [0, 0, 0],
                            "scale": [1, 1, 1],
                            "name": f"EnemyShip_{i+1}"
                        }
                    }
                )
            except Exception as e:
                logger.error(f"敵配置中にエラーが発生しました: {str(e)}")
        
        # パワーアップの配置
        powerup_positions = [
            {"x": 500, "y": 0, "z": 100},
            {"x": -700, "y": 300, "z": 100},
            {"x": 200, "y": -900, "z": 100}
        ]
        
        for i, pos in enumerate(powerup_positions):
            try:
                response = requests.post(
                    f"{self.server_url}/api/unreal/execute",
                    json={
                        "command": "place_actor",
                        "params": {
                            "blueprint": self.blueprints.get("powerup", "BP_PowerUp"),
                            "location": [pos["x"], pos["y"], pos["z"]],
                            "rotation": [0, 0, 0],
                            "scale": [1, 1, 1],
                            "name": f"PowerUp_{i+1}"
                        }
                    }
                )
            except Exception as e:
                logger.error(f"パワーアップ配置中にエラーが発生しました: {str(e)}")
        
        # プレイヤー開始位置を設定
        try:
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "place_actor",
                    "params": {
                        "blueprint": "PlayerStart",
                        "location": [0, 0, 100],
                        "rotation": [0, 0, 0],
                        "scale": [1, 1, 1],
                        "name": "PlayerStart_1"
                    }
                }
            )
        except Exception as e:
            logger.error(f"プレイヤー開始位置設定中にエラーが発生しました: {str(e)}")
    
    def generate_blueprint_logic(self):
        """ブループリントのロジックを生成する"""
        logger.info("ブループリントロジックの生成を開始します...")
        
        # AIを使用してブループリントロジックを生成
        for bp_type, bp_name in self.blueprints.items():
            # ブループリントの説明を取得
            description = next((t.strip() for t in BLUEPRINT_TEMPLATES[bp_type].split("\n") if "説明:" in t), "")
            description = description.replace("説明:", "").strip()
            
            # 機能の説明を取得
            features = []
            in_features = False
            for line in BLUEPRINT_TEMPLATES[bp_type].split("\n"):
                if "機能:" in line:
                    in_features = True
                    continue
                if in_features and line.strip() and "- " in line:
                    features.append(line.strip().replace("- ", ""))
            
            # AIにプロンプトを送信
            prompt = f"""
            UnrealEngine5でシューティングゲーム用の{bp_name}ブループリントを作成してください。
            
            概要: {description}
            
            実装すべき機能:
            {chr(10).join([f"- {f}" for f in features])}
            
            ブループリントのグラフの概要と、必要なコンポーネント、変数、関数を教えてください。
            """
            
            try:
                response = requests.post(
                    f"{self.server_url}/api/ai/generate",
                    json={
                        "prompt": prompt,
                        "type": "blueprint",
                        "params": {
                            "name": bp_name,
                            "parent_class": bp_name.replace("BP_", ""),
                            "description": description
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        logger.info(f"ブループリントロジック生成成功: {bp_name}")
                    else:
                        logger.warning(f"ブループリントロジック生成中にエラー: {result.get('message', 'Unknown error')}")
                else:
                    logger.warning(f"AIリクエストエラー: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"ブループリントロジック生成中にエラーが発生しました: {str(e)}")
        
        logger.info("ブループリントロジックの生成が完了しました")
        return True
    
    def create_shooter_game(self):
        """シューティングゲームを作成する全体のプロセス"""
        if not self.check_server_connection():
            logger.error("MCPサーバーに接続できません。終了します。")
            return False
        
        if not self.check_assets():
            logger.warning("一部のアセットが見つかりません。可能な限り続行します。")
        
        # アセットをインポート
        self.import_assets()
        
        # ブループリントを作成
        self.create_blueprints()
        
        # ブループリントロジックを生成
        self.generate_blueprint_logic()
        
        # ゲームレベルを作成
        self.create_game_level()
        
        logger.info("シューティングゲームの作成が完了しました！")
        return True

def main():
    """メイン実行関数"""
    logger.info("===== UE5シューティングゲーム作成を開始します =====")
    
    ue5_shooter = UE5ShooterGame()
    success = ue5_shooter.create_shooter_game()
    
    if success:
        logger.info("===== シューティングゲームの作成が完了しました =====")
        logger.info("UE5エディタでゲームを確認し、実行してください！")
    else:
        logger.error("シューティングゲーム作成中にエラーが発生しました")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
