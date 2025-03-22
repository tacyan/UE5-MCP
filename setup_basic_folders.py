#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5エディタ内に基本的なフォルダ構造を作成するスクリプト

このスクリプトは、UE5エディタ内に基本的なフォルダ構造を作成します。
直接Unrealエディタ内で実行するPythonコードを使用します。

使用方法:
  python setup_basic_folders.py
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

def create_folder_structure():
    """UE5エディタ内にフォルダ構造を作成する"""
    logger.info("UE5エディタ内にフォルダ構造を作成しています...")
    
    # フォルダ作成スクリプト
    script = """
import unreal
import time

# 必要なパス
base_path = "/Game/ShooterGame"
subdirs = ["Assets", "Blueprints", "Maps"]

# 結果を格納する辞書
results = {}

def ensure_directory_exists(path):
    # 指定されたパスのディレクトリを作成する
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        print(f"ディレクトリを作成します: {path}")
        success = unreal.EditorAssetLibrary.make_directory(path)
        
        # ディレクトリが実際に作成されるようダミーアセットを作成して削除
        if success:
            try:
                # テキストアセットを作成
                dummy_asset_name = "temp_dummy_asset"
                dummy_asset_path = f"{path}/{dummy_asset_name}"
                
                # アセットツールを使用してダミーアセットを作成
                asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
                text_factory = unreal.TextAssetFactory()
                asset = asset_tools.create_asset(dummy_asset_name, path, unreal.TextAsset, text_factory)
                
                if asset:
                    print(f"ダミーアセットを作成しました: {dummy_asset_path}")
                    
                    # アセットを保存
                    unreal.EditorAssetLibrary.save_asset(dummy_asset_path)
                    
                    # アセットレジストリが更新されるのを待つ
                    time.sleep(0.5)
                    
                    # ダミーアセットを削除
                    unreal.EditorAssetLibrary.delete_asset(dummy_asset_path)
                    print(f"ダミーアセットを削除しました: {dummy_asset_path}")
            except Exception as e:
                print(f"ダミーアセット作成中にエラーが発生しました: {e}")
        
        return success
    else:
        print(f"ディレクトリはすでに存在します: {path}")
        return True

# ベースディレクトリを作成
base_result = ensure_directory_exists(base_path)
results["base"] = base_result

# サブディレクトリを作成
for subdir in subdirs:
    full_path = f"{base_path}/{subdir}"
    subdir_result = ensure_directory_exists(full_path)
    results[subdir] = subdir_result

# コンテンツブラウザを更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
time.sleep(0.5)
unreal.EditorAssetLibrary.refresh_asset_directories([base_path])

# 結果の確認
print("=== フォルダ作成結果 ===")
all_ok = True
for name, success in results.items():
    print(f"{name}: {success}")
    if not success:
        all_ok = False

# 最終結果の表示
print(f"すべてのフォルダが正常に作成されました: {all_ok}")
return {{"success": all_ok, "results": results}}
"""
    
    # スクリプトを実行
    success, result = execute_unreal_python(script)
    return success

def main():
    """メイン処理"""
    logger.info("UE5エディタ内のフォルダ構造セットアップを開始します...")
    
    # UE5エディタとの接続を確認
    if not check_unreal_connection():
        logger.error("UE5エディタに接続できませんでした。UE5エディタが起動していて、MCPプラグインが有効になっていることを確認してください。")
        return False
    
    # フォルダ構造を作成
    if create_folder_structure():
        logger.info("フォルダ構造の作成に成功しました")
        
        # 少し待機してUE5エディタに反映されるのを待つ
        time.sleep(2)
        
        logger.info("UE5エディタでコンテンツブラウザを更新（F5キー）してください")
        logger.info("セットアップが完了しました")
        
        return True
    else:
        logger.error("フォルダ構造の作成に失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
