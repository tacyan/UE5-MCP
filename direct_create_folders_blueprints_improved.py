#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5エディタ内に基本的なフォルダ構造とブループリントを直接作成するスクリプト

このスクリプトは、UE5エディタ内に基本的なフォルダ構造とブループリントを一度に直接作成します。
直接Unrealエディタ内で実行するPythonコードを使用します。
実行前にSpaceShooterGameプロジェクトがDocumentsフォルダ内に存在し、UE5エディタが起動していることを確認してください。

使用方法:
  python direct_create_folders_blueprints.py
"""

import logging
import os
import sys
import requests
import json
import time
import subprocess
import platform
import shutil

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# UE5エディタのPythonスクリプトを実行するためのRESTエンドポイント
UNREAL_ENDPOINT = "http://localhost:8080/api/unreal/execute"
UNREAL_STATUS_ENDPOINT = "http://localhost:8080/api/status"

# ユーザーのホームディレクトリとプロジェクトパスを設定
HOME_DIR = os.path.expanduser("~")
DOCUMENTS_DIR = os.path.join(HOME_DIR, "Documents")
PROJECT_DIR = os.path.join(DOCUMENTS_DIR, "SpaceShooterGame")
PROJECT_FILE = os.path.join(PROJECT_DIR, "SpaceShooterGame.uproject")
CONTENT_DIR = os.path.join(PROJECT_DIR, "Content")
SHOOTER_GAME_DIR = os.path.join(CONTENT_DIR, "ShooterGame")

def create_directory_structure():
    """プロジェクトディレクトリにフォルダ構造を直接作成する"""
    logger.info("Contentディレクトリに直接ShooterGameフォルダ構造を作成します...")
    
    # ShooterGameディレクトリとサブディレクトリを作成
    if not os.path.exists(SHOOTER_GAME_DIR):
        os.makedirs(SHOOTER_GAME_DIR)
        logger.info(f"ディレクトリを作成しました: {SHOOTER_GAME_DIR}")
    else:
        logger.info(f"ディレクトリはすでに存在します: {SHOOTER_GAME_DIR}")
    
    # サブディレクトリの作成
    subdirs = ["Assets", "Blueprints", "Maps"]
    created_dirs = []
    
    for subdir in subdirs:
        subdir_path = os.path.join(SHOOTER_GAME_DIR, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
            logger.info(f"サブディレクトリを作成しました: {subdir_path}")
            created_dirs.append(subdir_path)
        else:
            logger.info(f"サブディレクトリはすでに存在します: {subdir_path}")
    
    return created_dirs

def ensure_ue5_running():
    """UE5エディタが実行中であることを確認し、必要に応じて起動する"""
    if check_unreal_connection():
        logger.info("UE5エディタは既に起動しています")
        return True
    
    # プロジェクトファイルの存在を確認
    if not os.path.exists(PROJECT_FILE):
        logger.error(f"プロジェクトファイルが見つかりません: {PROJECT_FILE}")
        return False
    
    # UE5エディタを起動
    try:
        logger.info(f"UE5エディタを起動しています: {PROJECT_FILE}")
        
        # OSに応じたコマンドを実行
        if platform.system() == "Windows":
            subprocess.Popen([PROJECT_FILE], shell=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", PROJECT_FILE])
        else:  # Linux
            logger.error("Linuxでの自動起動はサポートされていません。手動でUE5エディタを起動してください。")
            return False
        
        # エディタが起動するまで待機
        return wait_for_unreal_connection(max_attempts=60, wait_time=5)
    except Exception as e:
        logger.error(f"UE5エディタの起動に失敗しました: {str(e)}")
        return False

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

def wait_for_unreal_connection(max_attempts=30, wait_time=5):
    """UE5エディタとの接続を待機する"""
    logger.info(f"UE5エディタとの接続を待機しています... (最大{max_attempts}回試行、各{wait_time}秒間)")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(UNREAL_STATUS_ENDPOINT, timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                if status_data.get("unreal", {}).get("status") == "connected":
                    logger.info(f"UE5エディタに接続しました (試行回数: {attempt+1})")
                    return True
                else:
                    logger.warning(f"UE5エディタは接続中ですが、まだ準備ができていません: {status_data.get('unreal', {}).get('status')}")
            else:
                logger.warning(f"UE5エディタとの接続確認に失敗しました: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"UE5エディタとの接続を試行中...: {str(e)}")
        
        logger.info(f"再試行まで{wait_time}秒待機します... ({attempt+1}/{max_attempts})")
        time.sleep(wait_time)
    
    logger.error("UE5エディタとの接続がタイムアウトしました。UE5エディタが起動していて、MCPプラグインが有効になっていることを確認してください。")
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

def create_blueprints_and_level():
    """UE5エディタ内にブループリントとレベルを作成する"""
    logger.info("UE5エディタ内にブループリントとレベルを作成しています...")
    
    # スクリプト
    script = """
import unreal
import time

# ログ出力関数
def log_message(message):
    unreal.log(message)
    print(message)

log_message("ブループリントとレベルの作成を開始します...")

# 結果を格納する辞書
results = {
    "blueprints": {},
    "level": False
}

# 基本パス
base_path = "/Game/ShooterGame"
blueprints_path = f"{base_path}/Blueprints"
maps_path = f"{base_path}/Maps"
assets_path = f"{base_path}/Assets"

# パスがスラッシュで終わっていないことを確認（UE4/UE5のAPIでは最後のスラッシュがないほうが安全）
if base_path.endswith('/'):
    base_path = base_path[:-1]
if blueprints_path.endswith('/'):
    blueprints_path = blueprints_path[:-1]
if maps_path.endswith('/'):
    maps_path = maps_path[:-1]
if assets_path.endswith('/'):
    assets_path = assets_path[:-1]

# UE内でディレクトリを作成する関数
def ensure_directory_exists(path):
    log_message(f"ディレクトリ確認: {path}")
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        log_message(f"ディレクトリが見つかりません。作成します: {path}")
        parent_dir = "/".join(path.split("/")[:-1])
        # 親ディレクトリが存在することを確認
        if parent_dir and not unreal.EditorAssetLibrary.does_directory_exist(parent_dir):
            ensure_directory_exists(parent_dir)
        # ディレクトリを作成
        return unreal.EditorAssetLibrary.make_directory(path)
    else:
        log_message(f"ディレクトリは既に存在します: {path}")
        return True

# コンテンツブラウザを更新（ディレクトリを確認するため）
log_message("コンテンツブラウザを更新します...")
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])

# すべてのディレクトリを作成
log_message("必要なディレクトリをUE内に作成します...")
ensure_directory_exists(base_path)
ensure_directory_exists(blueprints_path)
ensure_directory_exists(maps_path)
ensure_directory_exists(assets_path)

# コンテンツブラウザを再度更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
unreal.EditorAssetLibrary.refresh_asset_directories([base_path])
unreal.EditorAssetLibrary.refresh_asset_directories([blueprints_path])
unreal.EditorAssetLibrary.refresh_asset_directories([maps_path])
unreal.EditorAssetLibrary.refresh_asset_directories([assets_path])

# キューブメッシュを取得
def get_cube_mesh():
    cube_mesh_path = "/Engine/BasicShapes/Cube"
    if unreal.EditorAssetLibrary.does_asset_exist(cube_mesh_path):
        return unreal.EditorAssetLibrary.load_asset(cube_mesh_path)
    else:
        log_message(f"キューブメッシュが見つかりません: {cube_mesh_path}")
        return None

# ブループリントを作成する関数
def create_blueprint(info, base_path):
    bp_name = info["name"]
    bp_path = f"{base_path}/{bp_name}"
    parent_class = info["parent_class"]
    components = info.get("components", [])
    
    log_message(f"ブループリント作成開始: {bp_path}")
    
    try:
        # ブループリントがすでに存在するか確認
        if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
            log_message(f"ブループリントはすでに存在します: {bp_path}")
            blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
        else:
            # ブループリントファクトリーを準備
            factory = unreal.BlueprintFactory()
            factory.parent_class = parent_class
            
            # アセットツールを取得
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            
            # ブループリントを作成
            blueprint = asset_tools.create_asset(bp_name, base_path, unreal.Blueprint, factory)
            if blueprint is None:
                log_message(f"ブループリント作成に失敗しました: {bp_path}")
                return False
                
            log_message(f"新しいブループリントを作成しました: {bp_path}")
        
        if blueprint:
            # コンポーネントを追加
            with unreal.ScopedEditorTransaction(f"Setup {bp_name}") as trans:
                for comp_info in components:
                    comp_type = comp_info["type"]
                    properties = comp_info.get("properties", {})
                    
                    # コンポーネントを追加
                    component = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, comp_type)
                    
                    # StaticMeshComponentの場合、キューブメッシュを設定
                    if comp_type == unreal.StaticMeshComponent:
                        cube_mesh = get_cube_mesh()
                        if cube_mesh:
                            component.set_editor_property("static_mesh", cube_mesh)
                    
                    # プロパティを設定
                    for prop_name, prop_value in properties.items():
                        component.set_editor_property(prop_name, prop_value)
            
            # 未保存の変更を保存
            log_message(f"ブループリントを保存します: {bp_path}")
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
            
            # パッケージを保存
            try:
                # パッケージ名を取得して強制保存
                package_path = blueprint.get_outer().get_path_name()
                package_name = blueprint.get_outer().get_name()
                log_message(f"パッケージを保存します: {package_path} (名前: {package_name})")
                
                # パッケージを保存
                unreal.EditorLoadingAndSavingUtils.save_packages([package_name], True)
                
                # パッケージ名でも試す（念のため両方試す）
                if hasattr(unreal, 'PackageTools'):
                    unreal.PackageTools.save_package(blueprint.get_outer())
                
                # すべてのダーティパッケージを保存
                unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
                
                # ログ出力
                log_message(f"ブループリント保存完了: {bp_path}")
            except Exception as save_error:
                log_message(f"パッケージ保存中にエラーが発生しました: {save_error}")
            
            return True
    except Exception as e:
        log_message(f"ブループリント作成中にエラーが発生しました: {e}")
    
    return False

# ゲームモードブループリントを作成する関数
def create_game_mode_blueprint(base_path):
    bp_name = "BP_ShooterGameMode"
    bp_path = f"{base_path}/{bp_name}"
    player_bp_path = f"{base_path}/BP_PlayerShip"
    
    log_message(f"ゲームモードブループリント作成開始: {bp_path}")
    
    try:
        # ブループリントがすでに存在するか確認
        if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
            log_message(f"ブループリントはすでに存在します: {bp_path}")
            blueprint = unreal.EditorAssetLibrary.load_asset(bp_path)
        else:
            # ブループリントファクトリーを準備
            factory = unreal.BlueprintFactory()
            factory.parent_class = unreal.GameModeBase
            
            # アセットツールを取得
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            
            # ブループリントを作成
            blueprint = asset_tools.create_asset(bp_name, base_path, unreal.Blueprint, factory)
            if blueprint is None:
                log_message(f"ゲームモードブループリント作成に失敗しました: {bp_path}")
                return False
                
            log_message(f"新しいゲームモードブループリントを作成しました: {bp_path}")
        
        if blueprint:
            # プレイヤーブループリントが存在するか確認
            if unreal.EditorAssetLibrary.does_asset_exist(player_bp_path):
                player_class = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
                
                # ゲームモード設定を更新
                with unreal.ScopedEditorTransaction(f"Setup {bp_name}") as trans:
                    blueprint.set_editor_property("default_pawn_class", player_class)
                
                # パッケージを保存
                log_message(f"ゲームモードブループリントを保存します: {bp_path}")
                unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
                
                # パッケージを保存
                try:
                    # パッケージ名を取得して強制保存
                    package_path = blueprint.get_outer().get_path_name()
                    package_name = blueprint.get_outer().get_name()
                    log_message(f"パッケージを保存します: {package_path} (名前: {package_name})")
                    
                    # パッケージを保存
                    unreal.EditorLoadingAndSavingUtils.save_packages([package_name], True)
                    
                    # パッケージ名でも試す
                    if hasattr(unreal, 'PackageTools'):
                        unreal.PackageTools.save_package(blueprint.get_outer())
                    
                    # すべてのダーティパッケージを保存
                    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
                    
                    # ログ出力
                    log_message(f"ゲームモードブループリント保存完了: {bp_path}")
                except Exception as save_error:
                    log_message(f"パッケージ保存中にエラーが発生しました: {save_error}")
                
                return True
    except Exception as e:
        log_message(f"ゲームモードブループリント作成中にエラーが発生しました: {e}")
    
    return False

# シンプルなレベルの作成関数
def create_simple_level(maps_path):
    level_name = "ShooterGameLevel"
    full_level_path = f"{maps_path}/{level_name}"
    player_bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"
    enemy_bp_path = "/Game/ShooterGame/Blueprints/BP_EnemyShip"
    game_mode_bp_path = "/Game/ShooterGame/Blueprints/BP_ShooterGameMode"
    
    log_message(f"レベル作成開始: {full_level_path}")
    
    try:
        # レベルサブシステムを取得
        level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        
        # 新しいレベルを作成
        current_level = level_subsystem.new_level(full_level_path)
        log_message(f"新しいレベルを作成しました: {full_level_path}")
        
        # レベルを保存
        level_subsystem.save_current_level()
        log_message("レベルを保存しました")
        
        # プレイヤーを配置
        if unreal.EditorAssetLibrary.does_asset_exist(player_bp_path):
            player_class = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
            player_location = unreal.Vector(0, 0, 100)
            player_rotation = unreal.Rotator(0, 0, 0)
            player_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(player_class, player_location, player_rotation)
            log_message(f"プレイヤーを配置しました: {player_bp_path}")
        else:
            log_message(f"プレイヤーブループリントが見つかりません: {player_bp_path}")
        
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
            log_message(f"敵を配置しました: {enemy_bp_path}")
        else:
            log_message(f"敵ブループリントが見つかりません: {enemy_bp_path}")
        
        # レベルを保存
        level_subsystem.save_current_level()
        log_message("レベルの変更を保存しました")
        
        # ゲームモードを設定
        if unreal.EditorAssetLibrary.does_asset_exist(game_mode_bp_path):
            game_mode_class = unreal.EditorAssetLibrary.load_blueprint_class(game_mode_bp_path)
            
            # レベルのゲームモードを設定
            with unreal.ScopedEditorTransaction("Set Level GameMode") as trans:
                world_settings = unreal.EditorLevelLibrary.get_game_mode_settings_for_current_level()
                if world_settings:
                    world_settings.set_editor_property("game_mode_override", game_mode_class)
                    log_message(f"ゲームモードを設定しました: {game_mode_bp_path}")
                else:
                    log_message("ワールド設定が見つかりません")
        else:
            log_message(f"ゲームモードブループリントが見つかりません: {game_mode_bp_path}")
        
        # 最終的なレベル保存
        level_subsystem.save_current_level()
        
        # すべてのダーティパッケージを保存
        log_message("すべてのダーティパッケージを保存します...")
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        
        log_message("最終レベル変更を保存しました")
        
        return True
    except Exception as e:
        log_message(f"レベル作成中にエラーが発生しました: {e}")
        return False

# ブループリント情報
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

# ----- 処理開始 -----

# 1. ブループリントの作成
log_message("1. ブループリントの作成を開始します...")

# プロジェクトフォルダをBlueprints内に作成
blueprint_dir = blueprints_path
log_message(f"ブループリント保存先: {blueprint_dir}")

# ディレクトリを確認・作成
ensure_directory_exists(blueprint_dir)

# 各ブループリントを作成
for bp_info in blueprints_info:
    name = bp_info["name"]
    result = create_blueprint(bp_info, blueprint_dir)
    results["blueprints"][name] = result
    # ブループリント間に少し間隔を空ける
    time.sleep(1)

# ゲームモードブループリントを作成
game_mode_result = create_game_mode_blueprint(blueprint_dir)
results["blueprints"]["BP_ShooterGameMode"] = game_mode_result

# すべてのダーティパッケージを保存
log_message("すべてのダーティパッケージを保存します...")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# 少し待機してブループリント作成が完了するのを待つ
log_message("ブループリント作成の完了を待機します...")
time.sleep(3)

# コンテンツブラウザを更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
unreal.EditorAssetLibrary.refresh_asset_directories([base_path])
unreal.EditorAssetLibrary.refresh_asset_directories([blueprint_dir])

# 2. レベルを作成
log_message("2. ゲームレベルの作成を開始します...")
log_message(f"レベル保存先: {maps_path}")
level_result = create_simple_level(maps_path)
results["level"] = level_result

# 少し待機してレベル作成が完了するのを待つ
log_message("レベル作成の完了を待機します...")
time.sleep(3)

# コンテンツブラウザを最終更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
unreal.EditorAssetLibrary.refresh_asset_directories([base_path])
unreal.EditorAssetLibrary.refresh_asset_directories([blueprints_path])
unreal.EditorAssetLibrary.refresh_asset_directories([maps_path])

# すべてのダーティパッケージを最終保存
log_message("すべてのダーティパッケージを最終保存します...")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# アセットレジストリを強制更新
if hasattr(unreal, 'AssetRegistryHelpers'):
    log_message("アセットレジストリを強制更新します...")
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry.search_all_assets(True)

# 現在のプロジェクトを保存
try:
    log_message("現在のプロジェクトを保存します...")
    if hasattr(unreal, 'EditorLoadingAndSavingUtils'):
        unreal.EditorLoadingAndSavingUtils.save_current_level()
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
except Exception as e:
    log_message(f"プロジェクト保存中にエラーが発生しました: {e}")

# 結果の確認
log_message("=== ブループリント作成結果 ===")
blueprints_ok = True
for name, success in results["blueprints"].items():
    log_message(f"{name}: {success}")
    if not success:
        blueprints_ok = False

log_message(f"レベル作成: {results['level']}")

# 最終結果の表示
all_ok = blueprints_ok and results["level"]
log_message(f"すべての要素が正常に作成されました: {all_ok}")

log_message("セットアップが完了しました！プロジェクトを閉じて再度開くと、新しいコンテンツが確実に表示されます。")
return {{"success": all_ok, "results": results}}
"""
    
    # スクリプトを実行
    success, result = execute_unreal_python(script)
    return success

def main():
    """メイン処理"""
    logger.info("UE5エディタ内のフォルダ構造とブループリントのセットアップを開始します...")
    
    # プロジェクトディレクトリが存在することを確認
    if not os.path.exists(PROJECT_DIR):
        logger.error(f"SpaceShooterGameプロジェクトが見つかりません: {PROJECT_DIR}")
        logger.info("プロジェクトが正しく作成されていることを確認してください。")
        return False
    
    # フォルダ構造をOSのファイルシステムに直接作成
    logger.info("ファイルシステムに直接フォルダ構造を作成します...")
    created_dirs = create_directory_structure()
    
    # UE5エディタが起動していることを確認、または起動
    if not ensure_ue5_running():
        logger.error("UE5エディタの起動と接続に失敗しました。セットアップを中止します。")
        return False
    
    # 追加の待機時間を設けて、エディタが完全に読み込まれるのを待つ
    logger.info("UE5エディタが完全に読み込まれるまで待機しています...")
    time.sleep(10)
    
    # Unrealエンジンでブループリントとレベルを作成
    if create_blueprints_and_level():
        logger.info("ブループリントとレベルの作成に成功しました")
        
        # 少し待機してUE5エディタに反映されるのを待つ
        time.sleep(3)
        
        logger.info("セットアップが完了しました")
        logger.info("UE5エディタでコンテンツブラウザを確認するか、F5キーを押して更新してください")
        logger.info("新しいコンテンツが表示されない場合は、プロジェクトを閉じて再度開いてください")
        
        # コンテンツブラウザを更新するため、自動でF5キーを送信する方法を試みる
        try:
            # PythonスクリプトでF5キーを送信
            refresh_script = """
import unreal
# コンテンツブラウザを更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game/ShooterGame"])
unreal.log("コンテンツブラウザを更新しました")
"""
            refresh_data = {
                "command": "execute_python",
                "params": {
                    "script": refresh_script
                }
            }
            requests.post(UNREAL_ENDPOINT, json=refresh_data)
            logger.info("コンテンツブラウザの更新を要求しました")
        except Exception as e:
            logger.warning(f"自動更新に失敗しました: {str(e)}。手動でF5キーを押してください。")
        
        return True
    else:
        logger.error("ブループリントとレベルの作成に失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
