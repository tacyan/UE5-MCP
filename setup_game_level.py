#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5エディタ内にゲームレベルを作成するスクリプト

このスクリプトは、UE5エディタ内にゲームレベルを作成し、
プレイヤーと敵を配置します。また、ゲームモードも設定します。
直接Unrealエディタ内で実行するPythonコードを使用します。

使用方法:
  python setup_game_level.py
"""

import logging
import os
import sys
import requests
import json
import time

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# UE5エディタのPythonスクリプトを実行するためのRESTエンドポイント
UNREAL_ENDPOINT = "http://localhost:8080/api/unreal/execute"
UNREAL_STATUS_ENDPOINT = "http://localhost:8080/api/status"

def check_unreal_connection():
    """UE5エディタとの接続を確認する"""
    try:
        response = requests.get(UNREAL_STATUS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            if status_data.get("unreal", {}).get("status") == "connected":
                logger.info("UE5エディタに接続しました")
                return True
            else:
                logger.error(f"UE5エディタが接続されていません: {status_data.get('unreal', {}).get('status')}")
        else:
            logger.error(f"UE5エディタとの接続確認に失敗しました: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"UE5エディタとの接続中にエラーが発生しました: {str(e)}")
    
    return False

def execute_unreal_python(script):
    """UE5エディタ内でPythonスクリプトを実行する"""
    try:
        data = {
            "command": "execute_python",
            "params": {
                "script": script
            }
        }
        
        # スクリプトを実行
        response = requests.post(UNREAL_ENDPOINT, json=data)
        
        # レスポンスをチェック
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                logger.info("UE5スクリプトの実行が成功しました")
                return True, result
            else:
                logger.error(f"UE5スクリプトの実行が失敗しました: {result.get('message')}")
                return False, result
        else:
            logger.error(f"UE5への接続に失敗しました: {response.status_code}")
            return False, {"status": "error", "message": f"HTTP error: {response.status_code}"}
            
    except Exception as e:
        logger.exception(f"UE5スクリプト実行中にエラーが発生しました: {str(e)}")
        return False, {"status": "error", "message": str(e)}

def create_game_level():
    """UE5エディタ内にゲームレベルを作成する"""
    logger.info("UE5エディタ内にゲームレベルを作成しています...")
    
    # ゲームレベル作成スクリプト
    script = """
import unreal
import time

# レベル情報
maps_path = "/Game/ShooterGame/Maps"
level_name = "ShooterGameLevel"
full_level_path = f"{maps_path}/{level_name}"
player_bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"
enemy_bp_path = "/Game/ShooterGame/Blueprints/BP_EnemyShip"
game_mode_bp_path = "/Game/ShooterGame/Blueprints/BP_ShooterGameMode"

# レベルサブシステムを取得
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# フォルダが存在することを確認（念のため）
if not unreal.EditorAssetLibrary.does_directory_exist(maps_path):
    unreal.EditorAssetLibrary.make_directory(maps_path)
    print(f"Mapsディレクトリを作成しました: {maps_path}")

try:
    # 新しいレベルを作成
    current_level = level_subsystem.new_level(full_level_path)
    print(f"新しいレベルを作成しました: {full_level_path}")
    
    # レベルを保存
    level_subsystem.save_current_level()
    print("レベルを保存しました")
    
    # プレイヤーを配置
    if unreal.EditorAssetLibrary.does_asset_exist(player_bp_path):
        player_class = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
        player_location = unreal.Vector(0, 0, 100)
        player_rotation = unreal.Rotator(0, 0, 0)
        player_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(player_class, player_location, player_rotation)
        print(f"プレイヤーを配置しました: {player_bp_path}")
    else:
        print(f"プレイヤーブループリントが見つかりません: {player_bp_path}")
    
    # 敵を配置
    if unreal.EditorAssetLibrary.does_asset_exist(enemy_bp_path):
        enemy_class = unreal.EditorAssetLibrary.load_blueprint_class(enemy_bp_path)
        
        # 複数の敵を配置
        enemy_positions = [
            unreal.Vector(500, 200, 100),
            unreal.Vector(500, -200, 100),
            unreal.Vector(700, 0, 100),
            unreal.Vector(900, 300, 100),
            unreal.Vector(900, -300, 100)
        ]
        
        for pos in enemy_positions:
            enemy_rotation = unreal.Rotator(0, 180, 0)
            enemy_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(enemy_class, pos, enemy_rotation)
        print(f"敵を配置しました: {enemy_bp_path}")
    else:
        print(f"敵ブループリントが見つかりません: {enemy_bp_path}")
    
    # レベルを保存
    level_subsystem.save_current_level()
    print("レベルの変更を保存しました")
    
    # ゲームモードを設定
    if unreal.EditorAssetLibrary.does_asset_exist(game_mode_bp_path):
        game_mode_class = unreal.EditorAssetLibrary.load_blueprint_class(game_mode_bp_path)
        
        # レベルのゲームモードを設定
        with unreal.ScopedEditorTransaction("Set Level GameMode") as trans:
            world_settings = unreal.EditorLevelLibrary.get_game_mode_settings_for_current_level()
            if world_settings:
                world_settings.set_editor_property("game_mode_override", game_mode_class)
                print(f"ゲームモードを設定しました: {game_mode_bp_path}")
            else:
                print("ワールド設定が見つかりません")
    else:
        print(f"ゲームモードブループリントが見つかりません: {game_mode_bp_path}")
    
    # 最終的なレベル保存
    level_subsystem.save_current_level()
    print("最終レベル変更を保存しました")
    
    # 以下の処理は非常に重要: 新しいレベルをデフォルトマップとして設定
    try:
        project_settings = unreal.get_default_object(unreal.EditorProjectAppearanceSettings)
        project_settings.set_editor_property("default_map_editor", f"{full_level_path}.{level_name}")
        print(f"デフォルトマップを設定しました: {full_level_path}")
    except Exception as e:
        print(f"デフォルトマップ設定中にエラー: {e}")
    
    # コンテンツブラウザを更新
    unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
    unreal.EditorAssetLibrary.refresh_asset_directories([maps_path])
    
    print("ゲームレベルの作成が完了しました")
    
    return {{"success": True, "level_path": full_level_path}}
except Exception as e:
    print(f"レベル作成中にエラーが発生しました: {e}")
    return {{"success": False, "error": str(e)}}
"""
    
    # スクリプトを実行
    success, result = execute_unreal_python(script)
    return success

def main():
    """メイン処理"""
    logger.info("UE5エディタ内のゲームレベル作成を開始します...")
    
    # UE5エディタとの接続を確認
    if not check_unreal_connection():
        logger.error("UE5エディタに接続できませんでした。UE5エディタが起動していて、MCPプラグインが有効になっていることを確認してください。")
        return False
    
    # ゲームレベルを作成
    if create_game_level():
        logger.info("ゲームレベルの作成に成功しました")
        
        # 少し待機してUE5エディタに反映されるのを待つ
        time.sleep(2)
        
        logger.info("UE5エディタでコンテンツブラウザを更新（F5キー）してください")
        logger.info("作成したレベルを開いてプレイできます")
        logger.info("セットアップが完了しました")
        
        return True
    else:
        logger.error("ゲームレベルの作成に失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
