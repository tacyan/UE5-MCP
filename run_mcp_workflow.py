#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP連携ワークフロー実行スクリプト

このスクリプトは、MCPフレームワークを使用してBlenderとUE5を連携させ、
様々なワークフローを実行します。コマンドライン引数によって異なる
ワークフローを選択できます。

主なワークフロー:
- blender_to_ue5: BlenderからUE5へのアセット転送
- treasure_hunt: トレジャーハントゲームの作成
- robot_game: ロボットゲームの作成

使用方法:
python run_mcp_workflow.py <ワークフロー名> [--blender] [--ue5]

オプション:
--blender: Blenderでスクリプトを実行する
--ue5: UE5でスクリプトを実行する
"""

import os
import sys
import logging
import argparse
import time
import subprocess

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_workflow")

def is_mcp_server_running():
    """
    MCPサーバーが実行中かどうかをチェックする
    
    戻り値:
        bool: サーバーが実行中ならTrue、そうでなければFalse
    """
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "running"
        return False
    except:
        return False

def start_mcp_server():
    """
    MCPサーバーを起動する
    """
    logger.info("MCPサーバーを起動しています...")
    
    # すでに実行中の場合は何もしない
    if is_mcp_server_running():
        logger.info("MCPサーバーはすでに実行中です")
        return True
    
    try:
        # バックグラウンドでサーバーを起動
        process = subprocess.Popen(
            ["python", "run_mcp.py", "all"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # サーバーの起動を待つ
        for _ in range(10):  # 最大10秒間待機
            time.sleep(1)
            if is_mcp_server_running():
                logger.info("MCPサーバーが正常に起動しました")
                return True
        
        logger.error("MCPサーバーの起動がタイムアウトしました")
        return False
    except Exception as e:
        logger.error(f"MCPサーバーの起動中にエラーが発生しました: {str(e)}")
        return False

def run_blender_direct_script():
    """
    Blenderでゲームオブジェクト作成スクリプトを実行する
    """
    logger.info("Blenderでゲームオブジェクト作成スクリプトを実行...")
    
    try:
        # 環境変数から取得したBlenderパス
        blender_path = os.environ.get("BLENDER_PATH", "blender")
        
        # スクリプトをBlenderで実行
        process = subprocess.Popen(
            [blender_path, "--background", "--python", "blender_direct_script.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("Blenderスクリプトが正常に完了しました")
            logger.debug(stdout.decode())
            return True
        else:
            logger.error(f"Blenderスクリプトの実行中にエラーが発生しました: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Blenderスクリプト実行中に例外が発生しました: {str(e)}")
        return False

def run_ue5_treasure_game():
    """
    UE5でトレジャーハントゲームを作成する
    """
    logger.info("UE5でトレジャーハントゲームを作成...")
    
    try:
        # スクリプトを実行
        process = subprocess.Popen(
            ["python", "ue5_treasure_game.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("UE5ゲーム作成スクリプトが正常に完了しました")
            return True
        else:
            logger.error(f"UE5ゲーム作成中にエラーが発生しました: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"UE5ゲーム作成中に例外が発生しました: {str(e)}")
        return False

def run_robot_game():
    """
    ロボットゲームを作成する
    """
    logger.info("ロボットゲームを作成...")
    
    try:
        # スクリプトを実行
        process = subprocess.Popen(
            ["python", "create_player_character.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("ロボットゲーム作成スクリプトが正常に完了しました")
            return True
        else:
            logger.error(f"ロボットゲーム作成中にエラーが発生しました: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"ロボットゲーム作成中に例外が発生しました: {str(e)}")
        return False

def run_ai_assistant():
    """
    AIアシスタントを実行する
    """
    logger.info("AIアシスタントを起動...")
    
    try:
        # スクリプトを実行
        process = subprocess.Popen(
            ["python", "ai_ue5_assistant.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("AIアシスタントが正常に完了しました")
            return True
        else:
            logger.error(f"AIアシスタント実行中にエラーが発生しました: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"AIアシスタント実行中に例外が発生しました: {str(e)}")
        return False

def run_ue5_standalone(workflow_name):
    """
    UE5単独でワークフローを実行する
    
    引数:
        workflow_name (str): 実行するワークフロー名
    """
    logger.info(f"UE5内でワークフロー '{workflow_name}' を実行...")
    
    try:
        # 環境変数から取得したUE5エディタパス
        ue5_path = os.environ.get("UE5_PATH", "UnrealEditor")
        
        # UE5プロジェクトパス（実際の環境に合わせて調整が必要）
        ue5_project = os.environ.get("UE5_PROJECT", "./MyProject/MyProject.uproject")
        
        # Python スクリプトパス
        if workflow_name == "treasure_hunt":
            script_path = os.path.abspath("ue5_treasure_game.py")
        elif workflow_name == "robot_game":
            script_path = os.path.abspath("create_player_character.py")
        else:
            logger.error(f"未知のワークフロー: {workflow_name}")
            return False
        
        # UE5エディタでスクリプトを実行
        cmd = [
            ue5_path,
            ue5_project,
            "-ExecutePythonScript=" + script_path
        ]
        
        logger.info(f"コマンド実行: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # この場合は非同期で実行するため、プロセスを待機しない
        logger.info("UE5エディタを起動しました。スクリプトはエディタ内で実行されます。")
        return True
    except Exception as e:
        logger.error(f"UE5実行中に例外が発生しました: {str(e)}")
        return False

def run_blender_standalone(workflow_name):
    """
    Blender単独でワークフローを実行する
    
    引数:
        workflow_name (str): 実行するワークフロー名
    """
    logger.info(f"Blender内でワークフロー '{workflow_name}' を実行...")
    
    try:
        # 環境変数から取得したBlenderパス
        blender_path = os.environ.get("BLENDER_PATH", "blender")
        
        # スクリプトパス
        if workflow_name == "blender_to_ue5":
            script_path = os.path.abspath("blender_direct_script.py")
        else:
            logger.error(f"未知のワークフロー: {workflow_name}")
            return False
        
        # Blenderを起動してスクリプトを実行
        cmd = [
            blender_path,
            "-P", script_path
        ]
        
        logger.info(f"コマンド実行: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # この場合は非同期で実行するため、プロセスを待機しない
        logger.info("Blenderを起動しました。スクリプトはBlender内で実行されます。")
        return True
    except Exception as e:
        logger.error(f"Blender実行中に例外が発生しました: {str(e)}")
        return False

def run_blender_to_ue5_workflow():
    """
    BlenderからUE5へのアセット転送ワークフローを実行する
    """
    logger.info("=== BlenderからUE5へのアセット転送ワークフロー開始 ===")
    
    # 1. MCPサーバーが実行中か確認し、必要なら起動
    if not start_mcp_server():
        logger.error("MCPサーバーが起動できませんでした。処理を中止します。")
        return False
    
    # 2. Blenderでゲームオブジェクト作成
    if not run_blender_direct_script():
        logger.error("Blenderスクリプトの実行に失敗しました。処理を中止します。")
        return False
    
    # 3. UE5でトレジャーハントゲーム作成
    if not run_ue5_treasure_game():
        logger.error("UE5ゲーム作成に失敗しました。")
        return False
    
    logger.info("=== BlenderからUE5へのアセット転送ワークフロー完了 ===")
    return True

def run_treasure_hunt_workflow():
    """
    トレジャーハントゲーム作成ワークフローを実行する
    """
    logger.info("=== トレジャーハントゲーム作成ワークフロー開始 ===")
    
    # 1. MCPサーバーが実行中か確認し、必要なら起動
    if not start_mcp_server():
        logger.error("MCPサーバーが起動できませんでした。処理を中止します。")
        return False
    
    # 2. UE5でトレジャーハントゲーム作成
    if not run_ue5_treasure_game():
        logger.error("UE5ゲーム作成に失敗しました。")
        return False
    
    logger.info("=== トレジャーハントゲーム作成ワークフロー完了 ===")
    return True

def run_robot_game_workflow():
    """
    ロボットゲーム作成ワークフローを実行する
    """
    logger.info("=== ロボットゲーム作成ワークフロー開始 ===")
    
    # 1. MCPサーバーが実行中か確認し、必要なら起動
    if not start_mcp_server():
        logger.error("MCPサーバーが起動できませんでした。処理を中止します。")
        return False
    
    # 2. ロボットゲーム作成
    if not run_robot_game():
        logger.error("ロボットゲーム作成に失敗しました。")
        return False
    
    logger.info("=== ロボットゲーム作成ワークフロー完了 ===")
    return True

def run_ai_assistant_workflow():
    """
    AIアシスタントワークフローを実行する
    """
    logger.info("=== AIアシスタントワークフロー開始 ===")
    
    # 1. MCPサーバーが実行中か確認し、必要なら起動
    if not start_mcp_server():
        logger.error("MCPサーバーが起動できませんでした。処理を中止します。")
        return False
    
    # 2. AIアシスタント実行
    if not run_ai_assistant():
        logger.error("AIアシスタント実行に失敗しました。")
        return False
    
    logger.info("=== AIアシスタントワークフロー完了 ===")
    return True

def main():
    """
    メイン関数
    """
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(description="MCPワークフロー実行スクリプト")
    parser.add_argument("workflow", choices=["blender_to_ue5", "treasure_hunt", "robot_game", "ai_assistant"],
                       help="実行するワークフロー名")
    parser.add_argument("--blender", action="store_true", help="Blenderでスクリプトを実行する")
    parser.add_argument("--ue5", action="store_true", help="UE5でスクリプトを実行する")
    
    args = parser.parse_args()
    
    try:
        # Blenderモードでの実行
        if args.blender:
            return run_blender_standalone(args.workflow)
        
        # UE5モードでの実行
        if args.ue5:
            return run_ue5_standalone(args.workflow)
        
        # 通常実行
        if args.workflow == "blender_to_ue5":
            return run_blender_to_ue5_workflow()
        elif args.workflow == "treasure_hunt":
            return run_treasure_hunt_workflow()
        elif args.workflow == "robot_game":
            return run_robot_game_workflow()
        elif args.workflow == "ai_assistant":
            return run_ai_assistant_workflow()
        else:
            logger.error(f"未知のワークフロー: {args.workflow}")
            return False
    except Exception as e:
        logger.exception(f"ワークフロー実行中に予期しないエラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 
