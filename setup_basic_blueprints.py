#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5エディタ内に基本的なブループリントを作成するスクリプト

このスクリプトは、UE5エディタ内に基本的なブループリントを作成します。
直接Unrealエディタ内で実行するPythonコードを使用します。

使用方法:
  python setup_basic_blueprints.py
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

def create_basic_blueprints():
    """UE5エディタ内に基本的なブループリントを作成する"""
    logger.info("UE5エディタ内にブループリントを作成しています...")
    
    # ブループリント作成スクリプト
    script = """
import unreal
import time

# 基本パス
base_path = "/Game/ShooterGame/Blueprints"

# ブループリント情報の定義
blueprints_info = [
    {
        "name": "BP_PlayerShip",
        "parent_class": unreal.Pawn,
        "components": [
            {"type": unreal.StaticMeshComponent, "properties": {
                "collision_enabled": unreal.CollisionEnabled.QUERY_AND_PHYSICS
            }},
            {"type": unreal.FloatingPawnMovement, "properties": {
                "max_speed": 1000.0
            }},
            {"type": unreal.CameraComponent, "properties": {
                "relative_location": unreal.Vector(0, 0, 100),
                "relative_rotation": unreal.Rotator(-20, 0, 0)
            }},
            {"type": unreal.SceneComponent, "properties": {
                "component_name": "ProjectileSpawnPoint",
                "relative_location": unreal.Vector(100, 0, 0)
            }}
        ]
    },
    {
        "name": "BP_EnemyShip",
        "parent_class": unreal.Pawn,
        "components": [
            {"type": unreal.StaticMeshComponent, "properties": {
                "collision_enabled": unreal.CollisionEnabled.QUERY_AND_PHYSICS
            }},
            {"type": unreal.FloatingPawnMovement, "properties": {
                "max_speed": 500.0
            }},
            {"type": unreal.SceneComponent, "properties": {
                "component_name": "ProjectileSpawnPoint",
                "relative_location": unreal.Vector(100, 0, 0)
            }}
        ]
    },
    {
        "name": "BP_Projectile",
        "parent_class": unreal.Actor,
        "components": [
            {"type": unreal.StaticMeshComponent, "properties": {
                "collision_enabled": unreal.CollisionEnabled.QUERY_AND_PHYSICS
            }},
            {"type": unreal.SphereComponent, "properties": {
                "sphere_radius": 30.0,
                "collision_enabled": unreal.CollisionEnabled.QUERY_ONLY
            }},
            {"type": unreal.ProjectileMovementComponent, "properties": {
                "initial_speed": 2000.0,
                "max_speed": 2000.0,
                "projectile_gravity_scale": 0.0
            }}
        ]
    }
]

# 結果を格納する辞書
results = {}

def create_blueprint(info):
    # ブループリントを作成する
    bp_name = info["name"]
    bp_path = f"{base_path}/{bp_name}"
    parent_class = info["parent_class"]
    components = info.get("components", [])
    
    # ブループリントがすでに存在するか確認
    if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
        print(f"ブループリントはすでに存在します: {bp_path}")
        blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
    else:
        # ブループリントファクトリーを準備
        factory = unreal.BlueprintFactory()
        factory.parent_class = parent_class
        
        # アセットツールを取得
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # ブループリントを作成
        blueprint = asset_tools.create_asset(bp_name, base_path, unreal.Blueprint, factory)
        print(f"新しいブループリントを作成しました: {bp_path}")
    
    if blueprint:
        # コンポーネントを追加
        with unreal.ScopedEditorTransaction(f"Setup {bp_name}") as trans:
            for comp_info in components:
                comp_type = comp_info["type"]
                properties = comp_info.get("properties", {})
                
                # コンポーネントを追加
                component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, comp_type)
                
                # プロパティを設定
                for prop_name, prop_value in properties.items():
                    component.set_editor_property(prop_name, prop_value)
            
            # 保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
        
        return True
    
    return False

# ゲームモードブループリントを作成する関数
def create_game_mode_blueprint():
    # ゲームモードブループリントを作成する
    bp_name = "BP_ShooterGameMode"
    bp_path = f"{base_path}/{bp_name}"
    player_bp_path = f"{base_path}/BP_PlayerShip"
    
    # ブループリントがすでに存在するか確認
    if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
        print(f"ブループリントはすでに存在します: {bp_path}")
        blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
    else:
        # ブループリントファクトリーを準備
        factory = unreal.BlueprintFactory()
        factory.parent_class = unreal.GameModeBase
        
        # アセットツールを取得
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # ブループリントを作成
        blueprint = asset_tools.create_asset(bp_name, base_path, unreal.Blueprint, factory)
        print(f"新しいブループリントを作成しました: {bp_path}")
    
    if blueprint:
        # プレイヤーブループリントが存在するか確認
        if unreal.EditorAssetLibrary.does_asset_exist(player_bp_path):
            player_class = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
            
            # ゲームモード設定を更新
            with unreal.ScopedEditorTransaction(f"Setup {bp_name}") as trans:
                blueprint.set_editor_property("default_pawn_class", player_class)
                unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
            
            return True
    
    return False

# 各ブループリントを作成
for bp_info in blueprints_info:
    name = bp_info["name"]
    result = create_blueprint(bp_info)
    results[name] = result

# ゲームモードブループリントを作成
game_mode_result = create_game_mode_blueprint()
results["BP_ShooterGameMode"] = game_mode_result

# 結果の確認
print("=== ブループリント作成結果 ===")
all_ok = True
for name, success in results.items():
    print(f"{name}: {success}")
    if not success:
        all_ok = False

# コンテンツブラウザを更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
unreal.EditorAssetLibrary.refresh_asset_directories([base_path])

print(f"すべてのブループリントが正常に作成されました: {all_ok}")
return {{"success": all_ok, "results": results}}
"""
    
    # スクリプトを実行
    success, result = execute_unreal_python(script)
    return success

def main():
    """メイン処理"""
    logger.info("UE5エディタ内の基本ブループリント作成を開始します...")
    
    # UE5エディタとの接続を確認
    if not check_unreal_connection():
        logger.error("UE5エディタに接続できませんでした。UE5エディタが起動していて、MCPプラグインが有効になっていることを確認してください。")
        return False
    
    # ブループリントを作成
    if create_basic_blueprints():
        logger.info("ブループリントの作成に成功しました")
        
        # 少し待機してUE5エディタに反映されるのを待つ
        time.sleep(2)
        
        logger.info("UE5エディタでコンテンツブラウザを更新（F5キー）してください")
        logger.info("セットアップが完了しました")
        
        return True
    else:
        logger.error("ブループリントの作成に失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
