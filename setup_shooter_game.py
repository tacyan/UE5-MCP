#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲームのセットアップを一括で行うスクリプト

このスクリプトは、UE5エディタ内にシューティングゲームの基本要素を一括で作成します。
以下の処理を順番に実行します：
1. 基本フォルダ構造の作成
2. 基本ブループリントの作成
3. ゲームレベルの作成

使用方法:
  python setup_shooter_game.py
"""

import logging
import os
import sys
import time
import importlib.util
import subprocess
import requests

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# UE5エディタのステータスエンドポイント
UNREAL_STATUS_ENDPOINT = "http://localhost:8080/api/status"

def import_module_from_file(module_name, file_path):
    """ファイルパスからモジュールをインポートする"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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

def setup_shooter_game():
    """シューティングゲームのセットアップを行う"""
    logger.info("シューティングゲームのセットアップを開始します...")
    
    # スクリプトファイルのパス
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folders_script = os.path.join(current_dir, "setup_basic_folders.py")
    blueprints_script = os.path.join(current_dir, "setup_basic_blueprints.py")
    level_script = os.path.join(current_dir, "setup_game_level.py")
    
    # UE5エディタが起動するまで待機
    if not wait_for_unreal_connection(max_attempts=60, wait_time=5):
        logger.error("UE5エディタに接続できないため、セットアップを中止します。")
        return False
    
    # 追加の待機時間を設けて、エディタが完全に読み込まれるのを待つ
    logger.info("UE5エディタが完全に読み込まれるまで待機しています...")
    time.sleep(10)
    
    # ステップ1: フォルダ構造の作成
    logger.info("ステップ1: フォルダ構造の作成を開始します...")
    folders_module = import_module_from_file("setup_basic_folders", folders_script)
    if not folders_module.main():
        logger.error("フォルダ構造の作成に失敗しました。セットアップを中止します。")
        return False
    
    # フォルダ作成完了後、十分に待機
    logger.info("フォルダ構造の作成が完了しました。次のステップまで待機しています...")
    time.sleep(5)
    
    # ステップ2: ブループリントの作成
    logger.info("ステップ2: ブループリントの作成を開始します...")
    blueprints_module = import_module_from_file("setup_basic_blueprints", blueprints_script)
    if not blueprints_module.main():
        logger.error("ブループリントの作成に失敗しました。セットアップを中止します。")
        return False
    
    # ブループリント作成完了後、十分に待機
    logger.info("ブループリントの作成が完了しました。次のステップまで待機しています...")
    time.sleep(5)
    
    # ステップ3: ゲームレベルの作成
    logger.info("ステップ3: ゲームレベルの作成を開始します...")
    level_module = import_module_from_file("setup_game_level", level_script)
    if not level_module.main():
        logger.error("ゲームレベルの作成に失敗しました。セットアップを中止します。")
        return False
    
    logger.info("すべてのセットアップが完了しました！")
    logger.info("UE5エディタでF5キーを押してコンテンツブラウザを更新し、作成されたアセットを確認してください。")
    logger.info("ゲームをプレイするには、ShooterGameLevelを開き、プレイボタンをクリックしてください。")
    
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
        requests.post("http://localhost:8080/api/unreal/execute", json=refresh_data)
        logger.info("コンテンツブラウザの更新を要求しました")
    except Exception as e:
        logger.warning(f"自動更新に失敗しました: {str(e)}。手動でF5キーを押してください。")
    
    return True

def main():
    """メイン処理"""
    try:
        success = setup_shooter_game()
        if not success:
            logger.error("セットアップに失敗しました。")
            return False
        return True
    except Exception as e:
        logger.exception(f"セットアップ中に予期せぬエラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
