#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPシステム起動スクリプト

このスクリプトは、Model Context Protocol (MCP) システム全体を簡単に起動するためのユーティリティです。
指定したモードに応じて、必要なMCPコンポーネントを起動します。

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
import yaml
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

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

def load_config():
    """
    設定ファイルを読み込む
    
    戻り値:
        dict: 設定情報
    """
    try:
        if os.path.exists('config.yml'):
            with open('config.yml', 'r') as f:
                return yaml.safe_load(f)
        else:
            logger.warning("設定ファイルが見つかりません。デフォルト設定を使用します。")
            return {
                'server': {
                    'host': '127.0.0.1',
                    'port': 5000,
                    'debug': False
                },
                'blender': {
                    'enabled': True,
                    'port': 5001
                },
                'unreal': {
                    'enabled': True,
                    'port': 5002
                }
            }
    except Exception as e:
        logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {str(e)}")
        sys.exit(1)

def run_server():
    """
    MCPサーバーを起動する
    """
    logger.info("MCPサーバーを起動します...")
    try:
        process = subprocess.Popen([sys.executable, 'server.py'])
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
    logger.info("Blender-MCPを起動します...")
    try:
        process = subprocess.Popen([sys.executable, 'blender_mcp.py'])
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
    logger.info("UE5-MCPを起動します...")
    try:
        process = subprocess.Popen([sys.executable, 'ue5_mcp.py'])
        processes.append(process)
        logger.info(f"UE5-MCPが起動しました (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"UE5-MCPの起動中にエラーが発生しました: {str(e)}")
        return None

def signal_handler(sig, frame):
    """
    シグナルハンドラ（Ctrl+Cなどで終了時に呼ばれる）
    """
    logger.info("終了シグナルを受信しました。すべてのプロセスを停止します...")
    for process in processes:
        try:
            logger.info(f"プロセス {process.pid} を停止します...")
            process.terminate()
        except:
            pass
    
    # プロセスが終了するまで少し待機
    time.sleep(1)
    
    # 終了していないプロセスを強制終了
    for process in processes:
        if process.poll() is None:
            try:
                logger.info(f"プロセス {process.pid} を強制終了します...")
                process.kill()
            except:
                pass
    
    logger.info("すべてのプロセスが停止しました。")
    sys.exit(0)

def print_system_info():
    """
    システム情報を表示する
    """
    logger.info("=== MCP システム情報 ===")
    config = load_config()
    
    # MCPサーバー情報
    server_host = config['server']['host']
    server_port = config['server']['port']
    logger.info(f"MCPサーバー: http://{server_host}:{server_port}")
    
    # Blender-MCP情報
    if config['blender']['enabled']:
        blender_port = config['blender']['port']
        logger.info(f"Blender-MCP: http://{server_host}:{blender_port}")
    else:
        logger.info("Blender-MCP: 無効")
    
    # UE5-MCP情報
    if config['unreal']['enabled']:
        ue5_port = config['unreal']['port']
        logger.info(f"UE5-MCP: http://{server_host}:{ue5_port}")
    else:
        logger.info("UE5-MCP: 無効")
    
    # AI状態の確認
    ai_key = os.environ.get('OPENAI_API_KEY')
    if ai_key:
        logger.info("OpenAI API: 設定済み")
    else:
        logger.info("OpenAI API: 未設定（モックモードで動作します）")
    
    logger.info("========================")

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
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # システム情報の表示
    print_system_info()
    
    # 設定のロード
    config = load_config()
    
    # サーバーを起動（すべてのモードで必要）
    server_process = run_server()
    if not server_process:
        sys.exit(1)
    
    # モードに応じて追加のコンポーネントを起動
    if args.mode in ['all', 'blender'] and config['blender']['enabled']:
        blender_process = run_blender_mcp()
        if not blender_process and args.mode == 'blender':
            logger.error("Blender-MCPの起動に失敗しました。")
            signal_handler(None, None)
            sys.exit(1)
    
    if args.mode in ['all', 'ue5'] and config['unreal']['enabled']:
        ue5_process = run_ue5_mcp()
        if not ue5_process and args.mode == 'ue5':
            logger.error("UE5-MCPの起動に失敗しました。")
            signal_handler(None, None)
            sys.exit(1)
    
    # 使い方の表示
    logger.info(f"MCPシステムが起動しました（モード: {args.mode}）")
    logger.info("Ctrl+C で終了")
    
    # すべてのプロセスが終了するまで待機
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main() 
