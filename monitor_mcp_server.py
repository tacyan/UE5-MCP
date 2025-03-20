#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPサーバーモニタリングツール

MCPサーバーと通信し、UE5のシミュレーションを行うモニタリングツール。
- サーバーのステータスを確認
- トレジャーハントゲームの構造を可視化
- モデルとオブジェクトの配置を表示

使用法:
  python monitor_mcp_server.py
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, Canvas

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_monitor")

# MCPサーバーURL
MCP_SERVER = f"http://127.0.0.1:8080"

class MCPMonitor:
    """MCPサーバーモニタリングツール"""
    
    def __init__(self, master):
        """初期化"""
        self.master = master
        self.server_url = MCP_SERVER
        
        # ウィンドウ設定
        self.master.title("MCPサーバーモニター")
        self.master.geometry("800x600")
        
        # タブコントロール
        self.tab_control = ttk.Notebook(self.master)
        
        # タブ1: サーバー情報
        self.tab_server = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_server, text="サーバー情報")
        self.create_server_tab()
        
        # タブ2: ゲーム構造
        self.tab_game = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_game, text="ゲーム構造")
        self.create_game_tab()
        
        # タブ3: 3Dビュー
        self.tab_3d = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_3d, text="3Dビュー")
        self.create_3d_tab()
        
        # タブ4: ログ
        self.tab_log = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_log, text="ログ")
        self.create_log_tab()
        
        # タブコントロールを配置
        self.tab_control.pack(expand=1, fill="both")
        
        # 更新ボタン
        refresh_btn = ttk.Button(self.master, text="更新", command=self.refresh_all)
        refresh_btn.pack(pady=10)
        
        # 初期更新
        self.refresh_all()
        
        # 定期更新タイマー（5秒ごと）
        self.master.after(5000, self.periodic_refresh)
    
    def create_server_tab(self):
        """サーバー情報タブの作成"""
        # サーバー情報用フレーム
        frame = ttk.LabelFrame(self.tab_server, text="サーバーステータス")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # サーバー情報用テキストエリア
        self.server_info_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.server_info_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_game_tab(self):
        """ゲーム構造タブの作成"""
        # ゲーム構造用ツリービュー
        self.game_tree = ttk.Treeview(self.tab_game)
        self.game_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ツリービューのスクロールバー
        tree_scroll = ttk.Scrollbar(self.game_tree, orient="vertical", command=self.game_tree.yview)
        self.game_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
    
    def create_3d_tab(self):
        """3Dビュータブの作成"""
        # 3Dビュー用キャンバス
        self.canvas_3d = Canvas(self.tab_3d, bg="black")
        self.canvas_3d.pack(fill="both", expand=True)
        
        # キャンバスにグリッドを表示
        self.draw_grid()
    
    def create_log_tab(self):
        """ログタブの作成"""
        # ログ用テキストエリア
        self.log_text = scrolledtext.ScrolledText(self.tab_log, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ログの初期化
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] MCPモニター起動\n")
    
    def draw_grid(self):
        """3Dビューにグリッドを描画"""
        width = self.canvas_3d.winfo_width() or 800
        height = self.canvas_3d.winfo_height() or 600
        
        # グリッド線の間隔
        grid_size = 50
        
        # キャンバスをクリア
        self.canvas_3d.delete("grid")
        
        # グリッド線の描画（横線）
        for y in range(0, height, grid_size):
            self.canvas_3d.create_line(0, y, width, y, fill="#333333", tags="grid")
        
        # グリッド線の描画（縦線）
        for x in range(0, width, grid_size):
            self.canvas_3d.create_line(x, 0, x, height, fill="#333333", tags="grid")
        
        # 中心線の描画
        self.canvas_3d.create_line(width/2, 0, width/2, height, fill="#555555", width=2, tags="grid")
        self.canvas_3d.create_line(0, height/2, width, height/2, fill="#555555", width=2, tags="grid")
    
    def draw_level_objects(self):
        """レベル内のオブジェクトを描画"""
        width = self.canvas_3d.winfo_width() or 800
        height = self.canvas_3d.winfo_height() or 600
        
        # キャンバスをクリア
        self.canvas_3d.delete("object")
        
        # キャンバスの中心座標
        center_x = width / 2
        center_y = height / 2
        
        # スケールファクター
        scale = 0.2
        
        try:
            # サーバーからレベルデータを取得するモック
            # 実際にはAPIからデータを取得するが、現在はハードコード
            objects = [
                {"type": "TreasureChest", "location": [500, 500, 50], "name": "TreasureChest_1"},
                {"type": "TreasureChest", "location": [-500, 500, 50], "name": "TreasureChest_2"},
                {"type": "TreasureChest", "location": [500, -500, 50], "name": "TreasureChest_3"},
                {"type": "TreasureChest", "location": [-500, -500, 50], "name": "TreasureChest_4"},
                {"type": "Coin", "location": [300, 300, 50], "name": "Coin_1"},
                {"type": "Coin", "location": [-300, 300, 50], "name": "Coin_2"},
                {"type": "Coin", "location": [300, -300, 50], "name": "Coin_3"},
                {"type": "Coin", "location": [-300, -300, 50], "name": "Coin_4"},
                {"type": "Coin", "location": [0, 0, 50], "name": "Coin_5"},
                {"type": "HealthPotion", "location": [200, 200, 50], "name": "HealthPotion_1"},
                {"type": "HealthPotion", "location": [-200, 200, 50], "name": "HealthPotion_2"},
                {"type": "PlayerStart", "location": [0, 0, 100], "name": "PlayerStart"}
            ]
            
            # オブジェクトを描画
            for obj in objects:
                obj_type = obj["type"]
                loc = obj["location"]
                name = obj["name"]
                
                # 座標を変換（UE5座標からキャンバス座標へ）
                # UE5は右手座標系、キャンバスは左上が原点
                x = center_x + loc[0] * scale
                y = center_y - loc[1] * scale  # Y軸は反転
                
                # オブジェクトタイプごとに描画方法を変える
                if obj_type == "TreasureChest":
                    # 宝箱は赤い四角形
                    size = 15
                    self.canvas_3d.create_rectangle(
                        x - size, y - size, x + size, y + size,
                        fill="red", outline="darkred", tags=("object", name)
                    )
                elif obj_type == "Coin":
                    # コインは黄色い円
                    size = 10
                    self.canvas_3d.create_oval(
                        x - size, y - size, x + size, y + size,
                        fill="gold", outline="darkgoldenrod", tags=("object", name)
                    )
                elif obj_type == "HealthPotion":
                    # ポーションは青い三角形
                    size = 12
                    self.canvas_3d.create_polygon(
                        x, y - size, x + size, y + size, x - size, y + size,
                        fill="blue", outline="darkblue", tags=("object", name)
                    )
                elif obj_type == "PlayerStart":
                    # プレイヤースタートは緑の星形
                    size = 15
                    self.canvas_3d.create_polygon(
                        x, y - size,
                        x + size/2, y - size/3,
                        x + size, y,
                        x + size/2, y + size/3,
                        x, y + size,
                        x - size/2, y + size/3,
                        x - size, y,
                        x - size/2, y - size/3,
                        fill="green", outline="darkgreen", tags=("object", name)
                    )
                
                # オブジェクト名を表示
                self.canvas_3d.create_text(
                    x, y + 20, text=name, fill="white", tags=("object", "label")
                )
        
        except Exception as e:
            logger.error(f"オブジェクト描画エラー: {str(e)}")
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] オブジェクト描画エラー: {str(e)}\n")
            self.log_text.see(tk.END)
    
    def refresh_server_info(self):
        """サーバー情報を更新"""
        try:
            response = requests.get(f"{self.server_url}/api/status")
            if response.status_code == 200:
                server_data = response.json()
                
                # テキストエリアをクリア
                self.server_info_text.delete(1.0, tk.END)
                
                # サーバー情報を表示
                self.server_info_text.insert(tk.END, "MCPサーバー情報\n")
                self.server_info_text.insert(tk.END, "----------------\n\n")
                self.server_info_text.insert(tk.END, f"ステータス: {server_data.get('status', 'unknown')}\n")
                self.server_info_text.insert(tk.END, f"バージョン: {server_data.get('version', 'unknown')}\n\n")
                
                system_info = server_data.get("system", {})
                self.server_info_text.insert(tk.END, "システム情報:\n")
                self.server_info_text.insert(tk.END, f"  OS: {system_info.get('os', 'unknown')}\n")
                self.server_info_text.insert(tk.END, f"  プラットフォーム: {system_info.get('platform', 'unknown')}\n")
                self.server_info_text.insert(tk.END, f"  Python: {system_info.get('python', 'unknown')}\n\n")
                
                ai_info = server_data.get("ai", {})
                self.server_info_text.insert(tk.END, "AI情報:\n")
                self.server_info_text.insert(tk.END, f"  プロバイダー: {ai_info.get('provider', 'unknown')}\n")
                self.server_info_text.insert(tk.END, f"  モデル: {ai_info.get('model', 'unknown')}\n")
                self.server_info_text.insert(tk.END, f"  ステータス: {ai_info.get('status', 'unknown')}\n\n")
                
                blender_info = server_data.get("blender", {})
                self.server_info_text.insert(tk.END, "Blender情報:\n")
                self.server_info_text.insert(tk.END, f"  有効: {blender_info.get('enabled', False)}\n")
                self.server_info_text.insert(tk.END, f"  ステータス: {blender_info.get('status', 'unknown')}\n\n")
                
                unreal_info = server_data.get("unreal", {})
                self.server_info_text.insert(tk.END, "Unreal Engine情報:\n")
                self.server_info_text.insert(tk.END, f"  有効: {unreal_info.get('enabled', False)}\n")
                self.server_info_text.insert(tk.END, f"  ステータス: {unreal_info.get('status', 'unknown')}\n")
                
                # ログに記録
                self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] サーバー情報を更新しました\n")
                self.log_text.see(tk.END)
            else:
                self.server_info_text.delete(1.0, tk.END)
                self.server_info_text.insert(tk.END, f"サーバー接続エラー: HTTP {response.status_code}")
                
                # ログに記録
                self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] サーバー接続エラー: HTTP {response.status_code}\n")
                self.log_text.see(tk.END)
        except Exception as e:
            self.server_info_text.delete(1.0, tk.END)
            self.server_info_text.insert(tk.END, f"サーバー接続例外: {str(e)}")
            
            # ログに記録
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] サーバー接続例外: {str(e)}\n")
            self.log_text.see(tk.END)
    
    def refresh_game_tree(self):
        """ゲーム構造ツリーを更新"""
        try:
            # ツリービューをクリア
            for item in self.game_tree.get_children():
                self.game_tree.delete(item)
            
            # ルートノード
            game_root = self.game_tree.insert("", "end", text="トレジャーハントゲーム", open=True)
            
            # アセットノード
            assets_node = self.game_tree.insert(game_root, "end", text="アセット", open=True)
            self.game_tree.insert(assets_node, "end", text="TreasureChest.fbx")
            self.game_tree.insert(assets_node, "end", text="Coin.fbx")
            self.game_tree.insert(assets_node, "end", text="HealthPotion.fbx")
            
            # ブループリントノード
            blueprints_node = self.game_tree.insert(game_root, "end", text="ブループリント", open=True)
            self.game_tree.insert(blueprints_node, "end", text="BP_TreasureChest (Actor)")
            self.game_tree.insert(blueprints_node, "end", text="BP_Coin (Actor)")
            self.game_tree.insert(blueprints_node, "end", text="BP_HealthPotion (Actor)")
            self.game_tree.insert(blueprints_node, "end", text="BP_TreasureGameMode (GameModeBase)")
            
            # レベルノード
            level_node = self.game_tree.insert(game_root, "end", text="レベル", open=True)
            treasureHuntMap = self.game_tree.insert(level_node, "end", text="TreasureHuntMap", open=True)
            
            # 各オブジェクトカテゴリ
            treasure_chests = self.game_tree.insert(treasureHuntMap, "end", text="宝箱", open=True)
            self.game_tree.insert(treasure_chests, "end", text="TreasureChest_1 [500, 500, 50]")
            self.game_tree.insert(treasure_chests, "end", text="TreasureChest_2 [-500, 500, 50]")
            self.game_tree.insert(treasure_chests, "end", text="TreasureChest_3 [500, -500, 50]")
            self.game_tree.insert(treasure_chests, "end", text="TreasureChest_4 [-500, -500, 50]")
            
            coins = self.game_tree.insert(treasureHuntMap, "end", text="コイン", open=True)
            self.game_tree.insert(coins, "end", text="Coin_1 [300, 300, 50]")
            self.game_tree.insert(coins, "end", text="Coin_2 [-300, 300, 50]")
            self.game_tree.insert(coins, "end", text="Coin_3 [300, -300, 50]")
            self.game_tree.insert(coins, "end", text="Coin_4 [-300, -300, 50]")
            self.game_tree.insert(coins, "end", text="Coin_5 [0, 0, 50]")
            
            potions = self.game_tree.insert(treasureHuntMap, "end", text="ポーション", open=True)
            self.game_tree.insert(potions, "end", text="HealthPotion_1 [200, 200, 50]")
            self.game_tree.insert(potions, "end", text="HealthPotion_2 [-200, 200, 50]")
            
            others = self.game_tree.insert(treasureHuntMap, "end", text="その他", open=True)
            self.game_tree.insert(others, "end", text="PlayerStart [0, 0, 100]")
            
            # ログに記録
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ゲーム構造ツリーを更新しました\n")
            self.log_text.see(tk.END)
        except Exception as e:
            logger.error(f"ゲーム構造更新エラー: {str(e)}")
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ゲーム構造更新エラー: {str(e)}\n")
            self.log_text.see(tk.END)
    
    def refresh_3d_view(self):
        """3Dビューを更新"""
        try:
            # グリッドを再描画
            self.draw_grid()
            
            # レベルオブジェクトを描画
            self.draw_level_objects()
            
            # ログに記録
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 3Dビューを更新しました\n")
            self.log_text.see(tk.END)
        except Exception as e:
            logger.error(f"3Dビュー更新エラー: {str(e)}")
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 3Dビュー更新エラー: {str(e)}\n")
            self.log_text.see(tk.END)
    
    def refresh_all(self):
        """すべての情報を更新"""
        self.refresh_server_info()
        self.refresh_game_tree()
        self.refresh_3d_view()
    
    def periodic_refresh(self):
        """定期的な更新処理"""
        self.refresh_all()
        # 次の定期更新をスケジュール
        self.master.after(5000, self.periodic_refresh)

# メイン実行
if __name__ == "__main__":
    root = tk.Tk()
    app = MCPMonitor(root)
    root.mainloop() 
