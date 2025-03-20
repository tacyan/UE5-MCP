#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5接続シミュレーションテストスクリプト

このスクリプトは、UE5が実際にインストールされていない環境でも、
UE5-MCPクライアントとMCPサーバーの接続をシミュレートして確認するためのものです。

モック版のunrealモジュールを定義し、UE5クライアントコードをテストします。
"""

import requests
import json
import logging
import os
import time
import sys

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_ue5_connection")

# モックunrealモジュールを定義
class MockUnreal:
    """
    モックUnrealモジュール
    
    UE5 Python APIをシミュレートするクラス
    """
    
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

# UE5MCPクライアントをインポート
from ue5_mcp_client import UE5MCPClient, connect_to_mcp

def test_connection():
    """
    MCP接続テスト
    """
    logger.info("=== UE5-MCP接続テスト開始 ===")
    
    # connect_to_mcp関数を呼び出し
    client = connect_to_mcp()
    
    # AI生成をテスト
    logger.info("AIを使ってアイテム生成を実行")
    ai_result = client.generate_ai_content(
        "RPGゲーム用の魔法の剣のアイデアを考えて下さい", 
        "item_description"
    )
    logger.info(f"AI生成結果: {json.dumps(ai_result, indent=2, ensure_ascii=False)}")
    
    # Blueprintの生成をテスト
    logger.info("AIを使ったBlueprint生成を実行")
    bp_result = client.generate_blueprint_from_ai(
        "MagicSword", 
        "Actor", 
        "剣を振ると炎が放射され、敵にダメージを与えるマジックソード"
    )
    logger.info(f"Blueprint生成結果: {json.dumps(bp_result, indent=2, ensure_ascii=False)}")
    
    logger.info("=== UE5-MCP接続テスト完了 ===")
    return client

if __name__ == "__main__":
    test_connection() 
