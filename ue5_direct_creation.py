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
import os

# ログ出力関数
def log_message(message):
    unreal.log(message)
    print(message)

log_message("シンプルなテストアセット作成を開始します...")

# テストブループリントの作成と保存
try:
    # ディレクトリの作成
    base_path = "/Game/ShooterGameTest"
    log_message(f"ディレクトリを作成します: {base_path}")
    
    if not unreal.EditorAssetLibrary.does_directory_exist(base_path):
        unreal.EditorAssetLibrary.make_directory(base_path)
        log_message(f"ディレクトリを作成しました: {base_path}")
    else:
        log_message(f"ディレクトリはすでに存在します: {base_path}")
    
    # ブループリント作成
    bp_name = "BP_TestActor"
    bp_path = f"{base_path}/{bp_name}"
    
    # 既存のブループリントがあれば削除
    if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
        log_message(f"既存のブループリントを削除します: {bp_path}")
        unreal.EditorAssetLibrary.delete_asset(bp_path)
    
    # ブループリントファクトリーを準備
    factory = unreal.BlueprintFactory()
    factory.parent_class = unreal.Actor
    
    # アセットツールを取得
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # ブループリントを作成
    log_message(f"ブループリントを作成します: {bp_path}")
    blueprint = asset_tools.create_asset(bp_name, base_path, unreal.Blueprint, factory)
    
    if blueprint:
        log_message(f"ブループリントの作成に成功しました: {bp_path}")
        
        # コンポーネントを追加
        with unreal.ScopedEditorTransaction("Add Components") as trans:
            # StaticMeshコンポーネントを追加
            mesh_comp = unreal.EditorUtilityLibrary.add_component_to_blueprint(blueprint, unreal.StaticMeshComponent)
            
            # キューブメッシュを取得してセット
            cube_mesh_path = "/Engine/BasicShapes/Cube"
            if unreal.EditorAssetLibrary.does_asset_exist(cube_mesh_path):
                cube_mesh = unreal.EditorAssetLibrary.load_asset(cube_mesh_path)
                mesh_comp.set_editor_property("static_mesh", cube_mesh)
                log_message("キューブメッシュをセットしました")
        
        # ブループリントを保存 - 様々な方法を試す
        log_message(f"ブループリントを保存します: {bp_path}")
        
        # 方法1: EditorAssetLibraryを使う
        unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
        log_message("方法1: EditorAssetLibraryによる保存完了")
        
        # 方法2: EditorLoadingAndSavingUtilsを使う
        package_name = blueprint.get_outer().get_name()
        unreal.EditorLoadingAndSavingUtils.save_packages([package_name], True)
        log_message(f"方法2: EditorLoadingAndSavingUtilsによる保存完了 - パッケージ名: {package_name}")
        
        # 方法3: すべてのダーティパッケージを保存
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log_message("方法3: すべてのダーティパッケージを保存完了")
        
        # 方法4: アセットレジストリを更新
        if hasattr(unreal, 'AssetRegistryHelpers'):
            asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            asset_registry.search_all_assets(True)
            log_message("方法4: アセットレジストリを更新完了")
        
        # 方法5: プロジェクトの保存を強制する
        try:
            # 現在のレベルを保存
            level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            level_subsystem.save_current_level()
            log_message("方法5: 現在のレベルを保存しました")
            
            # プロジェクトを保存
            unreal.EditorLoadingAndSavingUtils.save_current_level()
            log_message("方法5: プロジェクトを保存しました")
            
            # 明示的にパッケージを作成して保存する試み
            package_path = blueprint.get_path_name().split('.')[0]
            log_message(f"ブループリントのパッケージパス: {package_path}")
            
            # PackageToolsを使用する試み
            if hasattr(unreal, 'PackageTools'):
                unreal.PackageTools.save_package(blueprint.get_outer())
                log_message("方法5: PackageToolsを使用してパッケージを保存しました")
        except Exception as e:
            log_message(f"方法5でエラーが発生しました: {e}")
        
        # ファイルシステムに明示的に保存を試みる
        try:
            # 方法6: AssetToolsを使用して明示的に保存
            asset_tools.save_asset(bp_path)
            log_message("方法6: AssetToolsを使って保存しました")
        except Exception as e:
            log_message(f"方法6でエラーが発生しました: {e}")
        
        # 遅延させて保存が完了するのを待つ
        log_message("保存処理の完了を待機しています...")
        time.sleep(3)
        
        # 最終確認
        if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
            log_message(f"最終確認: ブループリントが存在します: {bp_path}")
            
            # 方法7: コンテンツブラウザを更新して保存を促進
            unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
            unreal.EditorAssetLibrary.refresh_asset_directories([base_path])
            log_message("方法7: コンテンツブラウザを更新しました")
            
            # 再度確認
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
            log_message("方法7: 最終的な保存を実行しました")
            
            # 方法8: プロジェクトのコンテンツディレクトリを確認
            try:
                # プロジェクトパスを取得
                project_dir = unreal.Paths.project_dir()
                content_dir = os.path.join(project_dir, "Content")
                test_dir = os.path.join(content_dir, "ShooterGameTest")
                
                log_message(f"プロジェクトディレクトリ: {project_dir}")
                log_message(f"コンテンツディレクトリ: {content_dir}")
                log_message(f"テストディレクトリパス: {test_dir}")
                
                # ディレクトリが存在するか確認
                if os.path.exists(test_dir):
                    log_message(f"テストディレクトリが存在します: {test_dir}")
                    
                    # .uassetファイルを探す
                    uasset_path = os.path.join(test_dir, f"{bp_name}.uasset")
                    if os.path.exists(uasset_path):
                        log_message(f".uassetファイルが見つかりました: {uasset_path}")
                    else:
                        log_message(f".uassetファイルが見つかりません: {uasset_path}")
                        
                        # ディレクトリ内のすべてのファイルを表示
                        files = os.listdir(test_dir)
                        log_message(f"ディレクトリ内のファイル: {files}")
                else:
                    log_message(f"テストディレクトリが存在しません: {test_dir}")
                    
                    # Contentディレクトリの中身を確認
                    if os.path.exists(content_dir):
                        files = os.listdir(content_dir)
                        log_message(f"Contentディレクトリ内のファイル・フォルダ: {files}")
            except Exception as e:
                log_message(f"ファイルシステムの確認中にエラーが発生しました: {e}")
        else:
            log_message(f"最終確認: ブループリントが見つかりません: {bp_path}")
    else:
        log_message(f"ブループリントの作成に失敗しました: {bp_path}")
except Exception as e:
    log_message(f"エラーが発生しました: {e}")

log_message("処理が完了しました。プロジェクトを閉じて再度開くと、アセットが確実に表示されます。")
return {{"success": True}}
"""
    
    # スクリプトを実行
    success, result = execute_unreal_python(script)
    return success

def main():
    """メイン処理"""
    logger.info("UE5エディタ内のシンプルなテストを開始します...")
    
    # プロジェクトディレクトリが存在することを確認
    if not os.path.exists(PROJECT_DIR):
        logger.error(f"SpaceShooterGameプロジェクトが見つかりません: {PROJECT_DIR}")
        logger.info("プロジェクトが正しく作成されていることを確認してください。")
        return False
    
    # UE5エディタが起動していることを確認、または起動
    if not ensure_ue5_running():
        logger.error("UE5エディタの起動と接続に失敗しました。セットアップを中止します。")
        return False
    
    # 追加の待機時間を設けて、エディタが完全に読み込まれるのを待つ
    logger.info("UE5エディタが完全に読み込まれるのを待機しています...")
    time.sleep(10)
    
    # Unrealエンジンでブループリントとレベルを作成
    if create_blueprints_and_level():
        logger.info("UE5でのアセット作成テストが完了しました")
        
        # 少し待機してUE5エディタに反映されるのを待つ
        time.sleep(3)
        
        # 最後に強制的にプロジェクト全体を保存するよう要求
        try:
            save_script = """
import unreal
# プロジェクト全体を保存
unreal.EditorLoadingAndSavingUtils.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log("プロジェクト全体を保存しました")
return {"success": True}
"""
            execute_unreal_python(save_script)
            logger.info("プロジェクト全体の保存を要求しました")
        except Exception as e:
            logger.warning(f"プロジェクト保存中にエラーが発生しました: {e}")
        
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
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game/ShooterGameTest"])
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
        
        # 重要なメッセージを表示
        logger.info("\n===== 重要なお知らせ =====")
        logger.info("UE5エディタでアセットを作成しましたが、ディスク上に.uassetファイルとして保存されていない可能性があります。")
        logger.info("これは、UE5の仕様で、プロジェクトを閉じるまでアセットが完全に保存されないことが原因かもしれません。")
        logger.info("次のステップを試してください：")
        logger.info("1. UE5エディタでメニューから「File」→「Save All」を選択")
        logger.info("2. UE5エディタを閉じる")
        logger.info("3. 再度プロジェクトを開く")
        logger.info("4. コンテンツブラウザで「ShooterGameTest」フォルダを確認する")
        logger.info("==========================\n")
        
        return True
    else:
        logger.error("UE5でのアセット作成テストに失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
