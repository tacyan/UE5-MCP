#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5プロジェクト作成＆シューティングゲーム自動生成スクリプト

新しいUE5プロジェクトを作成し、BlenderとMCPを使用して
自動的にシューティングゲームを生成するマスタースクリプトです。

機能:
- UE5を起動して新規プロジェクトを作成（またはモードモードで実行）
- MCPサーバーを起動してBlenderと連携
- 3Dモデルの生成とインポート
- ゲームロジックの実装
- 遊べるレベルの生成

使用方法:
  python create_ue5_project.py [--mock]

オプション:
  --mock  モックモードで実行（UE5が見つからない場合も処理を続行）
"""

import os
import sys
import time
import json
import logging
import subprocess
import shutil
import signal
import atexit
import requests
import argparse
from pathlib import Path

# コマンドライン引数の解析
parser = argparse.ArgumentParser(description='UE5プロジェクト作成＆シューティングゲーム自動生成')
parser.add_argument('--mock', action='store_true', help='モックモードで実行')
args = parser.parse_args()

# モックモードを設定
MOCK_MODE = args.mock

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ue5_project_creation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_ue5_project")

# グローバル変数
PROCESSES = []  # 起動したプロセスのリスト
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# UE5プロジェクト設定
UE5_PROJECT_NAME = "SpaceShooterGame"
UE5_PROJECT_DIR = os.path.expanduser(f"~/Documents/{UE5_PROJECT_NAME}")
UE5_PROJECT_PATH = os.path.join(UE5_PROJECT_DIR, f"{UE5_PROJECT_NAME}.uproject")

# 終了時にプロセスをクリーンアップする関数
def cleanup():
    """すべての子プロセスを終了"""
    for proc in PROCESSES:
        try:
            if proc.poll() is None:  # プロセスがまだ実行中
                logger.info(f"プロセス (PID: {proc.pid}) を停止しています...")
                proc.terminate()
                time.sleep(0.5)
                if proc.poll() is None:
                    proc.kill()  # 強制終了
        except Exception as e:
            logger.error(f"プロセス終了中にエラー: {str(e)}")
    
    logger.info("すべてのプロセスを停止しました。")

# 終了ハンドラを登録
atexit.register(cleanup)
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

def get_ue5_path():
    """UE5実行ファイルのパスを取得する"""
    # 環境変数から取得
    ue5_path = os.getenv("UE5_PATH", "")
    
    # 引用符があれば削除
    if ue5_path.startswith('"') and ue5_path.endswith('"'):
        ue5_path = ue5_path[1:-1]

    # 環境変数に適切なパスがなければ、.envファイルから直接取得を試みる
    if not ue5_path or not os.path.exists(ue5_path):
        env_file = os.path.join(SCRIPT_DIR, ".env")
        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key == "UE5_PATH":
                                ue5_path = value
                                # 引用符があれば削除
                                if ue5_path.startswith('"') and ue5_path.endswith('"'):
                                    ue5_path = ue5_path[1:-1]
                                break
            except Exception as e:
                logger.error(f".envファイルの読み込みエラー: {str(e)}")
    
    # 環境変数にない場合はデフォルトパスをプラットフォームに応じて使用
    if not ue5_path or not os.path.exists(ue5_path):
        if sys.platform == "darwin":  # macOS
            # macOSでは以下の可能性があります
            possibilities = [
                "/Users/Shared/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
                "/Users/Shared/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor",
                "/Applications/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
                "/Applications/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor"
            ]
            for path in possibilities:
                if os.path.exists(path):
                    ue5_path = path
                    break
        elif sys.platform == "win32":  # Windows
            # Windowsでは一般的なインストールパスを試します
            possibilities = [
                r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe",
                r"C:\Program Files\Unreal Engine\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
            ]
            for path in possibilities:
                if os.path.exists(path):
                    ue5_path = path
                    break
    
    # パスが見つからないかファイルが存在しない場合
    if not ue5_path or not os.path.exists(ue5_path):
        logger.error(f"UE5実行ファイルのパスが見つかりません: {ue5_path}")
        logger.error("UE5_PATH環境変数を確認してください。")
        return None
    
    logger.info(f"UE5パス: {ue5_path}")
    return ue5_path

def get_blender_path():
    """Blenderのパスを取得する"""
    # 環境変数から取得
    blender_path = os.getenv("BLENDER_PATH", "")
    
    # 引用符があれば削除
    if blender_path.startswith('"') and blender_path.endswith('"'):
        blender_path = blender_path[1:-1]
    
    # 環境変数にない場合はデフォルトパスを使用
    if not blender_path:
        if sys.platform == "darwin":  # macOS
            blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
        elif sys.platform == "win32":  # Windows
            blender_path = r"C:\Program Files\Blender Foundation\Blender\blender.exe"
        else:  # Linux その他
            blender_path = "blender"
    
    # パスが見つからないかファイルが存在しない場合
    if not os.path.exists(blender_path):
        logger.error(f"Blenderのパスが見つかりません: {blender_path}")
        logger.error("BLENDER_PATH環境変数を確認してください。")
        return None
    
    logger.info(f"Blenderパス: {blender_path}")
    return blender_path

def update_env_file():
    """環境変数設定ファイルを更新する"""
    logger.info("環境変数設定ファイルを更新しています...")
    
    env_file = os.path.join(SCRIPT_DIR, ".env")
    
    # 現在の設定を読み込む
    env_vars = {}
    try:
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
    except Exception as e:
        logger.error(f"環境変数ファイルの読み込みエラー: {str(e)}")
    
    # プロジェクトパスを更新
    env_vars["UE5_PROJECT_PATH"] = UE5_PROJECT_PATH
    
    # 環境変数をファイルに書き込む
    try:
        with open(env_file, "w") as f:
            f.write("# MCP環境変数設定ファイル\n")
            f.write("# このファイルは.envとして保存され、MCPシステムの設定を管理します\n\n")
            
            # OpenAI API設定
            f.write("# OpenAI API設定\n")
            f.write(f"OPENAI_API_KEY={env_vars.get('OPENAI_API_KEY', '')}\n\n")
            
            # サーバー設定
            f.write("# サーバー設定\n")
            f.write(f"MCP_SERVER_HOST={env_vars.get('MCP_SERVER_HOST', '0.0.0.0')}\n")
            f.write(f"MCP_SERVER_PORT={env_vars.get('MCP_SERVER_PORT', '8080')}\n")
            f.write(f"DEBUG={env_vars.get('DEBUG', 'false')}\n\n")
            
            # Blender設定
            f.write("# Blender設定\n")
            f.write(f"BLENDER_ENABLED={env_vars.get('BLENDER_ENABLED', 'true')}\n")
            f.write(f"BLENDER_PORT={env_vars.get('BLENDER_PORT', '8081')}\n")
            f.write(f"BLENDER_PATH={env_vars.get('BLENDER_PATH', get_blender_path())}\n\n")
            
            # UE5設定
            f.write("# UE5設定\n")
            f.write(f"UE5_ENABLED={env_vars.get('UE5_ENABLED', 'true')}\n")
            f.write(f"UE5_PORT={env_vars.get('UE5_PORT', '8082')}\n")
            f.write(f"UE5_PATH={env_vars.get('UE5_PATH', get_ue5_path())}\n")
            f.write(f"UE5_PROJECT_PATH={UE5_PROJECT_PATH}\n\n")
            
            # サブモジュール設定
            f.write("# サブモジュール設定\n")
            f.write(f"BLENDER_MCP_PORT={env_vars.get('BLENDER_MCP_PORT', '9081')}\n")
            f.write(f"UE5_MCP_PORT={env_vars.get('UE5_MCP_PORT', '9082')}\n")
        
        logger.info("環境変数設定ファイルを更新しました")
        return True
    except Exception as e:
        logger.error(f"環境変数ファイルの書き込みエラー: {str(e)}")
        return False

def update_mcp_settings():
    """MCP設定ファイルを更新する"""
    logger.info("MCP設定ファイルを更新しています...")
    
    settings_file = os.path.join(SCRIPT_DIR, "mcp_settings.json")
    
    # 現在の設定を読み込む
    settings = {}
    try:
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                settings = json.load(f)
    except Exception as e:
        logger.error(f"設定ファイルの読み込みエラー: {str(e)}")
    
    # Unrealプロジェクトパスを更新
    if "unreal" in settings:
        settings["unreal"]["project_path"] = UE5_PROJECT_PATH
    
    # 設定をファイルに書き込む
    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        
        logger.info("MCP設定ファイルを更新しました")
        return True
    except Exception as e:
        logger.error(f"設定ファイルの書き込みエラー: {str(e)}")
        return False

def create_ue5_project():
    """UE5プロジェクトを作成する"""
    logger.info(f"UE5プロジェクト '{UE5_PROJECT_NAME}' を作成しています...")
    
    # モックモードの場合は仮想的に処理
    if MOCK_MODE:
        logger.info("モックモード: UE5プロジェクト作成をシミュレートします")
        os.makedirs(UE5_PROJECT_DIR, exist_ok=True)
        
        # 仮のuprojectファイルを作成
        mock_uproject = {
            "FileVersion": 3,
            "EngineAssociation": "5.5",
            "Category": "Game",
            "Description": "MCP自動生成シューティングゲーム",
            "Modules": [
                {
                    "Name": "SpaceShooterGame",
                    "Type": "Runtime",
                    "LoadingPhase": "Default"
                }
            ],
            "Plugins": [
                {
                    "Name": "MCP",
                    "Enabled": True
                }
            ]
        }
        
        # uprojectファイルに書き込み
        try:
            with open(UE5_PROJECT_PATH, 'w') as f:
                json.dump(mock_uproject, f, indent=2)
            logger.info(f"モックuprojectファイルを作成しました: {UE5_PROJECT_PATH}")
            return True
        except Exception as e:
            logger.error(f"モックuprojectファイル作成エラー: {str(e)}")
            return False
    
    # 実際のUE5パスを取得
    ue5_path = get_ue5_path()
    if not ue5_path and not MOCK_MODE:
        logger.error("UE5実行ファイルが見つかりません。--mockオプションを使用してモックモードで実行してください。")
        return False
    
    # プロジェクトディレクトリが既に存在するか確認
    if os.path.exists(UE5_PROJECT_DIR):
        logger.warning(f"プロジェクトディレクトリ '{UE5_PROJECT_DIR}' は既に存在します。")
        if os.path.exists(UE5_PROJECT_PATH):
            logger.info(f"プロジェクト '{UE5_PROJECT_PATH}' は既に存在します。既存プロジェクトを使用します。")
            return True
    else:
        os.makedirs(UE5_PROJECT_DIR, exist_ok=True)
    
    # UE5コマンドラインパラメータ (macOSとWindows/Linuxで異なる)
    if sys.platform == "darwin":  # macOS
        # macOSではプロセス起動前に環境変数を設定して、別のスクリプトで作成するように変更
        temp_script_path = os.path.join(SCRIPT_DIR, "create_ue5_project_temp.sh")
        with open(temp_script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"mkdir -p \"{UE5_PROJECT_DIR}\"\n")
            f.write(f"\"{ue5_path}\" -createproject -projectpath=\"{UE5_PROJECT_DIR}\" -projectname=\"{UE5_PROJECT_NAME}\" -templatename=\"BlankBP\" -gamefirst\n")
        
        # 実行権限を付与
        os.chmod(temp_script_path, 0o755)
        
        # スクリプトを実行
        cmd = [temp_script_path]
    else:
        # Windows/Linuxの場合は直接コマンドを実行
        cmd = [
            ue5_path,
            "-createproject",
            f"-projectpath={UE5_PROJECT_DIR}",
            f"-projectname={UE5_PROJECT_NAME}",
            "-template=BlankBP",
            "-gamefirst"
        ]
    
    # プロジェクト作成
    try:
        logger.info(f"UE5プロジェクト作成コマンド: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            logger.info(f"UE5プロジェクト '{UE5_PROJECT_NAME}' の作成に成功しました")
            return True
        else:
            logger.error(f"UE5プロジェクト作成に失敗しました (コード: {process.returncode})")
            return False
    except Exception as e:
        logger.error(f"UE5プロジェクト作成中にエラーが発生しました: {str(e)}")
        return False

def start_mcp_server():
    """MCPサーバーを起動する"""
    logger.info("MCPサーバーを起動しています...")
    
    # サーバー起動スクリプト
    server_script = os.path.join(SCRIPT_DIR, "mcp_server.py")
    
    # モックモードの設定
    env = os.environ.copy()
    if MOCK_MODE:
        env["MOCK_MODE"] = "true"
        logger.info("モックモード: MCPサーバーのUE5連携をシミュレートします")
    
    # サーバー起動
    process = subprocess.Popen([sys.executable, server_script], env=env)
    PROCESSES.append(process)
    
    logger.info(f"MCPサーバーを起動しました (PID: {process.pid})")
    
    # サーバー起動を待機
    time.sleep(5)
    
    # サーバー起動確認
    max_retries = 10
    server_url = "http://127.0.0.1:8080"
    
    for i in range(max_retries):
        try:
            # 両方のエンドポイントを試す
            endpoints = ["/api/status", "/status"]
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{server_url}{endpoint}", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "running":
                            logger.info(f"MCPサーバーに接続しました: {server_url}{endpoint}")
                            return True
                except:
                    continue
        except Exception as e:
            pass
        
        logger.info(f"MCPサーバー起動待機中... ({i+1}/{max_retries})")
        time.sleep(2)
    
    logger.error("MCPサーバーへの接続に失敗しました")
    return False

def install_ue5_plugin():
    """UE5プロジェクトにMCPプラグインをインストールする"""
    logger.info("UE5プラグインをインストールしています...")
    
    # モックモードの場合
    if MOCK_MODE:
        logger.info("モックモード: UE5プラグインのインストールをシミュレートします")
        
        # Pluginsディレクトリを作成
        plugin_dest_dir = os.path.join(UE5_PROJECT_DIR, "Plugins", "MCP")
        os.makedirs(plugin_dest_dir, exist_ok=True)
        
        # 仮のプラグイン設定ファイルを作成
        plugin_config = {
            "FileVersion": 3,
            "Version": 1,
            "VersionName": "1.0",
            "FriendlyName": "MCP",
            "Description": "Model Context Protocol plugin for UE5",
            "Category": "Other",
            "CreatedBy": "MCP Framework",
            "CreatedByURL": "",
            "DocsURL": "",
            "MarketplaceURL": "",
            "CanContainContent": True,
            "Installed": True
        }
        
        # アップルーグイン設定ファイルを書き込み
        try:
            with open(os.path.join(plugin_dest_dir, "MCP.uplugin"), 'w') as f:
                json.dump(plugin_config, f, indent=2)
            
            logger.info(f"モックプラグインファイルを作成しました: {plugin_dest_dir}")
            return True
        except Exception as e:
            logger.error(f"モックプラグインファイル作成エラー: {str(e)}")
            return False
    
    # プロジェクトディレクトリのPluginsフォルダ
    plugin_dest_dir = os.path.join(UE5_PROJECT_DIR, "Plugins", "MCP")
    os.makedirs(plugin_dest_dir, exist_ok=True)
    
    # プラグインソースディレクトリ
    plugin_src_dir = os.path.join(SCRIPT_DIR, "ue5_plugin")
    
    if not os.path.exists(plugin_src_dir):
        logger.error(f"プラグインソースディレクトリ '{plugin_src_dir}' が見つかりません")
        return False
    
    # プラグインファイルをコピー
    try:
        for item in os.listdir(plugin_src_dir):
            src_item = os.path.join(plugin_src_dir, item)
            dst_item = os.path.join(plugin_dest_dir, item)
            
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)
        
        logger.info(f"UE5プラグインをインストールしました: {plugin_dest_dir}")
        return True
    except Exception as e:
        logger.error(f"プラグインインストール中にエラーが発生しました: {str(e)}")
        return False

def open_ue5_project():
    """UE5プロジェクトを開く"""
    logger.info(f"UE5プロジェクト '{UE5_PROJECT_PATH}' を開いています...")
    
    # モックモードの場合
    if MOCK_MODE:
        logger.info("モックモード: UE5エディタの起動をシミュレートします")
        
        # モックプロセスを作成（ダミーコマンド）
        process = subprocess.Popen(["echo", f"モックUE5エディタ: {UE5_PROJECT_PATH}"])
        PROCESSES.append(process)
        
        logger.info("モックUE5エディタを起動しました")
        return process
    
    # 実際のUE5パスを取得
    ue5_path = get_ue5_path()
    if not ue5_path:
        logger.error("UE5実行ファイルが見つかりません。--mockオプションを使用してモックモードで実行してください。")
        return None
    
    # UE5を起動
    try:
        # macOSとその他のプラットフォームで起動方法を変える
        if sys.platform == "darwin":  # macOS
            # macOSでは実行スクリプトを作成
            temp_script_path = os.path.join(SCRIPT_DIR, "open_ue5_project_temp.sh")
            with open(temp_script_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"\"{ue5_path}\" \"{UE5_PROJECT_PATH}\"\n")
            
            # 実行権限を付与
            os.chmod(temp_script_path, 0o755)
            
            # スクリプトを実行
            process = subprocess.Popen([temp_script_path])
        else:
            # Windows/Linuxの場合は直接コマンドを実行
            process = subprocess.Popen([ue5_path, UE5_PROJECT_PATH])
        
        PROCESSES.append(process)
        
        logger.info(f"UE5を起動しました (PID: {process.pid})")
        
        # UE5の起動を待機
        time.sleep(15)
        return process
    except Exception as e:
        logger.error(f"UE5起動中にエラーが発生しました: {str(e)}")
        return None

def create_models_with_blender():
    """Blenderを使用して3Dモデルを作成する"""
    logger.info("Blenderでシューティングゲーム用のモデルを作成しています...")
    
    # スクリプト実行
    blender_script = os.path.join(SCRIPT_DIR, "blender_shooter_game.py")
    
    try:
        process = subprocess.Popen([sys.executable, blender_script])
        
        # 完了を待機
        process.wait()
        
        if process.returncode == 0:
            logger.info("Blenderによるモデル作成が完了しました")
            return True
        else:
            logger.error(f"Blenderによるモデル作成に失敗しました (コード: {process.returncode})")
            return False
    except Exception as e:
        logger.error(f"Blenderスクリプト実行中にエラーが発生しました: {str(e)}")
        return False

def create_game_in_ue5():
    """UE5でゲームを作成する"""
    logger.info("UE5でシューティングゲームを作成しています...")
    
    # スクリプト実行
    ue5_script = os.path.join(SCRIPT_DIR, "ue5_shooter_game.py")
    
    try:
        process = subprocess.Popen([sys.executable, ue5_script])
        
        # 完了を待機
        process.wait()
        
        if process.returncode == 0:
            logger.info("UE5ゲーム作成が完了しました")
            return True
        else:
            logger.error(f"UE5ゲーム作成に失敗しました (コード: {process.returncode})")
            return False
    except Exception as e:
        logger.error(f"UE5スクリプト実行中にエラーが発生しました: {str(e)}")
        return False

def main():
    """メイン実行関数"""
    logger.info("===== UE5プロジェクト作成＆シューティングゲーム自動生成を開始 =====")
    
    # モックモードの表示
    if MOCK_MODE:
        logger.info("モックモードで実行中: UE5の実際の起動は行わず、動作をシミュレートします")
    
    # 必要なディレクトリを作成
    os.makedirs("exports", exist_ok=True)
    os.makedirs("imports", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 設定ファイルを更新
    update_env_file()
    update_mcp_settings()
    
    # UE5プロジェクトを作成
    if not create_ue5_project():
        logger.error("UE5プロジェクトの作成に失敗しました。終了します。")
        return 1
    
    # UE5プラグインをインストール
    if not install_ue5_plugin():
        logger.warning("UE5プラグインのインストールに失敗しました。続行しますが、機能が制限される可能性があります。")
    
    # MCPサーバーを起動
    if not start_mcp_server():
        logger.error("MCPサーバーの起動に失敗しました。終了します。")
        return 1
    
    # Blenderでモデルを作成
    if not create_models_with_blender():
        logger.warning("Blenderでのモデル作成に問題がありました。続行しますが、一部のモデルが使用できない可能性があります。")
    
    # UE5プロジェクトを開く
    ue5_process = open_ue5_project()
    if not ue5_process and not MOCK_MODE:
        logger.warning("UE5の起動に失敗しました。続行しますが、結果を視覚的に確認できません。")
    
    # UE5でゲームを作成
    if not create_game_in_ue5():
        logger.error("UE5でのゲーム作成に失敗しました。")
        return 1
    
    logger.info("===== UE5プロジェクト作成＆シューティングゲーム自動生成が完了しました =====")
    if MOCK_MODE:
        logger.info("モックモードで実行されました: 実際のUE5は起動していません")
        logger.info(f"作成されたプロジェクト: {UE5_PROJECT_PATH}")
    else:
        logger.info("UE5エディタでゲームを確認し、実行してください！")
    logger.info("終了するには Ctrl+C を押してください。")
    
    # サーバーとUE5を実行し続ける
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("ユーザーによって終了されました")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
