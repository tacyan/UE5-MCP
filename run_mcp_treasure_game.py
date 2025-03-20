#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPフレームワーク宝箱狩りゲーム自動作成スクリプト

このスクリプトは、MCPフレームワークを使用して宝箱狩りゲームを自動的に作成します。
以下の機能を含みます:
- MCPサーバーの起動
- Blenderでのゲームアセット作成
- UE5でのゲームレベル・ロジック作成

使用方法:
  python run_mcp_treasure_game.py
"""

import os
import sys
import time
import logging
import subprocess
import threading
import signal
import atexit
from pathlib import Path
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_mcp_treasure_game")

# 実行中のプロセスリスト（終了時に停止するため）
processes = []

# スクリプトディレクトリ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def cleanup():
    """
    終了時にすべてのプロセスを停止
    """
    for proc in processes:
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

def start_mcp_server():
    """
    MCPサーバーを起動
    
    戻り値:
        subprocess.Popen: サーバープロセス
    """
    logger.info("MCPサーバーを起動しています...")
    
    try:
        # サーバー起動スクリプト
        server_script = os.path.join(SCRIPT_DIR, "mcp_server.py")
        
        # サーバープロセス起動
        process = subprocess.Popen([sys.executable, server_script])
        processes.append(process)
        
        logger.info(f"MCPサーバーを起動しました (PID: {process.pid})")
        
        # サーバーの起動を待機
        time.sleep(2)
        return process
    
    except Exception as e:
        logger.error(f"MCPサーバー起動エラー: {str(e)}")
        return None

def start_blender_api():
    """
    Blender API を起動
    
    戻り値:
        subprocess.Popen: Blenderプロセス
    """
    logger.info("Blender APIを起動しています...")
    
    try:
        # Blenderパスを取得
        blender_path = os.getenv("BLENDER_PATH", "/Applications/Blender.app/Contents/MacOS/Blender")
        
        # APIスクリプト
        api_script = os.path.join(SCRIPT_DIR, "mcp_blender_api.py")
        
        # Blenderを起動
        process = subprocess.Popen([
            blender_path,
            "--background",
            "--python", api_script
        ])
        processes.append(process)
        
        logger.info(f"Blender APIを起動しました (PID: {process.pid})")
        
        # 起動を待機
        time.sleep(3)
        return process
    
    except Exception as e:
        logger.error(f"Blender API起動エラー: {str(e)}")
        return None

def create_game():
    """
    宝箱狩りゲームを作成
    """
    logger.info("宝箱狩りゲームの作成を開始します...")
    
    try:
        # ゲーム作成スクリプト
        game_script = os.path.join(SCRIPT_DIR, "ue5_treasure_game.py")
        
        # スクリプト実行
        process = subprocess.Popen([sys.executable, game_script])
        
        # 終了を待機
        process.wait()
        
        if process.returncode == 0:
            logger.info("宝箱狩りゲームの作成が完了しました！")
            return True
        else:
            logger.error(f"ゲーム作成中にエラーが発生しました (コード: {process.returncode})")
            return False
    
    except Exception as e:
        logger.error(f"ゲーム作成中に例外が発生しました: {str(e)}")
        return False

def check_server_connection():
    """
    MCPサーバーへの接続をチェック
    
    戻り値:
        bool: 接続成功ならTrue、失敗ならFalse
    """
    import requests
    
    server_url = f"http://{os.getenv('MCP_SERVER_HOST', '127.0.0.1')}:{os.getenv('MCP_SERVER_PORT', '8080')}"
    
    for _ in range(10):  # 最大10回リトライ
        try:
            response = requests.get(f"{server_url}/api/status", timeout=1)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    logger.info(f"MCPサーバーに接続しました: {server_url}")
                    return True
        except:
            pass
        
        time.sleep(1)
    
    logger.error(f"MCPサーバーに接続できませんでした: {server_url}")
    return False

def main():
    """
    メイン実行関数
    """
    logger.info("===== 宝箱狩りゲーム自動作成 =====")
    
    # 必要なディレクトリの作成
    os.makedirs("exports", exist_ok=True)
    os.makedirs("imports", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # MCPサーバーを起動
    server_process = start_mcp_server()
    if not server_process:
        logger.error("MCPサーバーの起動に失敗しました。終了します。")
        sys.exit(1)
    
    # サーバー接続を確認
    if not check_server_connection():
        logger.error("MCPサーバーに接続できません。終了します。")
        sys.exit(1)
    
    # Blender APIを起動
    blender_process = start_blender_api()
    if not blender_process:
        logger.warning("Blender APIの起動に失敗しました。一部の機能が制限されます。")
    
    # ゲームを作成
    if create_game():
        logger.info("===== ゲームの作成が完了しました =====")
        
        # サーバーとBlenderプロセスを維持
        logger.info("プロセスは実行中のままです。Ctrl+C で終了してください。")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("ユーザーによる終了操作を検出しました。")
    else:
        logger.error("ゲームの作成に失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main() 
