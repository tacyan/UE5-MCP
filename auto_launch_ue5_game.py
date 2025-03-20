#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5自動ゲーム開発スクリプト

UE5エディタを自動で起動し、MCPサーバーを介して自動的にゲーム制作を行うスクリプト。
Blenderでのモデル作成から、UE5へのインポート、ゲームロジックの生成までを自動化します。

機能：
- MCPサーバーの自動起動（モックモードをサポート）
- Blender APIの自動起動（バックグラウンドモード）
- 3Dモデルの自動生成
- UE5エディタの自動起動
- UE5プラグインの自動インストール
- ゲーム生成プロセスの自動実行

使用方法：
python auto_launch_ue5_game.py [--mock]

オプション:
  --mock  モックモードでサーバーを起動（UE5が動作しない環境でも動作）
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
import signal
import requests
import shutil
import atexit
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 引数のパース
parser = argparse.ArgumentParser(description='UE5自動ゲーム開発スクリプト')
parser.add_argument('--mock', action='store_true', help='モックモードでサーバーを起動')
args = parser.parse_args()

# 環境変数のロード
load_dotenv()

# 環境変数を上書き
if args.mock:
    os.environ["MOCK_MODE"] = "true"

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_launch_ue5.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auto_launch_ue5")

# グローバル変数
PROCESSES = []  # 起動したプロセスのリスト
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_MODE = args.mock

# 設定の読み込み
def load_settings():
    """設定ファイルを読み込む"""
    settings_path = os.path.join(SCRIPT_DIR, "mcp_settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"設定ファイルの読み込みエラー: {str(e)}")
        return {}

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

# MCPサーバーを起動
def start_mcp_server():
    """MCPサーバーを起動"""
    logger.info("MCPサーバーを起動しています...")
    
    try:
        # サーバー起動スクリプト
        server_script = os.path.join(SCRIPT_DIR, "mcp_server.py")
        
        # サーバープロセス起動（モックモードが有効なら環境変数を設定）
        env = os.environ.copy()
        if MOCK_MODE:
            env["MOCK_MODE"] = "true"
            logger.info("モックモードが有効: UE5の実際の起動は行わず、応答をシミュレートします")
        
        # サーバープロセス起動
        process = subprocess.Popen([sys.executable, server_script], env=env)
        PROCESSES.append(process)
        
        logger.info(f"MCPサーバーを起動しました (PID: {process.pid})")
        
        # サーバーの起動を待機
        time.sleep(5)  # 少し長めに待機
        return process
    
    except Exception as e:
        logger.error(f"MCPサーバー起動エラー: {str(e)}")
        return None

# Blender APIを起動
def start_blender_api():
    """Blender APIをバックグラウンドで起動"""
    logger.info("Blender APIを起動しています...")
    
    try:
        # Blenderパスを取得
        settings = load_settings()
        blender_path = settings.get("blender", {}).get("path", os.getenv("BLENDER_PATH", "/Applications/Blender.app/Contents/MacOS/Blender"))
        
        # APIスクリプト
        api_script = os.path.join(SCRIPT_DIR, "mcp_blender_api.py")
        
        # Blenderを起動
        process = subprocess.Popen([
            blender_path,
            "--background",
            "--python", api_script
        ])
        PROCESSES.append(process)
        
        logger.info(f"Blender APIを起動しました (PID: {process.pid})")
        
        # 起動を待機
        time.sleep(3)
        return process
    
    except Exception as e:
        logger.error(f"Blender API起動エラー: {str(e)}")
        return None

# モックアセットを作成
def create_mock_assets():
    """モックアセットを作成（オフラインテスト用）"""
    logger.info("モックアセットを作成しています...")
    
    try:
        # モックアセット作成スクリプト
        mock_script = os.path.join(SCRIPT_DIR, "create_mock_assets.py")
        
        # スクリプト実行
        process = subprocess.Popen([sys.executable, mock_script])
        process.wait()
        
        if process.returncode == 0:
            logger.info("モックアセットの作成が完了しました")
            return True
        else:
            logger.error(f"モックアセット作成エラー (コード: {process.returncode})")
            return False
    
    except Exception as e:
        logger.error(f"モックアセット作成中に例外: {str(e)}")
        return False

# サーバー接続をチェック
def check_server_connection(max_retries=15, retry_interval=2):
    """MCPサーバーへの接続を確認"""
    logger.info("MCPサーバーへの接続を確認しています...")
    
    settings = load_settings()
    server_host = settings.get("server", {}).get("host", os.getenv("MCP_SERVER_HOST", "127.0.0.1"))
    server_port = settings.get("server", {}).get("port", os.getenv("MCP_SERVER_PORT", "8080"))
    
    if server_host == "0.0.0.0":
        server_host = "127.0.0.1"  # 接続テスト用にlocalhostに変換
    
    server_url = f"http://{server_host}:{server_port}"
    
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
            if i == 0:  # 最初の失敗時のみログ出力
                logger.warning(f"MCPサーバー接続試行中... ({i+1}/{max_retries})")
        
        time.sleep(retry_interval)
    
    logger.error(f"MCPサーバーに接続できませんでした: {server_url}")
    return False

# UE5プラグインをインストール
def install_ue5_plugin():
    """UE5プロジェクトにMCPプラグインをインストール"""
    if MOCK_MODE:
        logger.info("モックモード: UE5プラグインのインストールをスキップします")
        return True
        
    logger.info("UE5プラグインをインストールしています...")
    
    try:
        settings = load_settings()
        project_path = settings.get("unreal", {}).get("project_path", os.getenv("UE5_PROJECT_PATH"))
        
        if not project_path:
            logger.error("UE5プロジェクトパスが設定されていません")
            return False
        
        # プロジェクトディレクトリからの相対パス
        project_dir = os.path.dirname(project_path)
        plugin_dest_dir = os.path.join(project_dir, "Plugins", "MCP")
        
        # プラグインソースディレクトリ
        plugin_src_dir = os.path.join(SCRIPT_DIR, "ue5_plugin")
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(plugin_dest_dir, exist_ok=True)
        
        # プラグインファイルをコピー
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
        logger.error(f"UE5プラグインインストールエラー: {str(e)}")
        return False

# UE5エディタを起動
def start_ue5_editor():
    """UE5エディタを起動"""
    if MOCK_MODE:
        logger.info("モックモード: UE5エディタの起動をスキップします")
        return subprocess.Popen(["echo", "モックモードのUE5"])  # ダミープロセス
        
    logger.info("Unreal Engineを起動しています...")
    
    try:
        settings = load_settings()
        ue5_path = settings.get("unreal", {}).get("path", os.getenv("UE5_PATH"))
        project_path = settings.get("unreal", {}).get("project_path", os.getenv("UE5_PROJECT_PATH"))
        
        if not ue5_path or not os.path.exists(ue5_path):
            logger.error(f"UE5実行ファイルが見つかりません: {ue5_path}")
            return None
        
        if not project_path:
            logger.error("UE5プロジェクトパスが設定されていません")
            return None
        
        # UE5を起動
        process = subprocess.Popen([ue5_path, project_path])
        PROCESSES.append(process)
        
        logger.info(f"Unreal Engineを起動しました (PID: {process.pid})")
        
        # UE5の起動を待機
        time.sleep(10)
        return process
    
    except Exception as e:
        logger.error(f"UE5起動エラー: {str(e)}")
        return None

# トレジャーゲーム作成
def create_treasure_game():
    """トレジャーハントゲームを作成"""
    logger.info("トレジャーハントゲームの作成を開始します...")
    
    try:
        # ゲーム作成スクリプト
        game_script = os.path.join(SCRIPT_DIR, "ue5_treasure_game.py")
        
        # 環境変数の設定
        env = os.environ.copy()
        if MOCK_MODE:
            env["MOCK_MODE"] = "true"
        
        # スクリプト実行
        process = subprocess.Popen([sys.executable, game_script], env=env)
        process.wait()
        
        if process.returncode == 0:
            logger.info("トレジャーハントゲームの作成が完了しました！")
            return True
        else:
            logger.error(f"ゲーム作成エラー (コード: {process.returncode})")
            return False
    
    except Exception as e:
        logger.error(f"ゲーム作成中に例外: {str(e)}")
        return False

# メイン関数
def main():
    """メイン実行関数"""
    logger.info("===== UE5自動ゲーム開発を開始します =====")
    if MOCK_MODE:
        logger.info("モックモードで実行中 - UE5は実際には起動せず、挙動をシミュレートします")
    
    # 必要なディレクトリの作成
    os.makedirs("exports", exist_ok=True)
    os.makedirs("imports", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # サーバーのプロセスチェック
    existing_mcp_server = False
    try:
        response = requests.get("http://127.0.0.1:8080/api/status", timeout=1)
        if response.status_code == 200:
            logger.info("既に実行中のMCPサーバーが見つかりました")
            existing_mcp_server = True
    except:
        pass
    
    # MCPサーバーを起動（既に起動していない場合）
    server_process = None
    if not existing_mcp_server:
        server_process = start_mcp_server()
        if not server_process:
            logger.error("MCPサーバーの起動に失敗しました。終了します。")
            sys.exit(1)
    
    # サーバー接続を確認
    if not check_server_connection():
        logger.error("MCPサーバーに接続できません。終了します。")
        sys.exit(1)
    
    # Blender APIをバックグラウンドで起動
    blender_process = start_blender_api()
    if not blender_process:
        logger.warning("Blender APIの起動に失敗しました。代わりにモックアセットを使用します。")
        # モックアセットを作成
        create_mock_assets()
    
    # UE5プラグインをインストール
    if not install_ue5_plugin():
        logger.warning("UE5プラグインのインストールに失敗しました。一部の機能が制限される可能性があります。")
    
    # UE5エディタを起動
    ue5_process = start_ue5_editor()
    if not ue5_process and not MOCK_MODE:
        logger.error("UE5エディタの起動に失敗しました。ゲーム作成を続行しますが、結果を視覚的に確認できません。")
    
    # UE5エディタの起動を待機（モックモードでなければ）
    if not MOCK_MODE:
        logger.info("UE5エディタの起動を待機しています...")
        time.sleep(15)
    
    # トレジャーゲームを作成
    if create_treasure_game():
        logger.info("===== ゲームの作成が完了しました =====")
        if MOCK_MODE:
            logger.info("モックモードで実行完了: 生成されたアセットとブループリントをチェックしてください。")
        else:
            logger.info("UE5エディタが実行中です。ゲームを確認してください。")
        logger.info("終了するには Ctrl+C を押してください。")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("ユーザーによる終了操作を検出しました。プロセスを終了します。")
    else:
        logger.error("ゲームの作成に失敗しました。")
        sys.exit(1)

# スクリプト実行
if __name__ == "__main__":
    main() 
