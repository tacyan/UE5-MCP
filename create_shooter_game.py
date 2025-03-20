#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲーム作成自動化スクリプト

MCPサーバーを介してBlenderとUE5を連携させ、シューティングゲームを
自動的に作成するワークフロースクリプトです。

ワークフロー:
1. MCPサーバーの起動
2. Blenderでのモデル作成
3. UE5へのモデルインポート
4. UE5でのゲームロジック実装
5. ゲームレベルの作成

使用方法:
  python create_shooter_game.py
"""

import os
import sys
import time
import logging
import subprocess
import signal
import atexit
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shooter_game_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_shooter_game")

# グローバル変数
PROCESSES = []  # 起動したプロセスのリスト
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

def start_mcp_server():
    """MCPサーバーを起動"""
    logger.info("MCPサーバーを起動しています...")
    
    # サーバープロセスを起動
    server_script = os.path.join(SCRIPT_DIR, "mcp_server.py")
    process = subprocess.Popen([sys.executable, server_script])
    PROCESSES.append(process)
    
    logger.info(f"MCPサーバーを起動しました (PID: {process.pid})")
    
    # サーバーの起動を待機
    time.sleep(3)
    
    # サーバー起動確認
    import requests
    max_retries = 5
    
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8080/api/status", timeout=1)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    logger.info("MCPサーバーが正常に応答しています")
                    return True
        except:
            pass
        
        logger.info(f"MCPサーバー起動待機中... ({i+1}/{max_retries})")
        time.sleep(2)
    
    logger.error("MCPサーバーへの接続に失敗しました")
    return False

def create_blender_models():
    """Blenderでモデルを作成"""
    logger.info("Blenderでシューティングゲームモデルを作成しています...")
    
    # Blenderスクリプト実行
    blender_script = os.path.join(SCRIPT_DIR, "blender_shooter_game.py")
    process = subprocess.Popen([sys.executable, blender_script])
    
    # 完了を待機
    process.wait()
    
    if process.returncode == 0:
        logger.info("Blenderモデル作成が完了しました")
        return True
    else:
        logger.error(f"Blenderモデル作成に失敗しました (コード: {process.returncode})")
        return False

def create_ue5_game():
    """UE5でゲームを作成"""
    logger.info("UE5でシューティングゲームを作成しています...")
    
    # UE5スクリプト実行
    ue5_script = os.path.join(SCRIPT_DIR, "ue5_shooter_game.py")
    process = subprocess.Popen([sys.executable, ue5_script])
    
    # 完了を待機
    process.wait()
    
    if process.returncode == 0:
        logger.info("UE5ゲーム作成が完了しました")
        return True
    else:
        logger.error(f"UE5ゲーム作成に失敗しました (コード: {process.returncode})")
        return False

def main():
    """メイン実行関数"""
    logger.info("===== シューティングゲーム作成ワークフローを開始します =====")
    
    # 必要なディレクトリを作成
    os.makedirs("exports", exist_ok=True)
    os.makedirs("imports", exist_ok=True)
    
    # MCPサーバーを起動
    if not start_mcp_server():
        logger.error("MCPサーバーの起動に失敗しました。終了します。")
        return 1
    
    # Blenderでモデルを作成
    if not create_blender_models():
        logger.error("Blenderモデル作成に失敗しました。UE5ゲーム作成を続行しますが、正常に動作しない可能性があります。")
    
    # UE5でゲームを作成
    if not create_ue5_game():
        logger.error("UE5ゲーム作成に失敗しました。")
        return 1
    
    logger.info("===== シューティングゲーム作成ワークフローが完了しました =====")
    logger.info("MCPサーバーは実行中です。終了するには Ctrl+C を押してください。")
    
    # サーバーを実行し続ける
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("ユーザーによって終了されました")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
