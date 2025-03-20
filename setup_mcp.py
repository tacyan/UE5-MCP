#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP環境セットアップスクリプト

このスクリプトはMCPフレームワークの初期セットアップを行います。
mcp_settings.jsonの作成、必要なディレクトリの作成、環境変数の設定などを自動化します。

使用方法:
python setup_mcp.py [--blender-path PATH] [--ue-path PATH] [--openai-key KEY]
"""

import os
import sys
import json
import argparse
import platform
import shutil
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("setup_mcp")

def detect_blender_path():
    """
    Blenderの実行ファイルパスを検出する
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        common_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            str(Path.home() / "Applications/Blender.app/Contents/MacOS/Blender")
        ]
    elif system == "Windows":
        common_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
        ]
    else:  # Linux
        common_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender"
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Blenderパスを自動検出しました: {path}")
            return path
    
    logger.warning("Blenderパスを自動検出できませんでした")
    return ""

def detect_unreal_path():
    """
    Unreal Engineの実行ファイルパスを検出する
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        common_paths = [
            "/Applications/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
            "/Applications/Epic Games/UE_5.4/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
            "/Applications/Epic Games/UE_5.3/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
            "/Applications/Epic Games/UE_5.2/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
            "/Applications/Epic Games/UE_5.1/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
        ]
    elif system == "Windows":
        common_paths = [
            r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe",
            r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor.exe",
            r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor.exe",
            r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor.exe",
            r"C:\Program Files\Epic Games\UE_5.1\Engine\Binaries\Win64\UnrealEditor.exe"
        ]
    else:  # Linux
        common_paths = [
            "/opt/unreal-engine/Engine/Binaries/Linux/UnrealEditor"
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Unreal Engineパスを自動検出しました: {path}")
            return path
    
    logger.warning("Unreal Engineパスを自動検出できませんでした")
    return ""

def create_default_project_structure():
    """
    プロジェクトの基本ディレクトリ構造を作成する
    """
    directories = [
        "exports",
        "imports",
        "assets",
        "temp",
        "logs",
        "blender_scripts"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"ディレクトリを作成しました: {directory}")

def create_settings_file(blender_path, ue_path, openai_key):
    """
    設定ファイルを作成する
    
    引数:
        blender_path (str): Blenderのパス
        ue_path (str): Unreal Engineのパス
        openai_key (str): OpenAI APIキー
    """
    example_path = "mcp_settings.json.example"
    settings_path = "mcp_settings.json"
    
    # 既存の設定ファイルがあればバックアップ
    if os.path.exists(settings_path):
        backup_path = f"{settings_path}.backup"
        shutil.copy2(settings_path, backup_path)
        logger.info(f"既存の設定ファイルをバックアップしました: {backup_path}")
    
    # 設定テンプレートを読み込み
    if os.path.exists(example_path):
        with open(example_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        # テンプレートがない場合、デフォルト設定を作成
        settings = {
            "server": {
                "host": "127.0.0.1",
                "port": 8000,
                "debug": False
            },
            "ai": {
                "provider": "openai",
                "model": "gpt-4.5",
                "api_key": "",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "blender": {
                "enabled": True,
                "path": "",
                "port": 8001,
                "python_path": "",
                "export_dir": "./exports",
                "script_dir": "./blender_scripts"
            },
            "unreal": {
                "enabled": True,
                "path": "",
                "port": 8002,
                "project_path": "./MyProject/MyProject.uproject",
                "import_dir": "./imports",
                "python_path": ""
            },
            "paths": {
                "assets": "./assets",
                "temp": "./temp",
                "logs": "./logs"
            }
        }
    
    # 検出されたパスを設定
    if blender_path:
        settings["blender"]["path"] = blender_path
    
    if ue_path:
        settings["unreal"]["path"] = ue_path
    
    if openai_key:
        settings["ai"]["api_key"] = openai_key
    
    # 設定を保存
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    
    logger.info(f"設定ファイルを作成しました: {settings_path}")
    
    # OpenAI APIキーが設定されていない場合は警告
    if not settings["ai"]["api_key"]:
        logger.warning("OpenAI APIキーが設定されていません。mcp_settings.jsonを編集して設定してください。")

def create_env_file(openai_key):
    """
    .env ファイルを作成する
    
    引数:
        openai_key (str): OpenAI APIキー
    """
    env_path = ".env"
    
    # 既存の.envファイルがあればバックアップ
    if os.path.exists(env_path):
        backup_path = f"{env_path}.backup"
        shutil.copy2(env_path, backup_path)
        logger.info(f"既存の.envファイルをバックアップしました: {backup_path}")
    
    # .envファイルを作成
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# MCP環境変数設定ファイル\n")
        f.write("# このファイルは.envとして保存され、MCPシステムの設定を管理します\n\n")
        
        f.write("# OpenAI API設定\n")
        f.write(f"OPENAI_API_KEY={openai_key}\n\n")
        
        f.write("# サーバー設定\n")
        f.write("MCP_SERVER_HOST=127.0.0.1\n")
        f.write("MCP_SERVER_PORT=8000\n")
        f.write("DEBUG=false\n\n")
        
        f.write("# Blender設定\n")
        f.write("BLENDER_ENABLED=true\n")
        f.write("BLENDER_PORT=8001\n")
        blender_path = detect_blender_path()
        f.write(f"BLENDER_PATH={blender_path}\n\n")
        
        f.write("# UE5設定\n")
        f.write("UE5_ENABLED=true\n")
        f.write("UE5_PORT=8002\n")
        ue_path = detect_unreal_path()
        f.write(f"UE5_PATH={ue_path}\n")
    
    logger.info(f".envファイルを作成しました: {env_path}")
    
    # OpenAI APIキーが設定されていない場合は警告
    if not openai_key:
        logger.warning("OpenAI APIキーが設定されていません。.envファイルを編集して設定してください。")

def create_quick_start_guide():
    """
    クイックスタートガイドを作成する
    """
    guide_path = "QUICK_START.md"
    
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write("# MCP フレームワーク クイックスタートガイド\n\n")
        
        f.write("## 1. 環境設定\n\n")
        f.write("このフレームワークを使用するには、以下の準備が必要です：\n\n")
        f.write("- Python 3.8以上\n")
        f.write("- Blender 4.0以上（オプション、Blender連携を使用する場合）\n")
        f.write("- Unreal Engine 5.1以上（オプション、UE5連携を使用する場合）\n")
        f.write("- OpenAI APIキー（AI機能を使用する場合）\n\n")
        
        f.write("## 2. セットアップ\n\n")
        f.write("1. 依存関係をインストールします：\n\n")
        f.write("```bash\npip install -r requirements.txt\n```\n\n")
        
        f.write("2. 設定ファイルを編集します：\n\n")
        f.write("```bash\n# 設定を自動生成（パスを自動検出）\npython setup_mcp.py\n\n")
        f.write("# または、パスを指定して生成\npython setup_mcp.py --blender-path /path/to/blender --ue-path /path/to/unrealEditor --openai-key YOUR_API_KEY\n```\n\n")
        
        f.write("3. `mcp_settings.json` ファイルを確認し、必要に応じて調整してください。\n\n")
        
        f.write("## 3. MCPサーバーの起動\n\n")
        f.write("```bash\npython run_mcp.py all\n```\n\n")
        
        f.write("## 4. 使用例\n\n")
        
        f.write("### BlenderからUE5へのアセット転送\n\n")
        f.write("```bash\npython run_mcp_workflow.py blender_to_ue5\n```\n\n")
        
        f.write("### トレジャーハントゲームの作成\n\n")
        f.write("```bash\npython run_mcp_workflow.py treasure_hunt\n```\n\n")
        
        f.write("### ロボットゲームの作成\n\n")
        f.write("```bash\npython run_mcp_workflow.py robot_game\n```\n\n")
        
        f.write("### AIアシスタントの起動\n\n")
        f.write("```bash\npython run_mcp_workflow.py ai_assistant\n```\n\n")
        
        f.write("## 5. 自然言語によるゲーム開発\n\n")
        f.write("AIアシスタントを使用することで、自然言語を使ったゲーム開発が可能です：\n\n")
        f.write("1. AIアシスタントを起動します：\n\n")
        f.write("```bash\npython ai_ue5_assistant.py\n```\n\n")
        
        f.write("2. 例えば、以下のような指示を英語または日本語で入力できます：\n\n")
        f.write("- 「シンプルな3Dプラットフォーマーゲームを作成して」\n")
        f.write("- 「剣と盾を持った騎士のキャラクターモデルを作成して」\n")
        f.write("- 「自動生成された地形に木と岩を配置して」\n\n")
        
        f.write("## 6. 詳細ドキュメント\n\n")
        f.write("詳細な使用方法とAPIリファレンスについては、`docs/` ディレクトリ内のドキュメントを参照してください。\n")
    
    logger.info(f"クイックスタートガイドを作成しました: {guide_path}")

def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(description="MCP環境セットアップツール")
    parser.add_argument("--blender-path", help="Blenderの実行ファイルパス")
    parser.add_argument("--ue-path", help="Unreal Engineの実行ファイルパス")
    parser.add_argument("--openai-key", help="OpenAI APIキー")
    
    args = parser.parse_args()
    
    print("\n===== MCP環境セットアップ =====\n")
    
    # コマンドラインで指定されていない場合は自動検出
    blender_path = args.blender_path or detect_blender_path()
    ue_path = args.ue_path or detect_unreal_path()
    openai_key = args.openai_key or ""
    
    # ディレクトリ構造を作成
    create_default_project_structure()
    
    # 設定ファイルを作成
    create_settings_file(blender_path, ue_path, openai_key)
    
    # .envファイルを作成
    create_env_file(openai_key)
    
    # クイックスタートガイドを作成
    create_quick_start_guide()
    
    print("\n===== セットアップ完了 =====\n")
    print("次のステップ:")
    print("1. mcp_settings.json を確認し、必要に応じて編集してください")
    print("2. OpenAI APIキーが設定されていない場合は、mcp_settings.json または .env ファイルに設定してください")
    print("3. サーバーを起動: python run_mcp.py all")
    print("4. 詳細はQUICK_START.mdを参照してください")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
