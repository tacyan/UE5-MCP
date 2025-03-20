#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPシステム起動スクリプト

このスクリプトは、Model Context Protocol (MCP) システム全体を簡単に起動するためのユーティリティです。
指定したモードに応じて、必要なMCPコンポーネントを起動します。
Windows、macOS、Linuxのすべてのプラットフォームで動作します。

主な機能:
- 「all」モード: すべてのコンポーネント（サーバー、Blender-MCP、UE5-MCP）を起動
- 「server」モード: MCPサーバーのみを起動
- 「blender」モード: MCPサーバーとBlender-MCPを起動
- 「ue5」モード: MCPサーバーとUE5-MCPを起動

使用方法:
    python run_mcp.py [mode]
    
    mode: 起動モード（all/server/blender/ue5、デフォルトはserver）
"""

import os
import sys
import subprocess
import argparse
import time
import signal
import logging
import json
import platform
from pathlib import Path
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# OSの検出
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Pythonコマンドの設定
PYTHON_CMD = "python" if IS_WINDOWS else "python3"

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_mcp")

# プロセスリスト（終了時に全てを停止するために使用）
processes = []

def signal_handler(sig, frame):
    """
    シグナルハンドラ（Ctrl+Cで終了時に全プロセスを停止）
    """
    logger.info("終了シグナルを受信しました。すべてのプロセスを停止しています...")
    for process in processes:
        try:
            if process.poll() is None:  # プロセスがまだ実行中
                if IS_WINDOWS:
                    process.kill()
                else:
                    process.terminate()
                logger.info(f"プロセス (PID: {process.pid}) を停止しました")
        except Exception as e:
            logger.error(f"プロセス終了中にエラーが発生しました: {str(e)}")
    
    logger.info("MCPシステムを終了しました")
    sys.exit(0)

def load_config():
    """
    設定ファイルをロードする
    
    戻り値:
        dict: 設定情報
    """
    # 設定ファイルパス
    config_path = os.path.join(os.getcwd(), "mcp_settings.json")
    
    try:
        if os.path.exists(config_path):
            logger.info("mcp_settings.json から設定を読み込みます")
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            logger.warning("設定ファイルが見つかりません。デフォルト設定を使用します。")
            config = {
                "server": {"host": "127.0.0.1", "port": 8000},
                "blender": {"enabled": True, "port": 9001},
                "unreal": {"enabled": True, "port": 9002}
            }
    except Exception as e:
        logger.error(f"設定ファイル読み込み中にエラーが発生しました: {str(e)}")
        config = {
            "server": {"host": "127.0.0.1", "port": 8000},
            "blender": {"enabled": True, "port": 9001},
            "unreal": {"enabled": True, "port": 9002}
        }
    
    return config

def print_system_info():
    """
    システム情報を表示する
    """
    logger.info("=== MCP システム情報 ===")
    logger.info(f"OS: {platform.system()} ({platform.platform()})")
    logger.info(f"Python: {platform.python_version()}")
    
    # 設定情報を表示
    config = load_config()
    server_host = config.get("server", {}).get("host", "127.0.0.1")
    server_port = config.get("server", {}).get("port", 8000)
    logger.info(f"MCPサーバー: http://{server_host}:{server_port}")
    
    blender_port = config.get("blender", {}).get("port", 9001)
    logger.info(f"Blender-MCP: http://{server_host}:{blender_port}")
    
    ue5_port = config.get("unreal", {}).get("port", 9002)
    logger.info(f"UE5-MCP: http://{server_host}:{ue5_port}")
    
    # OpenAI API設定を確認
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "***"
        logger.info(f"OpenAI API: 設定済み")
    else:
        logger.warning("OpenAI API: 未設定")
    
    logger.info("========================")

def check_port_availability(port):
    """
    指定されたポートが使用可能かどうかを確認する
    
    引数:
        port (int): チェックするポート番号
        
    戻り値:
        bool: ポートが使用可能ならTrue、そうでなければFalse
    """
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0  # 0なら接続可能＝使用中

def run_server():
    """
    MCPサーバーを起動する
    """
    # 設定を取得
    config = load_config()
    server_port = config.get("server", {}).get("port", 8000)
    
    # ポートの空き状況をチェック
    if not check_port_availability(server_port):
        logger.warning(f"ポート {server_port} はすでに使用されています。サーバーはすでに実行中の可能性があります。")
        return None
    
    logger.info("MCPサーバーを起動します...")
    try:
        process = subprocess.Popen([PYTHON_CMD, 'mcp_server.py'])
        processes.append(process)
        logger.info(f"MCPサーバーが起動しました (PID: {process.pid})")
        # サーバーが起動するまで少し待機
        time.sleep(2)
        return process
    except Exception as e:
        logger.error(f"MCPサーバーの起動中にエラーが発生しました: {str(e)}")
        return None

def run_blender_mcp():
    """
    Blender-MCPを起動する
    """
    # 設定を取得
    config = load_config()
    blender_port = config.get("blender", {}).get("port", 9001)
    
    # ポートの空き状況をチェック
    if not check_port_availability(blender_port):
        logger.warning(f"ポート {blender_port} はすでに使用されています。Blender-MCPはすでに実行中の可能性があります。")
        return None
    
    logger.info("Blender-MCPを起動します...")
    try:
        # Blender起動スクリプトの有無を確認
        blender_script = "blender_mcp.py"
        if not os.path.exists(blender_script):
            blender_script = "blender_integration.py"
            
        process = subprocess.Popen([PYTHON_CMD, blender_script])
        processes.append(process)
        logger.info(f"Blender-MCPが起動しました (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"Blender-MCPの起動中にエラーが発生しました: {str(e)}")
        return None

def run_ue5_mcp():
    """
    UE5-MCPを起動する
    """
    # 設定を取得
    config = load_config()
    ue5_port = config.get("unreal", {}).get("port", 9002)
    
    # ポートの空き状況をチェック
    if not check_port_availability(ue5_port):
        logger.warning(f"ポート {ue5_port} はすでに使用されています。UE5-MCPはすでに実行中の可能性があります。")
        return None
    
    logger.info("UE5-MCPを起動します...")
    try:
        # UE5起動スクリプトの有無を確認
        ue5_script = "ue5_mcp.py"
        if not os.path.exists(ue5_script):
            ue5_plugin_dir = Path("ue5_plugin")
            if ue5_plugin_dir.exists() and (ue5_plugin_dir / "mcp_plugin.py").exists():
                ue5_script = str(ue5_plugin_dir / "mcp_plugin.py")
        
        process = subprocess.Popen([PYTHON_CMD, ue5_script])
        processes.append(process)
        logger.info(f"UE5-MCPが起動しました (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"UE5-MCPの起動中にエラーが発生しました: {str(e)}")
        return None

def ensure_directories():
    """
    必要なディレクトリを作成する
    """
    dirs = [
        "assets", "temp", "logs", "exports", "imports", 
        "blender_scripts", "ue5_scripts"
    ]
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.debug(f"ディレクトリを確認: {dir_name}")

def main():
    """
    メイン関数
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='MCPシステム起動ツール')
    parser.add_argument('mode', nargs='?', default='server', 
                        choices=['all', 'server', 'blender', 'ue5'],
                        help='起動モード（all/server/blender/ue5、デフォルトはserver）')
    args = parser.parse_args()
    
    # シグナルハンドラの設定（Ctrl+Cで終了時に全プロセスを停止）
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (AttributeError, ValueError) as e:
        # Windowsでは一部のシグナルが使用できないため
        logger.warning(f"シグナルハンドラの設定中に警告が発生しました: {str(e)}")
    
    # システム情報の表示
    print_system_info()
    
    # 設定のロード
    config = load_config()
    
    # 必要なディレクトリの作成
    ensure_directories()
    
    # サーバーを起動（すべてのモードで必要）
    server_process = run_server()
    
    # モードに応じて追加のコンポーネントを起動
    if args.mode in ['all', 'blender'] and config.get('blender', {}).get('enabled', True):
        blender_process = run_blender_mcp()
    
    if args.mode in ['all', 'ue5'] and config.get('unreal', {}).get('enabled', True):
        ue5_process = run_ue5_mcp()
    
    # 使い方の表示
    logger.info(f"MCPシステムが起動しました（モード: {args.mode}）")
    logger.info("Ctrl+C で終了")
    
    # プロセスが終了しないように待機
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main() 
