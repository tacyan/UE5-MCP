#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲームのゲームプレイロジック設定スクリプト

このスクリプトは、UE5プロジェクト内にシューティングゲームのゲームプレイロジックを
設定します。MCPフレームワークを使用してUE5と連携し、ゲームの基本的な要素を
実装します。

使用方法:
  python setup_shooter_gameplay.py
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
        logging.FileHandler("setup_shooter_gameplay.log")
    ]
)
logger = logging.getLogger("setup_shooter_gameplay")

# 各種パス設定
UE5_ASSET_PATH = "/Game/ShooterGame/Assets"
UE5_BP_PATH = "/Game/ShooterGame/Blueprints"
UE5_MAPS_PATH = "/Game/ShooterGame/Maps"

def setup_player_blueprint():
    """プレイヤーキャラクターのブループリントを設定する"""
    logger.info("プレイヤーキャラクターのブループリントを設定しています...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # プレイヤーキャラクターBPのPythonスクリプト
    python_script = """
import unreal

# アセットパス
player_mesh_path = "{0}/PlayerShip"
blueprint_path = "{1}/BP_PlayerShip"

# プレイヤーキャラクターブループリントを作成
def create_player_blueprint():
    # ファクトリーを準備
    factory = unreal.BlueprintFactory()
    factory.parent_class = unreal.Pawn
    
    # アセットツールを取得
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # ブループリントを作成または開く
    blueprint = asset_tools.create_asset("BP_PlayerShip", "{1}", unreal.Blueprint, factory)
    
    # ブループリントを編集可能にする
    blueprint_obj = unreal.EditorAssetLibrary.load_blueprint_class(blueprint_path)
    
    # メッシュコンポーネントを追加
    with unreal.ScopedEditorTransaction("Setup Player Blueprint") as trans:
        # ブループリントを開く
        blueprint_editor = unreal.load_object(None, blueprint_path)
        
        # ルートコンポーネントがない場合は作成
        if not blueprint.get_editor_property("simple_construct_script"):
            # Static Meshコンポーネントを追加
            mesh_component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
            mesh_component.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            
            # メッシュアセットを設定
            static_mesh = unreal.EditorAssetLibrary.load_asset(player_mesh_path)
            if static_mesh:
                mesh_component.set_editor_property("static_mesh", static_mesh)
            
            # 移動コンポーネントを追加
            movement = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.FloatingPawnMovement)
            movement.set_editor_property("max_speed", 1000.0)
            
            # カメラコンポーネントを追加
            camera = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.CameraComponent)
            camera.set_editor_property("relative_location", unreal.Vector(0, 0, 100))
            camera.set_editor_property("relative_rotation", unreal.Rotator(-20, 0, 0))
            
            # 発射装置コンポーネントを追加
            spawn_point = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.SceneComponent)
            spawn_point.set_editor_property("component_name", "ProjectileSpawnPoint")
            spawn_point.set_editor_property("relative_location", unreal.Vector(100, 0, 0))
            
            # コンパイル・保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
    
    return "プレイヤーキャラクターブループリントの作成が完了しました"

# 実行
result = create_player_blueprint()
print(result)
""".format(UE5_ASSET_PATH, UE5_BP_PATH)
    
    params = {
        "script": python_script
    }
    
    result = client.execute_unreal_command("execute_python", params)
    
    if result.get("status") == "success":
        logger.info("プレイヤーキャラクターブループリントの設定に成功しました")
    else:
        logger.error(f"プレイヤーキャラクターブループリントの設定に失敗しました: {result}")
    
    return result.get("status") == "success"

def setup_enemy_blueprint():
    """敵キャラクターのブループリントを設定する"""
    logger.info("敵キャラクターのブループリントを設定しています...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # 敵キャラクターBPのPythonスクリプト
    python_script = """
import unreal

# アセットパス
enemy_mesh_path = "{0}/EnemyShip"
blueprint_path = "{1}/BP_EnemyShip"

# 敵キャラクターブループリントを作成
def create_enemy_blueprint():
    # ファクトリーを準備
    factory = unreal.BlueprintFactory()
    factory.parent_class = unreal.Pawn
    
    # アセットツールを取得
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # ブループリントを作成または開く
    blueprint = asset_tools.create_asset("BP_EnemyShip", "{1}", unreal.Blueprint, factory)
    
    # ブループリントを編集可能にする
    blueprint_obj = unreal.EditorAssetLibrary.load_blueprint_class(blueprint_path)
    
    # コンポーネントを追加
    with unreal.ScopedEditorTransaction("Setup Enemy Blueprint") as trans:
        # ブループリントを開く
        blueprint_editor = unreal.load_object(None, blueprint_path)
        
        # ルートコンポーネントがない場合は作成
        if not blueprint.get_editor_property("simple_construct_script"):
            # Static Meshコンポーネントを追加
            mesh_component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
            mesh_component.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            
            # メッシュアセットを設定
            static_mesh = unreal.EditorAssetLibrary.load_asset(enemy_mesh_path)
            if static_mesh:
                mesh_component.set_editor_property("static_mesh", static_mesh)
            
            # 移動コンポーネントを追加
            movement = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.FloatingPawnMovement)
            movement.set_editor_property("max_speed", 500.0)
            
            # 発射装置コンポーネントを追加
            spawn_point = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.SceneComponent)
            spawn_point.set_editor_property("component_name", "ProjectileSpawnPoint")
            spawn_point.set_editor_property("relative_location", unreal.Vector(100, 0, 0))
            
            # コンパイル・保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
    
    return "敵キャラクターブループリントの作成が完了しました"

# 実行
result = create_enemy_blueprint()
print(result)
""".format(UE5_ASSET_PATH, UE5_BP_PATH)
    
    params = {
        "script": python_script
    }
    
    result = client.execute_unreal_command("execute_python", params)
    
    if result.get("status") == "success":
        logger.info("敵キャラクターブループリントの設定に成功しました")
    else:
        logger.error(f"敵キャラクターブループリントの設定に失敗しました: {result}")
    
    return result.get("status") == "success"

def setup_projectile_blueprint():
    """弾丸のブループリントを設定する"""
    logger.info("弾丸のブループリントを設定しています...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # 弾丸BPのPythonスクリプト
    python_script = """
import unreal

# アセットパス
projectile_mesh_path = "{0}/Projectile"
blueprint_path = "{1}/BP_Projectile"

# 弾丸ブループリントを作成
def create_projectile_blueprint():
    # ファクトリーを準備
    factory = unreal.BlueprintFactory()
    factory.parent_class = unreal.Actor
    
    # アセットツールを取得
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # ブループリントを作成または開く
    blueprint = asset_tools.create_asset("BP_Projectile", "{1}", unreal.Blueprint, factory)
    
    # ブループリントを編集可能にする
    blueprint_obj = unreal.EditorAssetLibrary.load_blueprint_class(blueprint_path)
    
    # コンポーネントを追加
    with unreal.ScopedEditorTransaction("Setup Projectile Blueprint") as trans:
        # ブループリントを開く
        blueprint_editor = unreal.load_object(None, blueprint_path)
        
        # ルートコンポーネントがない場合は作成
        if not blueprint.get_editor_property("simple_construct_script"):
            # Static Meshコンポーネントを追加
            mesh_component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
            mesh_component.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            
            # メッシュアセットを設定
            static_mesh = unreal.EditorAssetLibrary.load_asset(projectile_mesh_path)
            if static_mesh:
                mesh_component.set_editor_property("static_mesh", static_mesh)
            
            # 球体コリジョンを追加
            collision = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.SphereComponent)
            collision.set_editor_property("sphere_radius", 30.0)
            collision.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_ONLY)
            
            # 移動コンポーネントを追加
            movement = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.ProjectileMovementComponent)
            movement.set_editor_property("initial_speed", 2000.0)
            movement.set_editor_property("max_speed", 2000.0)
            movement.set_editor_property("projectile_gravity_scale", 0.0)
            
            # コンパイル・保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
    
    return "弾丸ブループリントの作成が完了しました"

# 実行
result = create_projectile_blueprint()
print(result)
""".format(UE5_ASSET_PATH, UE5_BP_PATH)
    
    params = {
        "script": python_script
    }
    
    result = client.execute_unreal_command("execute_python", params)
    
    if result.get("status") == "success":
        logger.info("弾丸ブループリントの設定に成功しました")
    else:
        logger.error(f"弾丸ブループリントの設定に失敗しました: {result}")
    
    return result.get("status") == "success"

def setup_game_mode():
    """ゲームモードのブループリントを設定する"""
    logger.info("ゲームモードのブループリントを設定しています...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # ゲームモードBPのPythonスクリプト
    python_script = """
import unreal

# アセットパス
blueprint_path = "{0}/BP_ShooterGameMode"
player_bp_path = "{0}/BP_PlayerShip"

# ゲームモードブループリントを作成
def create_game_mode_blueprint():
    # ファクトリーを準備
    factory = unreal.BlueprintFactory()
    factory.parent_class = unreal.GameModeBase
    
    # アセットツールを取得
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # ブループリントを作成または開く
    blueprint = asset_tools.create_asset("BP_ShooterGameMode", "{0}", unreal.Blueprint, factory)
    
    # ブループリントを編集可能にする
    blueprint_obj = unreal.EditorAssetLibrary.load_blueprint_class(blueprint_path)
    
    # デフォルトポーンクラスを設定
    if unreal.EditorAssetLibrary.does_asset_exist(player_bp_path):
        player_class = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
        
        # GameMode設定を更新
        with unreal.ScopedEditorTransaction("Setup GameMode Blueprint") as trans:
            # デフォルトポーンクラスを設定
            blueprint.set_editor_property("default_pawn_class", player_class)
            
            # コンパイル・保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
    
    # プロジェクト設定を更新してデフォルトゲームモードに設定
    try:
        project_settings = unreal.get_default_object(unreal.ProjectPakSettings)
        game_mode_class = unreal.EditorAssetLibrary.load_blueprint_class(blueprint_path)
        
        # プロジェクトのデフォルトゲームモードを設定
        with unreal.ScopedEditorTransaction("Set Default GameMode") as trans:
            world_settings = unreal.EditorLevelLibrary.get_game_mode_settings_for_current_level()
            if world_settings:
                world_settings.set_editor_property("game_mode_override", game_mode_class)
    except:
        print("プロジェクト設定の更新中にエラーが発生しました。手動で設定してください。")
    
    return "ゲームモードブループリントの作成が完了しました"

# 実行
result = create_game_mode_blueprint()
print(result)
""".format(UE5_BP_PATH)
    
    params = {
        "script": python_script
    }
    
    result = client.execute_unreal_command("execute_python", params)
    
    if result.get("status") == "success":
        logger.info("ゲームモードブループリントの設定に成功しました")
    else:
        logger.error(f"ゲームモードブループリントの設定に失敗しました: {result}")
    
    return result.get("status") == "success"

def create_level():
    """ゲームレベルを作成する"""
    logger.info("ゲームレベルを作成しています...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # ディレクトリの確認と作成
    check_maps_script = """
import unreal

maps_path = "/Game/ShooterGame/Maps"
level_name = "ShooterGameLevel"
full_level_path = f"{maps_path}/{level_name}"

# Mapsディレクトリの確認と作成
if not unreal.EditorAssetLibrary.does_directory_exist(maps_path):
    print(f"Mapsディレクトリが存在しません。作成します: {maps_path}")
    unreal.EditorAssetLibrary.make_directory(maps_path)
    maps_created = unreal.EditorAssetLibrary.does_directory_exist(maps_path)
    print(f"Mapsディレクトリの作成結果: {maps_created}")
else:
    print(f"Mapsディレクトリは既に存在します: {maps_path}")
    
# レベルが既に存在するか確認
level_exists = unreal.EditorAssetLibrary.does_asset_exist(full_level_path)
print(f"レベルの存在確認: {level_exists} - {full_level_path}")

print("ディレクトリ確認完了")
"""
    
    maps_check_result = client.execute_unreal_command("execute_python", {"script": check_maps_script})
    logger.info(f"マップフォルダの確認結果: {maps_check_result}")
    
    # レベル作成のPythonスクリプト
    level_script = """
import unreal

# アセットパス
maps_path = "/Game/ShooterGame/Maps"
level_name = "ShooterGameLevel"
full_level_path = f"{maps_path}/{level_name}"
player_bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"
enemy_bp_path = "/Game/ShooterGame/Blueprints/BP_EnemyShip"
game_mode_bp_path = "/Game/ShooterGame/Blueprints/BP_ShooterGameMode"

# ゲームレベルを作成
def create_game_level():
    # 新しいレベルを作成
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    try:
        # 既存のレベルを閉じる
        level_subsystem.new_level(full_level_path)
        print(f"新しいレベルを作成しました: {full_level_path}")
    except Exception as e:
        print(f"レベル作成中にエラーが発生しました: {e}")
        # 既存のレベルを開いてみる
        try:
            if unreal.EditorAssetLibrary.does_asset_exist(full_level_path):
                level_subsystem.load_level(full_level_path)
                print(f"既存のレベルを開きました: {full_level_path}")
            else:
                print(f"レベルが存在せず、作成もできませんでした: {full_level_path}")
                return "レベル作成に失敗しました"
        except Exception as e2:
            print(f"既存レベルを開く際にエラーが発生しました: {e2}")
            return "レベル作成に失敗しました"
    
    # レベルを保存
    try:
        level_subsystem.save_current_level()
        print("レベルを保存しました")
    except Exception as e:
        print(f"レベル保存中にエラーが発生しました: {e}")
    
    # プレイヤーを配置
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(player_bp_path):
            player_class = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
            player_location = unreal.Vector(0, 0, 100)
            player_rotation = unreal.Rotator(0, 0, 0)
            player_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(player_class, player_location, player_rotation)
            print(f"プレイヤーを配置しました: {player_bp_path}")
        else:
            print(f"プレイヤーブループリントが見つかりません: {player_bp_path}")
    except Exception as e:
        print(f"プレイヤー配置中にエラーが発生しました: {e}")
    
    # 敵を配置
    try:
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
    except Exception as e:
        print(f"敵配置中にエラーが発生しました: {e}")
    
    # レベルを保存
    try:
        level_subsystem.save_current_level()
        print("レベルの変更を保存しました")
    except Exception as e:
        print(f"変更保存中にエラーが発生しました: {e}")
    
    # ゲームモードを設定
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(game_mode_bp_path):
            game_mode_class = unreal.EditorAssetLibrary.load_blueprint_class(game_mode_bp_path)
            
            # レベルのゲームモードを設定
            with unreal.ScopedEditorTransaction("Set Level GameMode") as trans:
                world_settings = unreal.EditorLevelLibrary.get_game_mode_settings_for_current_level()
                if world_settings:
                    world_settings.set_editor_property("game_mode_override", game_mode_class)
            print(f"ゲームモードを設定しました: {game_mode_bp_path}")
        else:
            print(f"ゲームモードブループリントが見つかりません: {game_mode_bp_path}")
    except Exception as e:
        print(f"ゲームモード設定中にエラーが発生しました: {e}")
    
    # 最終的なレベル保存
    try:
        level_subsystem.save_current_level()
        print("最終レベル変更を保存しました")
    except Exception as e:
        print(f"最終保存中にエラーが発生しました: {e}")
    
    return "ゲームレベルの作成が完了しました"

# 実行
try:
    result = create_game_level()
    print(result)
except Exception as e:
    print(f"レベル作成関数実行中に例外が発生しました: {e}")
    print("レベル作成に失敗しました")
"""

    level_result = client.execute_unreal_command("execute_python", {"script": level_script})
    
    if level_result.get("status") == "success":
        logger.info("ゲームレベルの作成に成功しました")
        # レベルが正常に開かれたか確認
        check_level_script = """
import unreal
level_path = "/Game/ShooterGame/Maps/ShooterGameLevel"
is_open = unreal.EditorAssetLibrary.does_asset_exist(level_path)
print(f"レベル確認: {level_path} - 存在する: {is_open}")

# デフォルトマップとして設定
if is_open:
    try:
        project_settings = unreal.get_default_object(unreal.ProjectPackagingSettings)
        project_settings.set_editor_property("map_to_cook", [level_path])
        unreal.EditorAssetLibrary.save_loaded_asset(project_settings)
        print("デフォルトマップとして設定しました")
    except Exception as e:
        print(f"デフォルトマップ設定中にエラー: {e}")
"""
        level_check_result = client.execute_unreal_command("execute_python", {"script": check_level_script})
        logger.info(f"レベル確認結果: {level_check_result}")
    else:
        logger.error(f"ゲームレベルの作成に失敗しました: {level_result}")
    
    return level_result.get("status") == "success"

def setup_player_input():
    """プレイヤー入力設定を行う"""
    logger.info("プレイヤー入力設定を行っています...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # 入力設定のPythonスクリプト
    python_script = """
import unreal

# 入力設定を作成
def setup_input_settings():
    # プロジェクト設定を取得
    editor_settings = unreal.get_editor_subsystem(unreal.EditorSubsystem)
    
    # 新しい入力アクションを作成
    input_settings = unreal.InputSettings.get_default_object()
    
    # 入力アクションに「Fire」を追加
    with unreal.ScopedEditorTransaction("Add Input Bindings") as trans:
        # 既存のアクションマッピングをクリア
        input_settings.action_mappings = []
        
        # 新しいアクションマッピングを追加
        fire_action = unreal.InputActionKeyMapping("Fire", unreal.InputChord(unreal.Key.SPACE_BAR))
        input_settings.add_action_mapping(fire_action)
        
        # 軸マッピングを設定
        input_settings.axis_mappings = []
        
        # 前後移動
        move_forward = unreal.InputAxisKeyMapping("MoveForward", unreal.Key.W, 1.0)
        move_backward = unreal.InputAxisKeyMapping("MoveForward", unreal.Key.S, -1.0)
        input_settings.add_axis_mapping(move_forward)
        input_settings.add_axis_mapping(move_backward)
        
        # 左右移動
        move_right = unreal.InputAxisKeyMapping("MoveRight", unreal.Key.D, 1.0)
        move_left = unreal.InputAxisKeyMapping("MoveRight", unreal.Key.A, -1.0)
        input_settings.add_axis_mapping(move_right)
        input_settings.add_axis_mapping(move_left)
    
    return "入力設定が完了しました"

# 実行
result = setup_input_settings()
print(result)
"""
    
    params = {
        "script": python_script
    }
    
    result = client.execute_unreal_command("execute_python", params)
    
    if result.get("status") == "success":
        logger.info("プレイヤー入力設定に成功しました")
    else:
        logger.error(f"プレイヤー入力設定に失敗しました: {result}")
    
    return result.get("status") == "success"

def main():
    """メイン実行関数"""
    logger.info("===== シューティングゲームのゲームプレイロジック設定を開始します =====")
    
    # ディレクトリ作成を確実に行う
    client = UE5MCPClient(host="127.0.0.1", port=8080)

    # より直接的なディレクトリ作成スクリプト
    create_dirs_script = """
import unreal
import os

# すべてのディレクトリ作成を確実に行うスクリプト
def ensure_directories():
    # ベースパス
    shooter_game_path = "/Game/ShooterGame"
    # サブディレクトリ
    subdirs = ["Assets", "Blueprints", "Maps"]
    
    try:
        # ShooterGameディレクトリの確認と作成
        if not unreal.EditorAssetLibrary.does_directory_exist(shooter_game_path):
            print(f"ShooterGameディレクトリを作成します: {shooter_game_path}")
            success = unreal.EditorAssetLibrary.make_directory(shooter_game_path)
            print(f"ShooterGameディレクトリ作成結果: {success}")
        else:
            print(f"ShooterGameディレクトリは既に存在します: {shooter_game_path}")
        
        # 各サブディレクトリを個別に作成（トランザクションを個別に実行）
        for subdir in subdirs:
            full_path = f"{shooter_game_path}/{subdir}"
            
            if not unreal.EditorAssetLibrary.does_directory_exist(full_path):
                print(f"{subdir}ディレクトリを作成します: {full_path}")
                with unreal.ScopedEditorTransaction(f"Create {subdir} Directory") as trans:
                    success = unreal.EditorAssetLibrary.make_directory(full_path)
                    # キャッシュを更新
                    unreal.EditorAssetLibrary.refresh_asset_directories([shooter_game_path])
                print(f"{subdir}ディレクトリ作成結果: {success}")
            else:
                print(f"{subdir}ディレクトリは既に存在します: {full_path}")
        
        # 作成されたかどうかを確認
        all_ok = True
        for subdir in subdirs:
            full_path = f"{shooter_game_path}/{subdir}"
            exists = unreal.EditorAssetLibrary.does_directory_exist(full_path)
            print(f"ディレクトリ確認: {full_path} - 存在する: {exists}")
            if not exists:
                all_ok = False
                
        # 最終確認
        print(f"すべてのディレクトリが存在するか: {all_ok}")
        
        # コンテンツブラウザを更新
        unreal.EditorAssetLibrary.refresh_asset_directories([shooter_game_path])
        
        return all_ok
    except Exception as e:
        print(f"ディレクトリ作成中にエラーが発生しました: {e}")
        return False

# 直接実行
success = ensure_directories()
print(f"ディレクトリ作成処理の結果: {success}")
"""

    # ディレクトリ作成コマンドの実行
    dir_result = client.execute_unreal_command("execute_python", {"script": create_dirs_script})
    logger.info(f"ディレクトリ作成結果: {dir_result}")

    # ディレクトリが正しく作成されるのを待つ（0.5秒）
    time.sleep(0.5)
    
    # 再度確認
    verify_script = """
import unreal
paths = ["/Game/ShooterGame/Assets", "/Game/ShooterGame/Blueprints", "/Game/ShooterGame/Maps"]
exists = {}
for path in paths:
    exists[path] = unreal.EditorAssetLibrary.does_directory_exist(path)
    print(f"パス確認: {path} - 存在する: {exists[path]}")

all_ok = all(exists.values())
print(f"すべてのディレクトリが存在するか: {all_ok}")

# 必要に応じて再作成
if not all_ok:
    print("不足しているディレクトリを再作成します")
    for path, exists_flag in exists.items():
        if not exists_flag:
            print(f"ディレクトリを作成します: {path}")
            success = unreal.EditorAssetLibrary.make_directory(path)
            print(f"ディレクトリ作成結果: {success}")
    
    # コンテンツブラウザを更新
    unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
    unreal.EditorAssetLibrary.refresh_asset_directories(["/Game/ShooterGame"])
"""
    
    verify_result = client.execute_unreal_command("execute_python", {"script": verify_script})
    logger.info(f"ディレクトリ検証結果: {verify_result}")
    
    # 処理の続き
    # ブループリントの設定
    success = True
    
    if not setup_player_blueprint():
        success = False
    
    if not setup_enemy_blueprint():
        success = False
    
    if not setup_projectile_blueprint():
        success = False
    
    if not setup_game_mode():
        success = False
    
    if not setup_player_input():
        success = False
    
    # ゲームレベルの作成
    if not create_level():
        success = False
    
    if success:
        logger.info("シューティングゲームのゲームプレイロジック設定が完了しました")
        logger.info("UE5エディタでゲームを実行してください")
    else:
        logger.error("ゲームプレイロジック設定中にエラーが発生しました")
    
    logger.info("===== ゲームプレイロジック設定が完了しました =====")

if __name__ == "__main__":
    main() 
