#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI駆動UE5ゲーム開発アシスタント

このスクリプトは、自然言語コマンドを解釈してUnreal Engine 5の
機能を実行するAI駆動のゲーム開発支援ツールです。

主な機能:
- 自然言語コマンドの解釈とUE5コマンドへの変換
- コンテキストに応じたアセット生成と配置
- AI駆動のBlueprintロジック生成
- ゲームデザイン支援機能

使用例:
    - "山と森のある大きなオープンワールドの地形を生成して"
    - "プレイヤーが近づくと爆発する赤い樽を作成して"
    - "ジャンプ力が2倍になるパワーアップアイテムを実装して"

使用方法:
    python ai_ue5_assistant.py
    > コマンドを入力してください: 

制限事項:
- MCPサーバーが起動している必要があります
- 自然言語解析には、設定済みのOpenAI APIキーが必要です
"""

import json
import logging
import time
import sys
import os
import readline  # 入力履歴とコマンド編集のサポート用

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_ue5_assistant.log"),
        logging.StreamHandler(sys.stderr)  # コンソール出力とプロンプトが混在しないようにstderrに出力
    ]
)
logger = logging.getLogger("ai_ue5_assistant")

# UE5クライアントのモック化の準備
try:
    # UE5のモックモジュール
    if 'unreal' not in sys.modules:
        class MockUnreal:
            class SystemLibrary:
                @staticmethod
                def get_engine_version():
                    return "5.3.0 (モックバージョン)"
            
            class LinearColor:
                def __init__(self, r, g, b, a):
                    self.r = r
                    self.g = g
                    self.b = b
                    self.a = a
            
            class EditorNotificationController:
                def __init__(self):
                    self.notification_style = self.NotificationStyle()
                
                class NotificationStyle:
                    def __init__(self):
                        self.fade_in_duration = 0.5
                        self.fade_out_duration = 0.5
                        self.expire_duration = 5.0
                        self.text_color = None
                
                def display_notification(self, message, style):
                    logger.info(f"UE5通知: {message}")
            
            @staticmethod
            def log(message):
                logger.info(f"UE5ログ: {message}")

        # モックunrealモジュールをシステムに追加
        sys.modules['unreal'] = MockUnreal()
    
    # 必要なモジュールのインポート
    from ue5_mcp_client import UE5MCPClient, connect_to_mcp
    import requests
except ImportError as e:
    logger.error(f"必要なモジュールのインポートに失敗しました: {str(e)}")
    sys.exit(1)

class AIUE5Assistant:
    """
    AI駆動UE5アシスタントクラス
    """
    
    def __init__(self):
        """
        初期化メソッド
        """
        # UE5 MCPクライアントを作成
        self.client = None
        
        # コマンド履歴
        self.command_history = []
        
        # 利用可能なコマンドマッピング
        self.available_commands = {
            "create_level": "新しいレベルを作成します",
            "generate_terrain": "地形を生成します",
            "create_blueprint": "Blueprintを作成します",
            "import_asset": "アセットをインポートします",
            "place_foliage": "植生を配置します",
            "build_lighting": "ライティングをビルドします",
            "place_asset": "アセットを配置します"
        }
    
    def connect(self):
        """
        MCPサーバーに接続する
        """
        logger.info("MCPサーバーに接続しています...")
        try:
            self.client = connect_to_mcp()
            status = self.client.check_server_status()
            
            if status.get("status") == "running":
                logger.info("MCPサーバーに接続しました")
                print("\n⭐ MCPサーバーに接続しました")
                
                # AIのステータスを確認
                ai_info = status.get("ai", {})
                ai_provider = ai_info.get("provider", "unknown")
                ai_status = ai_info.get("status", "unknown")
                
                if ai_provider == "mock":
                    print("⚠️ AIはモックモードで実行されています。OpenAI APIキーを設定すると、完全な機能が利用できます。")
                else:
                    print(f"✅ AI ({ai_info.get('model', 'unknown')}) は正常に機能しています")
                
                return True
            else:
                logger.error(f"サーバーの状態が異常です: {status}")
                print("❌ MCPサーバーに接続できませんでした。サーバーが実行されていることを確認してください。")
                return False
        except Exception as e:
            logger.exception(f"MCPサーバーへの接続中にエラーが発生しました: {str(e)}")
            print(f"❌ エラー: {str(e)}")
            return False
    
    def parse_natural_language(self, text):
        """
        自然言語コマンドを解析する
        
        引数:
            text (str): 自然言語コマンド
            
        戻り値:
            dict: 解析結果（コマンドとパラメータ）
        """
        # AIを使ってテキストを解析し、UE5コマンドに変換
        logger.info(f"自然言語コマンドを解析: {text}")
        
        try:
            # AIに自然言語を解析してもらう
            ai_result = self.client.generate_ai_content(
                f"以下の自然言語コマンドを解析して、Unreal Engine 5のコマンドとパラメータに変換してください。"
                f"JSONフォーマットで返してください。コマンド: {text}",
                "command_parser"
            )
            
            result_content = ai_result.get("data", {}).get("content", "{}")
            
            # 文字列からJSONを解析
            try:
                parsed_command = json.loads(result_content)
                logger.info(f"解析結果: {json.dumps(parsed_command, ensure_ascii=False)}")
                return parsed_command
            except json.JSONDecodeError:
                # AIからの応答がJSONでない場合、簡易パース
                logger.warning(f"AIからの応答がJSONではありません: {result_content}")
                
                # 簡易的なパーシング（実際の環境では、より堅牢な実装が必要）
                if "地形" in text or "環境" in text:
                    return {
                        "command": "generate_terrain",
                        "params": {
                            "size_x": 8192,
                            "size_y": 8192,
                            "height_variation": "high" if "山" in text else "medium",
                            "terrain_type": "mountainous" if "山" in text else "plains"
                        }
                    }
                elif "レベル" in text or "マップ" in text:
                    return {
                        "command": "create_level",
                        "params": {
                            "name": "GeneratedLevel",
                            "template": "ThirdPerson"
                        }
                    }
                elif "ブループリント" in text or "機能" in text or "アイテム" in text:
                    return {
                        "command": "create_blueprint",
                        "params": {
                            "name": "BP_" + ("Item" if "アイテム" in text else "Actor"),
                            "class": "Actor",
                            "description": text,
                            "ai_generate": True
                        }
                    }
                else:
                    return {
                        "command": "unknown",
                        "params": {
                            "original_text": text
                        }
                    }
        except Exception as e:
            logger.exception(f"コマンド解析中にエラーが発生しました: {str(e)}")
            return {
                "command": "error",
                "params": {
                    "error_message": str(e),
                    "original_text": text
                }
            }
    
    def execute_command(self, parsed_command):
        """
        解析されたコマンドを実行する
        
        引数:
            parsed_command (dict): 解析されたコマンド
            
        戻り値:
            dict: 実行結果
        """
        if not self.client:
            logger.error("MCPサーバーに接続されていません")
            return {"status": "error", "message": "MCPサーバーに接続されていません"}
        
        command = parsed_command.get("command", "")
        params = parsed_command.get("params", {})
        
        logger.info(f"コマンド実行: {command}, パラメータ: {json.dumps(params, ensure_ascii=False)}")
        
        try:
            # コマンドに応じて実行
            if command in self.available_commands:
                result = self.client.execute_unreal_command(command, params)
                logger.info(f"実行結果: {json.dumps(result, ensure_ascii=False)}")
                return result
            elif command == "unknown":
                # 未知のコマンドの場合、AIに生成してもらう
                description = params.get("original_text", "")
                blueprint_result = self.client.generate_blueprint_from_ai(
                    f"BP_Custom_{len(self.command_history)}",
                    "Actor",
                    description
                )
                logger.info(f"Blueprint生成結果: {json.dumps(blueprint_result, ensure_ascii=False)}")
                return {
                    "status": "success",
                    "message": f"指定された機能を実装するBlueprintを生成しました: {description}",
                    "action": "blueprint_creation"
                }
            else:
                logger.warning(f"未知のコマンド: {command}")
                return {"status": "error", "message": f"未知のコマンド: {command}"}
        except Exception as e:
            logger.exception(f"コマンド実行中にエラーが発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_interactive(self):
        """
        対話モードで実行する
        """
        # MCPサーバーに接続
        if not self.connect():
            return
        
        print("\n===== AI駆動UE5ゲーム開発アシスタント =====")
        print("自然言語でUE5コマンドを実行できます。")
        print("'exit'または'quit'と入力すると終了します。")
        print("'help'と入力するとヘルプを表示します。")
        print("============================================\n")
        
        while True:
            try:
                # コマンド入力
                user_input = input("\n> コマンドを入力してください: ").strip()
                
                # 終了コマンド
                if user_input.lower() in ["exit", "quit", "終了"]:
                    print("アシスタントを終了します。")
                    break
                
                # 空のコマンド
                if not user_input:
                    continue
                
                # ヘルプコマンド
                if user_input.lower() in ["help", "ヘルプ", "?"]:
                    self.show_help()
                    continue
                
                # コマンド履歴に追加
                self.command_history.append(user_input)
                
                # コマンドの解析と実行
                print(f"\n🔍 '{user_input}' を解析しています...")
                parsed_command = self.parse_natural_language(user_input)
                
                if parsed_command.get("command") == "error":
                    print(f"❌ エラー: {parsed_command.get('params', {}).get('error_message', '不明なエラー')}")
                    continue
                
                print(f"🚀 コマンド '{parsed_command.get('command')}' を実行しています...")
                result = self.execute_command(parsed_command)
                
                if result.get("status") == "success":
                    print(f"✅ 成功: {result.get('message', '操作が完了しました')}")
                else:
                    print(f"❌ 失敗: {result.get('message', '不明なエラー')}")
                
            except KeyboardInterrupt:
                print("\nキャンセルされました。終了するには 'exit' と入力してください。")
            except Exception as e:
                logger.exception(f"対話モード実行中にエラーが発生しました: {str(e)}")
                print(f"❌ エラー: {str(e)}")
    
    def show_help(self):
        """
        ヘルプを表示する
        """
        print("\n===== ヘルプ =====")
        print("以下のような自然言語コマンドを入力できます:")
        print("- '山と森のある大きなオープンワールドの地形を生成して'")
        print("- '新しいサードパーソンレベルを作成して'")
        print("- 'プレイヤーが近づくと爆発する赤い樽を作成して'")
        print("- 'ジャンプ力が2倍になるパワーアップアイテムを実装して'")
        print("\n利用可能なUE5コマンド:")
        for cmd, desc in self.available_commands.items():
            print(f"- {cmd}: {desc}")
        print("\nその他のコマンド:")
        print("- 'help', 'ヘルプ', '?': このヘルプを表示")
        print("- 'exit', 'quit', '終了': アシスタントを終了")
        print("====================")

if __name__ == "__main__":
    try:
        assistant = AIUE5Assistant()
        assistant.run_interactive()
    except Exception as e:
        logger.exception(f"実行中にエラーが発生しました: {str(e)}")
        print(f"致命的なエラーが発生しました: {str(e)}")
        sys.exit(1) 
