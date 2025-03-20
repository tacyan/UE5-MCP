#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCPフレームワーク用Blender APIモジュール

BlenderとMCPサーバーを中継する軽量APIモジュールです。
このスクリプトはBlender Python環境で実行され、MCPサーバーとREST APIで通信します。

主な機能:
- ローカルBlenderインスタンスとの通信
- MCPサーバーへのコマンド転送
- モデル生成、編集、エクスポート機能の提供

使用方法:
1. Blenderで「スクリプト」タブを開く
2. このスクリプトをテキストエディタにロード
3. 実行（Alt+P）

注意:
- このスクリプトを実行するにはBlender 4.0以上が必要です
- BlenderがPythonモジュールをインポートできる環境が必要です
"""

import bpy
import os
import sys
import json
import math
import tempfile
import threading
import time
import socket
import logging
from pathlib import Path

# Blender環境で外部モジュールを使用できるようにする
def setup_python_path():
    """Python環境変数を設定し、外部パッケージをロードできるようにする"""
    # site-packagesのパスを追加
    import site
    import subprocess
    
    try:
        # システムPythonパスを取得（サブプロセスで実行）
        python_exe = "python3" if sys.platform != "win32" else "python"
        result = subprocess.run(
            [python_exe, "-c", "import site; print(site.getsitepackages()[0])"],
            capture_output=True,
            text=True,
            check=True
        )
        site_packages = result.stdout.strip()
        
        if site_packages and site_packages not in sys.path:
            sys.path.append(site_packages)
        
        # 現在のディレクトリを追加
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        
        return True
    except Exception as e:
        print(f"Python環境設定エラー: {str(e)}")
        return False

# requestsモジュールのロード
try:
    import requests
except ImportError:
    setup_python_path()
    try:
        import requests
    except ImportError:
        print("requestsモジュールをインストールしてください。")
        print("コマンドライン: pip install requests")
        requests = None

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_blender_api")

class MCPBlenderAPI:
    """
    BlenderとMCPサーバーを連携させるAPIクラス
    """
    
    def __init__(self, server_url=None, port=None):
        """
        初期化メソッド
        
        引数:
            server_url (str): MCPサーバーのURL（デフォルト: 環境変数またはlocalhostから取得）
            port (int): APIサーバーのポート（デフォルト: 環境変数または9001）
        """
        # サーバーURL設定
        if server_url:
            self.server_url = server_url
        else:
            host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
            port = os.environ.get("MCP_SERVER_PORT", "8080")
            self.server_url = f"http://{host}:{port}"
        
        # APIサーバーポート設定
        self.api_port = port or int(os.environ.get("BLENDER_MCP_PORT", 9081))
        
        # エクスポートディレクトリ設定
        self.export_dir = os.environ.get("MCP_EXPORT_DIR", os.path.join(tempfile.gettempdir(), "mcp_exports"))
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Blenderバージョン確認
        self.blender_version = bpy.app.version
        logger.info(f"Blender バージョン: {self.blender_version[0]}.{self.blender_version[1]}.{self.blender_version[2]}")
        
        # セッション情報
        self.session = {
            "id": f"blender_{int(time.time())}",
            "connected": False,
            "last_command": None,
            "last_response": None
        }
        
        # サーバーとの接続確認
        self.check_connection()
    
    def check_connection(self):
        """
        MCPサーバーとの接続を確認する
        
        戻り値:
            bool: 接続成功したかどうか
        """
        if not requests:
            logger.error("requestsモジュールがインストールされていないため、MCPサーバーに接続できません")
            return False
            
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    logger.info(f"MCPサーバーに接続しました: {self.server_url}")
                    self.session["connected"] = True
                    return True
                else:
                    logger.warning(f"MCPサーバーの状態が異常です: {data.get('status')}")
            else:
                logger.error(f"MCPサーバー接続エラー: ステータスコード {response.status_code}")
        except Exception as e:
            logger.error(f"MCPサーバー接続例外: {str(e)}")
        
        self.session["connected"] = False
        return False
    
    def create_model(self, model_type, model_name=None, location=(0, 0, 0), scale=(1, 1, 1)):
        """
        シンプルなモデルを作成する
        
        引数:
            model_type (str): モデルタイプ (cube, sphere, cylinder, cone, torus)
            model_name (str): モデル名（未指定時は自動生成）
            location (tuple): 位置
            scale (tuple): スケール
            
        戻り値:
            dict: 作成したモデルの情報
        """
        # すべての選択を解除
        bpy.ops.object.select_all(action='DESELECT')
        
        # モデル名が指定されていない場合は自動生成
        if not model_name:
            model_name = f"{model_type.capitalize()}_{int(time.time())}"
        
        # モデルタイプに応じてオブジェクトを作成
        if model_type.lower() == "cube":
            bpy.ops.mesh.primitive_cube_add(size=2.0, location=location)
        elif model_type.lower() == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=location)
        elif model_type.lower() == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=2.0, location=location)
        elif model_type.lower() == "cone":
            bpy.ops.mesh.primitive_cone_add(radius1=1.0, radius2=0.0, depth=2.0, location=location)
        elif model_type.lower() == "torus":
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.25, location=location)
        else:
            logger.error(f"未知のモデルタイプ: {model_type}")
            return {"status": "error", "message": f"Unknown model type: {model_type}"}
        
        # 作成したオブジェクトを取得
        obj = bpy.context.active_object
        
        # 名前とスケールを設定
        obj.name = model_name
        obj.scale = (scale[0], scale[1], scale[2])
        
        logger.info(f"モデルを作成しました: {model_name} ({model_type})")
        
        return {
            "status": "success",
            "model": {
                "name": model_name,
                "type": model_type,
                "location": location,
                "scale": scale
            }
        }
    
    def apply_material(self, obj_name, color=(0.8, 0.8, 0.8, 1.0), 
                        metallic=0.0, roughness=0.5, specular=0.5):
        """
        オブジェクトにマテリアルを適用する
        
        引数:
            obj_name (str): オブジェクト名
            color (tuple): RGBA色
            metallic (float): メタリック値 (0.0-1.0)
            roughness (float): ラフネス値 (0.0-1.0)
            specular (float): スペキュラ値 (0.0-1.0)
            
        戻り値:
            dict: 適用結果
        """
        # オブジェクトの存在確認
        if obj_name not in bpy.data.objects:
            logger.error(f"オブジェクトが見つかりません: {obj_name}")
            return {"status": "error", "message": f"Object '{obj_name}' not found"}
        
        obj = bpy.data.objects[obj_name]
        
        # マテリアル名を生成
        mat_name = f"{obj_name}_Material"
        
        # マテリアルが既に存在するか確認、なければ作成
        if mat_name in bpy.data.materials:
            mat = bpy.data.materials[mat_name]
        else:
            mat = bpy.data.materials.new(name=mat_name)
        
        # ノードベースのマテリアルを使用
        mat.use_nodes = True
        
        # プリンシプルBSDFノードの取得とパラメータ設定
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Specular'].default_value = specular
        
        # オブジェクトにマテリアルを割り当て
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
        
        logger.info(f"マテリアルを適用しました: {mat_name} -> {obj_name}")
        
        return {
            "status": "success",
            "material": {
                "name": mat_name,
                "object": obj_name,
                "color": color,
                "metallic": metallic,
                "roughness": roughness,
                "specular": specular
            }
        }
    
    def export_model(self, obj_name=None, file_format="fbx"):
        """
        モデルをエクスポートする
        
        引数:
            obj_name (str): エクスポートするオブジェクト名（未指定時は選択オブジェクト）
            file_format (str): エクスポート形式（fbx, obj, glb）
            
        戻り値:
            dict: エクスポート結果
        """
        # オブジェクト選択
        if obj_name:
            if obj_name not in bpy.data.objects:
                logger.error(f"オブジェクトが見つかりません: {obj_name}")
                return {"status": "error", "message": f"Object '{obj_name}' not found"}
            
            # 選択解除して対象オブジェクトのみ選択
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[obj_name].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[obj_name]
        else:
            # 選択があるか確認
            if not bpy.context.selected_objects:
                logger.error("オブジェクトが選択されていません")
                return {"status": "error", "message": "No objects selected"}
            
            obj_name = bpy.context.active_object.name
        
        # エクスポートパス設定
        export_file = f"{obj_name}.{file_format.lower()}"
        export_path = os.path.join(self.export_dir, export_file)
        
        # 形式別のエクスポート処理
        if file_format.lower() == "fbx":
            bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=True,
                global_scale=1.0,
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_NONE',
                object_types={'MESH', 'ARMATURE'},
                use_mesh_modifiers=True,
                mesh_smooth_type='OFF',
                path_mode='AUTO'
            )
        elif file_format.lower() == "obj":
            bpy.ops.export_scene.obj(
                filepath=export_path,
                use_selection=True,
                global_scale=1.0,
                path_mode='AUTO'
            )
        elif file_format.lower() == "glb":
            bpy.ops.export_scene.gltf(
                filepath=export_path,
                export_format='GLB',
                use_selection=True
            )
        else:
            logger.error(f"未対応のファイル形式: {file_format}")
            return {"status": "error", "message": f"Unsupported file format: {file_format}"}
        
        logger.info(f"モデルをエクスポートしました: {export_path}")
        
        return {
            "status": "success",
            "export": {
                "object": obj_name,
                "format": file_format,
                "path": export_path,
                "file": export_file
            }
        }
    
    def send_to_ue5(self, obj_name, format="fbx"):
        """
        モデルをUE5に送信する
        
        引数:
            obj_name (str): 送信するオブジェクト名
            format (str): エクスポート形式
            
        戻り値:
            dict: 送信結果
        """
        if not self.session["connected"]:
            if not self.check_connection():
                logger.error("MCPサーバーに接続されていないため、UE5にモデルを送信できません")
                return {"status": "error", "message": "Not connected to MCP server"}
        
        # モデルをエクスポート
        export_result = self.export_model(obj_name, format)
        if export_result["status"] != "success":
            return export_result
        
        export_path = export_result["export"]["path"]
        
        # UE5へのインポートコマンドを送信
        try:
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "import_asset",
                    "params": {
                        "path": export_path,
                        "destination": f"/Game/Assets/{obj_name}"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    logger.info(f"モデルをUE5に送信しました: {obj_name}")
                    return {
                        "status": "success",
                        "message": f"Model {obj_name} sent to UE5 successfully",
                        "details": result
                    }
                else:
                    logger.error(f"UE5送信エラー: {result.get('message', 'Unknown error')}")
                    return {
                        "status": "error",
                        "message": result.get("message", "Unknown error in UE5 import"),
                        "details": result
                    }
            else:
                logger.error(f"UE5送信エラー: HTTP {response.status_code}")
                return {
                    "status": "error",
                    "message": f"HTTP error: {response.status_code}",
                    "details": {"status_code": response.status_code}
                }
        
        except Exception as e:
            logger.error(f"UE5送信中に例外が発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_api_server(self):
        """
        APIサーバーを起動して、外部からのコマンドを受け付ける
        """
        import http.server
        import socketserver
        
        port = self.api_port
        handler = self._create_api_handler()
        
        class TCPServer(socketserver.TCPServer):
            allow_reuse_address = True
        
        try:
            # サーバーの開始
            with TCPServer(("0.0.0.0", port), handler) as httpd:
                logger.info(f"APIサーバーを開始しました。ポート: {port}")
                logger.info("Ctrl+Cで終了")
                httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("APIサーバーを終了します")
        except Exception as e:
            logger.error(f"APIサーバー起動エラー: {str(e)}")
            
            # 既に使用中のポートを検出
            if "Address already in use" in str(e):
                logger.info(f"ポート {port} は既に使用されています。別のポートを試します。")
                # 別のポートを試す
                for new_port in range(port + 1, port + 10):
                    try:
                        with TCPServer(("0.0.0.0", new_port), handler) as httpd:
                            logger.info(f"APIサーバーを開始しました。ポート: {new_port}")
                            logger.info("Ctrl+Cで終了")
                            httpd.serve_forever()
                            break
                    except:
                        continue
    
    def _create_api_handler(self):
        """
        APIリクエストを処理するハンドラークラスを作成
        
        戻り値:
            class: HTTPリクエストハンドラークラス
        """
        import http.server
        import json
        
        api = self  # selfへの参照を保持
        
        class MCPBlenderAPIHandler(http.server.BaseHTTPRequestHandler):
            """BlenderのAPIリクエストを処理するハンドラー"""
            
            def _send_response(self, status_code, data):
                """JSONレスポンスを送信"""
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            
            def do_OPTIONS(self):
                """CORSプリフライトリクエストに応答"""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def do_GET(self):
                """GETリクエストを処理"""
                if self.path == '/status':
                    # ステータス情報を返す
                    self._send_response(200, {
                        "status": "running",
                        "blender_version": bpy.app.version_string,
                        "session_id": api.session["id"],
                        "connected_to_server": api.session["connected"]
                    })
                else:
                    self._send_response(404, {"error": "Not found"})
            
            def do_POST(self):
                """POSTリクエストを処理"""
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    data = json.loads(post_data)
                    command = data.get("command")
                    params = data.get("params", {})
                    
                    # コマンドの処理
                    if command == "create_model":
                        model_type = params.get("type", "cube")
                        model_name = params.get("name")
                        location = params.get("location", (0, 0, 0))
                        scale = params.get("scale", (1, 1, 1))
                        
                        result = api.create_model(model_type, model_name, location, scale)
                        self._send_response(200, result)
                    
                    elif command == "apply_material":
                        obj_name = params.get("object")
                        color = params.get("color", (0.8, 0.8, 0.8, 1.0))
                        metallic = params.get("metallic", 0.0)
                        roughness = params.get("roughness", 0.5)
                        specular = params.get("specular", 0.5)
                        
                        result = api.apply_material(obj_name, color, metallic, roughness, specular)
                        self._send_response(200, result)
                    
                    elif command == "export_model":
                        obj_name = params.get("object")
                        format = params.get("format", "fbx")
                        
                        result = api.export_model(obj_name, format)
                        self._send_response(200, result)
                    
                    elif command == "send_to_ue5":
                        obj_name = params.get("object")
                        format = params.get("format", "fbx")
                        
                        result = api.send_to_ue5(obj_name, format)
                        self._send_response(200, result)
                    
                    elif command == "run_script":
                        script_path = params.get("script_path")
                        script_args = params.get("args", [])
                        
                        # スクリプトの実行（メインスレッドで）
                        try:
                            # 現在のアドオンディレクトリを取得
                            addon_dir = os.path.dirname(os.path.abspath(__file__))
                            
                            # スクリプトパスの調整（相対パスの場合）
                            if not os.path.isabs(script_path):
                                script_path = os.path.join(addon_dir, script_path)
                            
                            # スクリプトの存在確認
                            if not os.path.exists(script_path):
                                self._send_response(404, {
                                    "status": "error", 
                                    "message": f"Script not found: {script_path}"
                                })
                                return
                            
                            # スクリプトを実行
                            # ここではexecを使用して現在の環境でスクリプトを実行
                            with open(script_path, 'r') as script_file:
                                script_code = script_file.read()
                                
                                # グローバル変数と辞書を設定
                                globals_dict = globals().copy()
                                globals_dict.update({
                                    "__file__": script_path,
                                    "argv": script_args
                                })
                                
                                # スクリプトを実行
                                exec(script_code, globals_dict)
                            
                            self._send_response(200, {
                                "status": "success",
                                "message": f"Script executed: {script_path}"
                            })
                        except Exception as e:
                            self._send_response(500, {
                                "status": "error",
                                "message": f"Script execution error: {str(e)}"
                            })
                    
                    else:
                        self._send_response(400, {
                            "status": "error", 
                            "message": f"Unknown command: {command}"
                        })
                
                except json.JSONDecodeError:
                    self._send_response(400, {"error": "Invalid JSON"})
                except Exception as e:
                    self._send_response(500, {"error": str(e)})
        
        return MCPBlenderAPIHandler

# Blenderで実行したときのエントリポイント
def register():
    """Blenderアドオンとして登録"""
    # ここにはアドオン登録コードが入る（今回は単独スクリプトのため使用しない）
    pass

def unregister():
    """Blenderアドオンの登録解除"""
    # ここにはアドオン登録解除コードが入る（今回は単独スクリプトのため使用しない）
    pass

# スクリプトが直接実行された場合に実行
if __name__ == "__main__":
    # API初期化
    api = MCPBlenderAPI()
    
    # APIサーバーを別スレッドで起動
    server_thread = threading.Thread(target=api.run_api_server)
    server_thread.daemon = True  # メインスレッドが終了したらサーバーも終了
    server_thread.start()
    
    # Blenderのメインスレッドはそのまま実行を続ける（UIを維持）
    print("MCPBlenderAPIサーバーがバックグラウンドで起動しました。")
    print(f"サーバーURL: http://localhost:{api.api_port}")
    print("このウィンドウを閉じるとサーバーも終了します。") 
