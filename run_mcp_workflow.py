#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP統合ワークフロー実行スクリプト

このスクリプトは、MCPサーバーを起動し、BlenderとUE5を連携した
ワークフローを実行するためのものです。OpenAI APIを使用して
AIドリブンの開発を行います。

主な機能:
- MCPサーバーの起動
- Blenderで3Dモデルを作成してUE5に転送
- UE5でゲームプロジェクトの作成
- AIを活用したゲーム開発支援

使用方法:
    python run_mcp_workflow.py [workflow]
    
    workflow: 実行するワークフロー (blender_to_ue5, simple_game, ai_assistant)

制限事項:
- Blender 4.0以上およびUE5.1以上が必要です
- OpenAI APIキーが設定されている必要があります
"""

import os
import sys
import subprocess
import argparse
import time
import logging
import json
import platform
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_workflow")

# OSの検出
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Pythonコマンドの設定
PYTHON_CMD = "python" if IS_WINDOWS else "python3"

# プロセスリスト（終了時に全てを停止するために使用）
processes = []

def ensure_mcp_server_running():
    """
    MCPサーバーを起動する
    
    戻り値:
        bool: 起動成功したかどうか
    """
    logger.info("MCPサーバーの状態を確認しています...")
    
    # すでに起動しているかをチェック
    try:
        # 設定を読み込み
        with open('mcp_settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        server_host = settings.get('server', {}).get('host', '127.0.0.1')
        server_port = settings.get('server', {}).get('port', 8000)
        
        # サーバーに接続を試みる
        import requests
        response = requests.get(f"http://{server_host}:{server_port}/status", timeout=2)
        
        if response.status_code == 200:
            status_data = response.json()
            if status_data.get("status") == "running":
                logger.info("MCPサーバーはすでに起動しています")
                return True
    except:
        pass
    
    # サーバーが起動していないので起動
    logger.info("MCPサーバーを起動します...")
    try:
        # サーバープロセスを開始（バックグラウンドで実行）
        process = subprocess.Popen([PYTHON_CMD, 'run_mcp.py', 'all'])
        processes.append(process)
        
        # サーバーが起動するまで少し待機
        time.sleep(5)
        logger.info(f"MCPサーバーを起動しました (PID: {process.pid})")
        
        # 再度接続を試みる
        try:
            response = requests.get(f"http://{server_host}:{server_port}/status", timeout=2)
            if response.status_code == 200:
                status_data = response.json()
                if status_data.get("status") == "running":
                    logger.info("MCPサーバーは正常に起動しています")
                    return True
        except:
            pass
        
        logger.error("MCPサーバーの起動後に接続できませんでした")
        return False
    except Exception as e:
        logger.error(f"MCPサーバーの起動中にエラーが発生しました: {str(e)}")
        return False

def run_blender_to_ue5_workflow():
    """
    BlenderからUE5へのワークフローを実行する
    
    戻り値:
        bool: 成功したかどうか
    """
    logger.info("BlenderからUE5へのアセット転送ワークフローを実行します...")
    
    try:
        # blender_to_ue5_asset.pyスクリプトを実行
        command = [PYTHON_CMD, 'blender_to_ue5_asset.py']
        logger.info(f"コマンドを実行: {' '.join(command)}")
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info("ワークフローは正常に完了しました")
            logger.info(f"出力:\n{result.stdout}")
            return True
        else:
            logger.error(f"ワークフロー実行中にエラーが発生しました: {result.stderr}")
            return False
    except Exception as e:
        logger.exception(f"ワークフロー実行中に例外が発生しました: {str(e)}")
        return False

def run_simple_game_workflow():
    """
    シンプルなゲーム作成ワークフローを実行する
    
    戻り値:
        bool: 成功したかどうか
    """
    logger.info("シンプルなゲーム作成ワークフローを実行します...")
    
    try:
        # simple_ue5_game.pyスクリプトを実行
        command = [PYTHON_CMD, 'simple_ue5_game.py']
        logger.info(f"コマンドを実行: {' '.join(command)}")
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info("ワークフローは正常に完了しました")
            logger.info(f"出力:\n{result.stdout}")
            return True
        else:
            logger.error(f"ワークフロー実行中にエラーが発生しました: {result.stderr}")
            return False
    except Exception as e:
        logger.exception(f"ワークフロー実行中に例外が発生しました: {str(e)}")
        return False

def run_ai_assistant_workflow():
    """
    AI駆動UE5ゲーム開発アシスタントを実行する
    
    戻り値:
        bool: 成功したかどうか
    """
    logger.info("AI駆動UE5ゲーム開発アシスタントを起動します...")
    
    try:
        # ai_ue5_assistant.pyスクリプトを実行（対話モードのため、直接実行して制御を移す）
        command = [PYTHON_CMD, 'ai_ue5_assistant.py']
        logger.info(f"コマンドを実行: {' '.join(command)}")
        
        # サブプロセスを直接実行（制御を移す）
        return subprocess.call(command) == 0
    except Exception as e:
        logger.exception(f"AIアシスタント実行中に例外が発生しました: {str(e)}")
        return False

def run_on_blender(script_path):
    """
    指定されたスクリプトをBlenderで実行する
    
    引数:
        script_path (str): 実行するスクリプトのパス
        
    戻り値:
        bool: 成功したかどうか
    """
    logger.info(f"Blenderで{script_path}を実行します...")
    
    try:
        # Blenderのパスを取得
        blender_path = os.environ.get('BLENDER_PATH')
        if not blender_path:
            blender_path = "/Applications/Blender.app/Contents/MacOS/Blender" if IS_MAC else "blender"
        
        # Blenderを起動し、スクリプトを実行
        command = [blender_path, "--background", "--python", script_path]
        logger.info(f"コマンドを実行: {' '.join(command)}")
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info("Blenderスクリプトは正常に完了しました")
            logger.info(f"出力:\n{result.stdout}")
            return True
        else:
            logger.error(f"Blenderスクリプト実行中にエラーが発生しました: {result.stderr}")
            return False
    except Exception as e:
        logger.exception(f"Blenderスクリプト実行中に例外が発生しました: {str(e)}")
        return False

def run_on_ue5(script_path):
    """
    指定されたスクリプトをUE5で実行する
    
    引数:
        script_path (str): 実行するスクリプトのパス
        
    戻り値:
        bool: 成功したかどうか
    """
    logger.info(f"UE5で{script_path}を実行します...")
    
    try:
        # UE5のパスを取得
        ue5_path = os.environ.get('UE5_PATH')
        if not ue5_path:
            ue5_path = "/Applications/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" if IS_MAC else "UnrealEditor"
        
        # プロジェクトパスを指定（適切なプロジェクトパスに変更する必要があります）
        project_path = os.path.join(os.getcwd(), "MyProject", "MyProject.uproject")
        
        # UE5を起動し、スクリプトを実行
        command = [ue5_path, project_path, "-ExecutePythonScript", script_path]
        logger.info(f"コマンドを実行: {' '.join(command)}")
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info("UE5スクリプトは正常に完了しました")
            logger.info(f"出力:\n{result.stdout}")
            return True
        else:
            logger.error(f"UE5スクリプト実行中にエラーが発生しました: {result.stderr}")
            return False
    except Exception as e:
        logger.exception(f"UE5スクリプト実行中に例外が発生しました: {str(e)}")
        return False

def check_openai_api_key():
    """
    OpenAI APIキーが設定されているかを確認する
    
    戻り値:
        bool: 設定されているかどうか
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.error("OpenAI APIキーが設定されていません。.envファイルにOPENAI_API_KEYを設定してください。")
        return False
    
    # キーの形式を簡易的にチェック
    if not api_key.startswith('sk-'):
        logger.warning("OpenAI APIキーの形式が不正な可能性があります。'sk-'で始まる文字列であるべきです。")
    
    logger.info("OpenAI APIキーが設定されています")
    return True

def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(description='MCPワークフロー実行ツール')
    parser.add_argument('workflow', nargs='?', default='simple_game',
                        choices=['blender_to_ue5', 'simple_game', 'ai_assistant'],
                        help='実行するワークフロー（blender_to_ue5, simple_game, ai_assistant）')
    parser.add_argument('--blender', action='store_true',
                        help='スクリプトをBlender内で実行する')
    parser.add_argument('--ue5', action='store_true',
                        help='スクリプトをUE5内で実行する')
    args = parser.parse_args()
    
    # OpenAI APIキーのチェック
    if not check_openai_api_key():
        return 1
    
    # MCPサーバーの起動確認
    if not ensure_mcp_server_running():
        logger.error("MCPサーバーの起動に失敗しました。先に別ターミナルで `python run_mcp.py all` を実行してください。")
        return 1
    
    # ワークフロー実行前のメッセージ
    logger.info(f"'{args.workflow}' ワークフローを実行します...")
    
    # ワークフロー実行
    success = False
    
    if args.workflow == 'blender_to_ue5':
        if args.blender:
            success = run_on_blender('blender_integration.py')
        else:
            success = run_blender_to_ue5_workflow()
    
    elif args.workflow == 'simple_game':
        if args.ue5:
            success = run_on_ue5('ue5_integration.py')
        else:
            success = run_simple_game_workflow()
    
    elif args.workflow == 'ai_assistant':
        success = run_ai_assistant_workflow()
    
    # 実行結果を表示
    if success:
        logger.info(f"{args.workflow} ワークフローは正常に完了しました")
        return 0
    else:
        logger.error(f"{args.workflow} ワークフローの実行中にエラーが発生しました")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました")
        
        # 起動したプロセスを全て停止
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        
        sys.exit(1)
    except Exception as e:
        logger.exception(f"予期しないエラーが発生しました: {str(e)}")
        sys.exit(1) 
