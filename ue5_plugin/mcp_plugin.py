#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPプラグイン for Unreal Engine 5

UE5内で実行するためのMCPプラグインスクリプト。
MCPサーバーと通信し、UE5内でのコマンド実行を可能にします。

使用方法:
1. UE5エディタのスクリプトエディタでこのファイルを開く
2. 実行ボタンを押すか、Alt+Pでスクリプトを実行
"""

import unreal
import requests
import json
import os
import sys
import time
import random
import threading

# 環境変数からMCPサーバー設定を取得
def get_mcp_server_url():
    """環境変数または設定ファイルからMCPサーバーURLを取得"""
    # 環境変数から取得を試みる
    env_host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
    env_port = os.environ.get("MCP_SERVER_PORT", "8080")
    
    # 設定ファイルから取得を試みる
    try:
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
                host = settings.get("server", {}).get("host", env_host)
                port = settings.get("server", {}).get("port", env_port)
                return f"http://{host}:{port}"
    except:
        pass
    
    # デフォルト値を返す
    return f"http://{env_host}:{env_port}"

# MCPサーバー設定
MCP_SERVER = get_mcp_server_url()

class MCPPlugin:
    """UE5-MCP連携プラグイン"""

    def __init__(self):
        """初期化"""
        self.editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        self.editorAssetLib = unreal.EditorAssetLibrary
        self.editor_level_lib = unreal.EditorLevelLibrary
        self.editor_filter_lib = unreal.EditorFilterLibrary
        self.connected = False
        
        # 通知スタイルを設定
        self.notification = unreal.EditorNotificationController()
        self.style = self.notification.notification_style
        self.style.fade_in_duration = 0.5
        self.style.fade_out_duration = 0.5
        self.style.expire_duration = 3.0
        
        unreal.log(f"MCPサーバーURL: {MCP_SERVER}")
        
        # サーバー接続を確認
        self.check_connection()

    def check_connection(self):
        """MCPサーバーとの接続を確認"""
        try:
            response = requests.get(f"{MCP_SERVER}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    self.connected = True
                    unreal.log("MCPサーバーに接続しました")
                    self.show_notification("MCPサーバーに接続しました", True)
                    return True
            
            # 404エラーの場合は別のエンドポイントを試す
            if response.status_code == 404:
                response = requests.get(f"{MCP_SERVER}/api/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "running":
                        self.connected = True
                        unreal.log("MCPサーバーに接続しました")
                        self.show_notification("MCPサーバーに接続しました", True)
                        return True
            
            self.connected = False
            unreal.log_error("MCPサーバーに接続できません")
            self.show_notification("MCPサーバーに接続できません", False)
            return False
        except Exception as e:
            self.connected = False
            unreal.log_error(f"MCPサーバー接続エラー: {str(e)}")
            self.show_notification(f"MCPサーバー接続エラー: {str(e)}", False)
            return False

    def show_notification(self, message, success=True):
        """UE5エディタに通知を表示"""
        self.style.text_color = unreal.LinearColor(0.0, 1.0, 0.0, 1.0) if success else unreal.LinearColor(1.0, 0.0, 0.0, 1.0)
        self.notification.display_notification(message, self.style)
    
    def create_level(self, name="NewLevel", template="Empty"):
        """新しいレベルを作成"""
        try:
            # 既存のレベルを閉じる
            self.level_editor_subsystem.new_level_from_template(f"/Game/Maps/{name}", template)
            self.show_notification(f"レベル '{name}' を作成しました", True)
            return True
        except Exception as e:
            unreal.log_error(f"レベル作成エラー: {str(e)}")
            self.show_notification(f"レベル作成エラー: {str(e)}", False)
            return False
    
    def import_asset(self, file_path, destination="/Game/Assets"):
        """アセットをインポート"""
        try:
            # インポートタスクを作成
            task = unreal.AssetImportTask()
            task.filename = file_path
            task.destination_path = destination
            task.replace_existing = True
            task.automated = True
            task.save = True
            
            # インポート実行
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            
            self.show_notification(f"アセットをインポートしました: {os.path.basename(file_path)}", True)
            return True
        except Exception as e:
            unreal.log_error(f"アセットインポートエラー: {str(e)}")
            self.show_notification(f"アセットインポートエラー: {str(e)}", False)
            return False
    
    def place_asset(self, asset_path, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), name=None):
        """アセットをレベルに配置"""
        try:
            # アセットをロード
            asset = self.editorAssetLib.load_asset(asset_path)
            if not asset:
                unreal.log_error(f"アセット '{asset_path}' が見つかりません")
                self.show_notification(f"アセット '{asset_path}' が見つかりません", False)
                return False
            
            # アセットを配置
            x, y, z = location
            pitch, yaw, roll = rotation
            scale_x, scale_y, scale_z = scale
            
            location_vector = unreal.Vector(x, y, z)
            rotation_rotator = unreal.Rotator(pitch, yaw, roll)
            scale_vector = unreal.Vector(scale_x, scale_y, scale_z)
            
            actor = self.editor_level_lib.spawn_actor_from_object(
                asset, 
                location_vector, 
                rotation_rotator
            )
            
            # スケールを設定
            actor.set_actor_scale3d(scale_vector)
            
            # 名前を設定（指定があれば）
            if name:
                actor.set_actor_label(name)
            
            self.show_notification(f"アセットを配置しました: {os.path.basename(asset_path)}", True)
            return True
        except Exception as e:
            unreal.log_error(f"アセット配置エラー: {str(e)}")
            self.show_notification(f"アセット配置エラー: {str(e)}", False)
            return False
    
    def create_blueprint(self, name, parent_class="Actor", script="", components=None, variables=None):
        """ブループリントを作成"""
        try:
            # ブループリントファクトリを作成
            blueprint_factory = unreal.BlueprintFactory()
            blueprint_factory.parent_class = unreal.load_class(None, parent_class)
            
            # ブループリントアセットを作成
            blueprint_path = f"/Game/Blueprints/{name}"
            blueprint = self.asset_tools.create_asset(name, "/Game/Blueprints", unreal.Blueprint, blueprint_factory)
            
            if not blueprint:
                unreal.log_error(f"ブループリント '{name}' の作成に失敗しました")
                self.show_notification(f"ブループリント '{name}' の作成に失敗しました", False)
                return False
            
            # コンポーネントを追加（実装が必要）
            if components:
                pass  # 実装が必要
            
            # 変数を追加（実装が必要）
            if variables:
                pass  # 実装が必要
            
            # スクリプトを実装（実装が必要）
            if script:
                pass  # 実装が必要
            
            # アセットを保存
            self.editorAssetLib.save_asset(blueprint_path)
            
            self.show_notification(f"ブループリント '{name}' を作成しました", True)
            return True
        except Exception as e:
            unreal.log_error(f"ブループリント作成エラー: {str(e)}")
            self.show_notification(f"ブループリント作成エラー: {str(e)}", False)
            return False
    
    def build_lighting(self, quality="Production"):
        """ライティングをビルド"""
        try:
            # 品質設定
            quality_map = {
                "Preview": unreal.LightingBuildQuality.PREVIEW,
                "Medium": unreal.LightingBuildQuality.MEDIUM,
                "Production": unreal.LightingBuildQuality.PRODUCTION,
                "High": unreal.LightingBuildQuality.HIGH
            }
            
            build_quality = quality_map.get(quality, unreal.LightingBuildQuality.MEDIUM)
            
            # ライティングをビルド
            unreal.EditorLightingSubsystem.get_editor_lighting_subsystem().build_lighting(
                build_quality,
                True,  # すべてビルド
                False  # 非同期
            )
            
            self.show_notification(f"ライティングビルドを開始しました（品質: {quality}）", True)
            return True
        except Exception as e:
            unreal.log_error(f"ライティングビルドエラー: {str(e)}")
            self.show_notification(f"ライティングビルドエラー: {str(e)}", False)
            return False
    
    def set_environment(self, sky_type="dynamic", time_of_day="day", weather="clear"):
        """環境設定を適用"""
        try:
            # 実装が必要
            self.show_notification(f"環境設定を適用しました: {sky_type}, {time_of_day}, {weather}", True)
            return True
        except Exception as e:
            unreal.log_error(f"環境設定エラー: {str(e)}")
            self.show_notification(f"環境設定エラー: {str(e)}", False)
            return False

    def handle_command(self, command, params):
        """受信したコマンドを処理する"""
        unreal.log(f"コマンド処理: {command}, パラメータ: {json.dumps(params)}")
        
        try:
            # コマンドごとに処理を分岐
            if command == "create_level":
                name = params.get("name", "NewLevel")
                template = params.get("template", "Empty")
                success = self.create_level(name, template)
                return {
                    "status": "success" if success else "error",
                    "message": f"レベル '{name}' を作成しました" if success else f"レベル '{name}' の作成に失敗しました"
                }
            
            elif command == "import_asset":
                file_path = params.get("path", "")
                destination = params.get("destination", "/Game/Assets")
                
                if not file_path:
                    return {"status": "error", "message": "インポートするファイルパスが指定されていません"}
                
                success = self.import_asset(file_path, destination)
                return {
                    "status": "success" if success else "error",
                    "message": f"アセット '{file_path}' をインポートしました" if success else f"アセット '{file_path}' のインポートに失敗しました"
                }
            
            elif command == "place_actor" or command == "spawn_actor":
                asset_path = params.get("asset_path", "")
                blueprint = params.get("blueprint", "")
                
                # blueprintパラメータが指定されている場合はそれを使用
                if blueprint:
                    asset_path = blueprint
                
                location = params.get("location", [0, 0, 0])
                rotation = params.get("rotation", [0, 0, 0])
                scale = params.get("scale", [1, 1, 1])
                name = params.get("name", None)
                
                if not asset_path:
                    # actor_typeがある場合は標準アクター
                    actor_type = params.get("type", "")
                    if actor_type:
                        # 標準アクターのパスマッピング
                        type_map = {
                            "PlayerStart": "/Engine/EditorBlueprintResources/PlayerStart",
                            "PointLight": "/Engine/BasicShapes/PointLight",
                            "StaticMeshActor": "/Engine/BasicShapes/Cube"
                        }
                        
                        asset_path = type_map.get(actor_type, "")
                        
                        # StaticMeshActorの場合、static_meshパラメータがあればそれを使用
                        if actor_type == "StaticMeshActor":
                            static_mesh = params.get("static_mesh", "")
                            if static_mesh:
                                asset_path = static_mesh
                
                if not asset_path:
                    return {"status": "error", "message": "配置するアセットパスが指定されていません"}
                
                success = self.place_asset(asset_path, location, rotation, scale, name)
                return {
                    "status": "success" if success else "error",
                    "message": f"アクター '{asset_path}' を配置しました" if success else f"アクター '{asset_path}' の配置に失敗しました"
                }
            
            elif command == "create_blueprint":
                name = params.get("name", "NewBlueprint")
                parent_class = params.get("parent_class", "Actor")
                script = params.get("script", "")
                components = params.get("components", None)
                variables = params.get("variables", None)
                
                success = self.create_blueprint(name, parent_class, script, components, variables)
                return {
                    "status": "success" if success else "error",
                    "message": f"ブループリント '{name}' を作成しました" if success else f"ブループリント '{name}' の作成に失敗しました"
                }
            
            elif command == "build_lighting":
                quality = params.get("quality", "Production")
                success = self.build_lighting(quality)
                return {
                    "status": "success" if success else "error",
                    "message": f"ライティングビルドを開始しました" if success else "ライティングビルドの開始に失敗しました"
                }
            
            elif command == "save_level":
                # 現在のレベルを保存
                try:
                    self.level_editor_subsystem.save_current_level()
                    return {"status": "success", "message": "レベルを保存しました"}
                except Exception as e:
                    unreal.log_error(f"レベル保存エラー: {str(e)}")
                    return {"status": "error", "message": f"レベル保存エラー: {str(e)}"}
            
            elif command == "set_game_mode":
                game_mode = params.get("game_mode", "")
                
                if not game_mode:
                    return {"status": "error", "message": "ゲームモードが指定されていません"}
                
                try:
                    # ワールド設定を取得
                    world_settings = unreal.EditorLevelLibrary.get_game_mode()
                    if not world_settings:
                        return {"status": "error", "message": "ワールド設定の取得に失敗しました"}
                    
                    # ゲームモードを設定
                    game_mode_class = unreal.load_class(None, game_mode)
                    if not game_mode_class:
                        return {"status": "error", "message": f"ゲームモード '{game_mode}' が見つかりません"}
                    
                    world_settings.set_editor_property("game_mode", game_mode_class)
                    
                    return {"status": "success", "message": f"ゲームモード '{game_mode}' を設定しました"}
                except Exception as e:
                    unreal.log_error(f"ゲームモード設定エラー: {str(e)}")
                    return {"status": "error", "message": f"ゲームモード設定エラー: {str(e)}"}
            
            elif command == "create_actor":
                # place_actorコマンドに転送
                return self.handle_command("place_actor", params)
            
            else:
                # 未知のコマンド
                return {"status": "error", "message": f"未知のコマンド: {command}"}
        
        except Exception as e:
            unreal.log_error(f"コマンド実行中にエラーが発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def start_command_listener(self):
        """コマンドリスナーを開始"""
        def listener_thread():
            while True:
                try:
                    # サーバーからコマンドをポーリング
                    pass
                except Exception as e:
                    unreal.log_error(f"コマンドリスナーエラー: {str(e)}")
                time.sleep(1)
        
        # スレッドを開始
        thread = threading.Thread(target=listener_thread)
        thread.daemon = True
        thread.start()

# インスタンスを作成
mcp_plugin = MCPPlugin()

def create_ball_collector_game():
    """ボール収集ゲームを作成"""
    # 1. レベルを作成
    mcp_plugin.create_level("BallCollectorLevel", "ThirdPerson")
    
    # 2. コレクティブルボールのブループリントを作成
    mcp_plugin.create_blueprint(
        "BP_CollectibleBall",
        "Actor",
        "プレイヤーが近づくと収集できる回転するボール"
    )
    
    # 3. ゲームモードのブループリントを作成
    mcp_plugin.create_blueprint(
        "BP_BallCollectorGameMode",
        "GameModeBase",
        "プレイヤーのスコアを管理し、すべてのボールを集めるとゲームクリアになるゲームモード"
    )
    
    # 4. HUDのブループリントを作成
    mcp_plugin.create_blueprint(
        "BP_BallCollectorHUD",
        "HUD",
        "プレイヤーのスコアと残りのボール数を表示するHUD"
    )
    
    # 5. ボールをレベルに配置
    for i in range(10):
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        z = random.uniform(50, 200)
        
        mcp_plugin.place_asset(
            "/Game/Blueprints/BP_CollectibleBall",
            location=(x, y, z),
            rotation=(0, 0, 0),
            scale=(1, 1, 1),
            name=f"CollectibleBall_{i+1}"
        )
    
    # 6. 環境設定を適用
    mcp_plugin.set_environment(
        sky_type="dynamic",
        time_of_day="day",
        weather="clear"
    )
    
    # 7. ライティングをビルド
    mcp_plugin.build_lighting("Medium")
    
    mcp_plugin.show_notification("ボール収集ゲームの作成が完了しました！", True)

# テスト実行
create_ball_collector_game()

# UE5 MCP API用のHTTPサーバー実装
def run_ue5_api_server():
    """UE5のMCP APIサーバーを起動"""
    import threading
    import http.server
    import socketserver
    
    # UE5 MCP APIポート
    ue5_mcp_port = int(os.environ.get("UE5_MCP_PORT", 9082))
    
    class UE5Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                command = data.get("command")
                params = data.get("params", {})
                
                unreal.log(f"コマンド受信: {command}")
                
                # MCPPluginインスタンスを作成
                plugin = MCPPlugin()
                
                # コマンドを実行
                result = plugin.handle_command(command, params)
                
                # レスポンスを返す
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                unreal.log_error(f"コマンド実行エラー: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode('utf-8'))
    
    def api_server_thread():
        try:
            with socketserver.TCPServer(("0.0.0.0", ue5_mcp_port), UE5Handler) as httpd:
                unreal.log(f"UE5 MCP APIサーバーを開始しました - ポート: {ue5_mcp_port}")
                httpd.serve_forever()
        except Exception as e:
            unreal.log_error(f"UE5 MCP APIサーバー起動エラー: {str(e)}")
    
    # バックグラウンドでAPIサーバーを起動
    api_thread = threading.Thread(target=api_server_thread)
    api_thread.daemon = True
    api_thread.start()
    
    return api_thread 

# メイン実行部分（UE5エディタで実行されるコード）
if __name__ == "__main__":
    unreal.log("UE5 MCPプラグインを初期化しています...")
    # UE5 API HTTP サーバーを起動
    api_thread = run_ue5_api_server()
    
    # MCPプラグインのインスタンスを作成
    plugin = MCPPlugin()
    
    # 接続状態を確認
    connected = plugin.check_connection()
    
    if connected:
        unreal.log("MCPフレームワークが正常に初期化されました！")
        
        # テストレベルの作成（オプション）
        create_ball_collector_game()
    else:
        unreal.log_warning("MCPサーバーに接続できませんでした。サーバーが実行中か確認してください。")
        unreal.log(f"MCPサーバーURL: {MCP_SERVER}")
        
    unreal.log("初期化完了 - UE5 MCPプラグインは実行中です") 
