#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5エディタ内の基本的なブループリントを作成するスクリプト

このスクリプトは、UE5エディタ内にシューティングゲームの基本的なブループリントを
作成します。MCPフレームワークを使用して、各種ブループリントを設定します。

使用方法:
  python create_basic_blueprints.py
"""

import logging
from ue5_mcp_client import UE5MCPClient

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("create_basic_blueprints")

def create_player_blueprint():
    """プレイヤーのブループリントを作成する"""
    logger.info("プレイヤーのブループリントを作成します...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    script = """
import unreal

# ブループリントを作成
bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"
bp_name = "BP_PlayerShip"
bp_location = "/Game/ShooterGame/Blueprints"

# ファクトリーを準備
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.Pawn

# アセットツールを取得
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# ブループリントが存在するか確認
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    print(f"ブループリントはすでに存在します: {bp_path}")
    blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
else:
    # 新規作成
    blueprint = asset_tools.create_asset(bp_name, bp_location, unreal.Blueprint, factory)
    print(f"新しいブループリントを作成しました: {bp_path}")

# コンポーネントを追加
with unreal.ScopedEditorTransaction("Setup Player Blueprint") as trans:
    # Static Meshコンポーネントを追加
    mesh_component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
    mesh_component.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    
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

print(f"プレイヤーブループリントの設定が完了しました: {bp_path}")
"""
    
    result = client.execute_unreal_command("execute_python", {"script": script})
    
    if result.get("status") == "success":
        logger.info("プレイヤーブループリントの作成に成功しました")
    else:
        logger.error(f"プレイヤーブループリントの作成に失敗しました: {result}")
    
    return result

def create_enemy_blueprint():
    """敵のブループリントを作成する"""
    logger.info("敵のブループリントを作成します...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    script = """
import unreal

# ブループリントを作成
bp_path = "/Game/ShooterGame/Blueprints/BP_EnemyShip"
bp_name = "BP_EnemyShip"
bp_location = "/Game/ShooterGame/Blueprints"

# ファクトリーを準備
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.Pawn

# アセットツールを取得
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# ブループリントが存在するか確認
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    print(f"ブループリントはすでに存在します: {bp_path}")
    blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
else:
    # 新規作成
    blueprint = asset_tools.create_asset(bp_name, bp_location, unreal.Blueprint, factory)
    print(f"新しいブループリントを作成しました: {bp_path}")

# コンポーネントを追加
with unreal.ScopedEditorTransaction("Setup Enemy Blueprint") as trans:
    # Static Meshコンポーネントを追加
    mesh_component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
    mesh_component.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    
    # 移動コンポーネントを追加
    movement = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.FloatingPawnMovement)
    movement.set_editor_property("max_speed", 500.0)
    
    # 発射装置コンポーネントを追加
    spawn_point = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.SceneComponent)
    spawn_point.set_editor_property("component_name", "ProjectileSpawnPoint")
    spawn_point.set_editor_property("relative_location", unreal.Vector(100, 0, 0))
    
    # コンパイル・保存
    unreal.EditorAssetLibrary.save_loaded_asset(blueprint)

print(f"敵ブループリントの設定が完了しました: {bp_path}")
"""
    
    result = client.execute_unreal_command("execute_python", {"script": script})
    
    if result.get("status") == "success":
        logger.info("敵ブループリントの作成に成功しました")
    else:
        logger.error(f"敵ブループリントの作成に失敗しました: {result}")
    
    return result

def create_projectile_blueprint():
    """弾丸のブループリントを作成する"""
    logger.info("弾丸のブループリントを作成します...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    script = """
import unreal

# ブループリントを作成
bp_path = "/Game/ShooterGame/Blueprints/BP_Projectile"
bp_name = "BP_Projectile"
bp_location = "/Game/ShooterGame/Blueprints"

# ファクトリーを準備
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.Actor

# アセットツールを取得
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# ブループリントが存在するか確認
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    print(f"ブループリントはすでに存在します: {bp_path}")
    blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
else:
    # 新規作成
    blueprint = asset_tools.create_asset(bp_name, bp_location, unreal.Blueprint, factory)
    print(f"新しいブループリントを作成しました: {bp_path}")

# コンポーネントを追加
with unreal.ScopedEditorTransaction("Setup Projectile Blueprint") as trans:
    # Static Meshコンポーネントを追加
    mesh_component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
    mesh_component.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    
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

print(f"弾丸ブループリントの設定が完了しました: {bp_path}")
"""
    
    result = client.execute_unreal_command("execute_python", {"script": script})
    
    if result.get("status") == "success":
        logger.info("弾丸ブループリントの作成に成功しました")
    else:
        logger.error(f"弾丸ブループリントの作成に失敗しました: {result}")
    
    return result

def create_game_mode_blueprint():
    """ゲームモードのブループリントを作成する"""
    logger.info("ゲームモードのブループリントを作成します...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    script = """
import unreal

# ブループリントを作成
bp_path = "/Game/ShooterGame/Blueprints/BP_ShooterGameMode"
bp_name = "BP_ShooterGameMode"
bp_location = "/Game/ShooterGame/Blueprints"
player_bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"

# ファクトリーを準備
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.GameModeBase

# アセットツールを取得
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# ブループリントが存在するか確認
if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
    print(f"ブループリントはすでに存在します: {bp_path}")
    blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
else:
    # 新規作成
    blueprint = asset_tools.create_asset(bp_name, bp_location, unreal.Blueprint, factory)
    print(f"新しいブループリントを作成しました: {bp_path}")

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
    with unreal.ScopedEditorTransaction("Set Default GameMode") as trans:
        world_settings = unreal.EditorLevelLibrary.get_game_mode_settings_for_current_level()
        if world_settings:
            game_mode_class = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
            world_settings.set_editor_property("game_mode_override", game_mode_class)
except:
    print("プロジェクト設定の更新中にエラーが発生しました。手動で設定してください。")

print(f"ゲームモードブループリントの設定が完了しました: {bp_path}")
"""
    
    result = client.execute_unreal_command("execute_python", {"script": script})
    
    if result.get("status") == "success":
        logger.info("ゲームモードブループリントの作成に成功しました")
    else:
        logger.error(f"ゲームモードブループリントの作成に失敗しました: {result}")
    
    return result

def create_game_level():
    """ゲームレベルを作成する"""
    logger.info("ゲームレベルを作成します...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    script = """
import unreal

# レベル情報
maps_path = "/Game/ShooterGame/Maps"
level_name = "ShooterGameLevel"
full_level_path = f"{maps_path}/{level_name}"
player_bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"
enemy_bp_path = "/Game/ShooterGame/Blueprints/BP_EnemyShip"
game_mode_bp_path = "/Game/ShooterGame/Blueprints/BP_ShooterGameMode"

# レベルサブシステムを取得
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
            exit(1)
    except Exception as e2:
        print(f"既存レベルを開く際にエラーが発生しました: {e2}")
        exit(1)

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

print("ゲームレベルの作成が完了しました")
"""
    
    result = client.execute_unreal_command("execute_python", {"script": script})
    
    if result.get("status") == "success":
        logger.info("ゲームレベルの作成に成功しました")
    else:
        logger.error(f"ゲームレベルの作成に失敗しました: {result}")
    
    return result

def main():
    """メイン実行関数"""
    logger.info("===== 基本的なブループリントの作成を開始します =====")
    
    # ブループリントの作成
    create_player_blueprint()
    create_enemy_blueprint()
    create_projectile_blueprint()
    create_game_mode_blueprint()
    
    # ゲームレベルの作成
    create_game_level()
    
    logger.info("===== 基本的なブループリントの作成が完了しました =====")

if __name__ == "__main__":
    main() 
