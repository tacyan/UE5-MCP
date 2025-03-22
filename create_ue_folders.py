#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5エディタ内のディレクトリ構造を直接作成するスクリプト

このスクリプトは、UE5エディタ内に基本的なディレクトリ構造を作成します。
MCPフレームワークを使用して、ShooterGameの基本構造を設定します。

使用方法:
  python create_ue_folders.py
"""

import logging
from ue5_mcp_client import UE5MCPClient

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("create_ue_folders")

def create_directories():
    """UE5エディタ内に必要なディレクトリを作成する"""
    logger.info("UE5エディタ内にディレクトリを作成します...")
    
    client = UE5MCPClient(host="127.0.0.1", port=8080)
    
    # 非常にシンプルなスクリプト - 直接フォルダを作成
    script = """
import unreal

def create_directory(path):
    # フォルダを作成し、結果を返す
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        print(f"ディレクトリを作成します: {path}")
        success = unreal.EditorAssetLibrary.make_directory(path)
        print(f"ディレクトリ作成結果: {success}")
        return success
    else:
        print(f"ディレクトリはすでに存在します: {path}")
        return True

# メインディレクトリ
base_dir = "/Game/ShooterGame"
create_directory(base_dir)

# サブディレクトリ
subdirs = ["Assets", "Blueprints", "Maps"]
for subdir in subdirs:
    path = f"{base_dir}/{subdir}"
    create_directory(path)

# 確認
print("作成済みディレクトリの確認:")
for subdir in [""] + subdirs:
    path = f"{base_dir}/{subdir}".rstrip("/")
    exists = unreal.EditorAssetLibrary.does_directory_exist(path)
    print(f"ディレクトリ {path} 存在: {exists}")

# コンテンツブラウザを更新
unreal.EditorAssetLibrary.refresh_asset_directories(["/Game"])
unreal.EditorAssetLibrary.refresh_asset_directories([base_dir])
"""
    
    result = client.execute_unreal_command("execute_python", {"script": script})
    
    if result.get("status") == "success":
        logger.info("ディレクトリの作成に成功しました")
    else:
        logger.error(f"ディレクトリの作成に失敗しました: {result}")
    
    return result

if __name__ == "__main__":
    result = create_directories()
    print(result) 
