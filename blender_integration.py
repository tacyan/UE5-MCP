#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blender-MCP統合スクリプト

このスクリプトは、Blender 4.4.0のPythonインタプリタから実行され、
MCPサーバーと連携してMCPフレームワークを使用できるようにします。

主な機能:
- MCPサーバーへの接続
- BlenderからUE5へのモデル転送の実装
- AIを活用した3Dモデリングのサポート

使用方法:
1. Blenderを起動
2. スクリプトエディタでこのファイルを開く
3. 実行ボタンを押すか、Alt+Pでスクリプトを実行

制限事項:
- Blender 4.0以上が必要です
- MCPサーバーが事前に起動している必要があります
"""

import bpy
import json
import os
import sys
import requests
import tempfile
import mathutils
import time
import logging
from pathlib import Path

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("blender_integration")

class BlenderMCPIntegration:
    """
    BlenderとMCP連携のためのクラス
    """
    
    def __init__(self, server_host="127.0.0.1", server_port=8000):
        """
        初期化メソッド
        
        引数:
            server_host (str): MCPサーバーのホスト
            server_port (int): MCPサーバーのポート
        """
        self.server_url = f"http://{server_host}:{server_port}"
        self.export_dir = os.path.join(tempfile.gettempdir(), "blender_mcp_exports")
        
        # エクスポートディレクトリが存在しなければ作成
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
        
        logger.info(f"MCPサーバーURL: {self.server_url}")
        logger.info(f"エクスポートディレクトリ: {self.export_dir}")
        logger.info(f"Blenderバージョン: {bpy.app.version_string}")
        
        # Blenderの通知UI設定
        self.report_level = {'INFO'}
    
    def connect_to_server(self):
        """
        MCPサーバーへの接続を確認する
        
        戻り値:
            bool: 接続成功したかどうか
        """
        try:
            logger.info("MCPサーバーへの接続を確認しています...")
            response = requests.get(f"{self.server_url}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                server_status = status_data.get("status", "unknown")
                
                if server_status == "running":
                    logger.info("MCPサーバーに正常に接続しました")
                    self.report({'INFO'}, "MCPサーバーに正常に接続しました")
                    return True
                else:
                    logger.warning(f"MCPサーバーのステータスが異常: {server_status}")
                    self.report({'WARNING'}, f"MCPサーバーのステータスが異常: {server_status}")
                    return False
            else:
                logger.error(f"MCPサーバーへの接続に失敗しました: {response.status_code}")
                self.report({'ERROR'}, f"MCPサーバーへの接続に失敗しました: {response.status_code}")
                return False
        except Exception as e:
            logger.exception(f"MCPサーバーへの接続中にエラーが発生しました: {str(e)}")
            self.report({'ERROR'}, f"MCPサーバーへの接続中にエラーが発生しました: {str(e)}")
            return False
    
    def report(self, level, message):
        """
        Blenderの通知システムを模倣するメソッド（実際のaddonではbpy.ops.report()を使用）
        
        引数:
            level (set): 通知レベル
            message (str): 通知メッセージ
        """
        level_str = list(level)[0]
        logger.log(
            logging.INFO if level_str == 'INFO' else 
            logging.WARNING if level_str == 'WARNING' else
            logging.ERROR,
            f"[{level_str}] {message}"
        )
        
        # Blenderのインタラクティブコンソールに出力
        if hasattr(bpy, "ops") and hasattr(bpy.ops, "wm") and hasattr(bpy.ops.wm, "redraw_timer"):
            print(f"[{level_str}] {message}")
    
    def export_model(self, model_name=None, export_format="fbx"):
        """
        現在選択されているオブジェクトをエクスポートする
        
        引数:
            model_name (str): エクスポートするモデル名（省略時は選択オブジェクト名）
            export_format (str): エクスポート形式 (fbx, obj, glb)
            
        戻り値:
            dict: エクスポート結果
        """
        try:
            # 選択されているオブジェクトがあるか確認
            if not bpy.context.selected_objects:
                self.report({'ERROR'}, "エクスポートするオブジェクトを選択してください")
                return {"status": "error", "message": "No objects selected"}
            
            # モデル名が指定されていない場合は選択オブジェクト名を使用
            if not model_name:
                model_name = bpy.context.selected_objects[0].name
            
            # エクスポートパスを設定
            file_extension = f".{export_format.lower()}"
            export_path = os.path.join(self.export_dir, f"{model_name}{file_extension}")
            
            # 現在のカーソル位置とモードを記憶
            original_cursor_location = bpy.context.scene.cursor.location.copy()
            original_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
            
            # オブジェクトモードに切り替え
            if bpy.context.object and original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # エクスポート処理
            if export_format.lower() == "fbx":
                bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True,
                    global_scale=1.0,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_NONE',
                    bake_space_transform=False,
                    object_types={'MESH', 'ARMATURE'},
                    use_mesh_modifiers=True,
                    mesh_smooth_type='OFF',
                    use_mesh_edges=False,
                    path_mode='AUTO'
                )
            elif export_format.lower() == "obj":
                bpy.ops.export_scene.obj(
                    filepath=export_path,
                    use_selection=True,
                    global_scale=1.0,
                    path_mode='AUTO'
                )
            elif export_format.lower() == "glb":
                bpy.ops.export_scene.gltf(
                    filepath=export_path,
                    export_format='GLB',
                    use_selection=True
                )
            else:
                self.report({'ERROR'}, f"未サポートのエクスポート形式: {export_format}")
                return {"status": "error", "message": f"Unsupported export format: {export_format}"}
            
            # カーソル位置とモードを元に戻す
            bpy.context.scene.cursor.location = original_cursor_location
            if bpy.context.object and original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=original_mode)
            
            # エクスポート成功を報告
            self.report({'INFO'}, f"{model_name}を{export_format}形式でエクスポートしました: {export_path}")
            logger.info(f"モデル'{model_name}'を'{export_path}'にエクスポートしました")
            
            return {
                "status": "success",
                "export_info": {
                    "model_name": model_name,
                    "format": export_format,
                    "path": export_path
                }
            }
        
        except Exception as e:
            logger.exception(f"エクスポート中にエラーが発生しました: {str(e)}")
            self.report({'ERROR'}, f"エクスポート中にエラーが発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def create_simple_model(self, model_type="cube", model_name=None, location=(0, 0, 0), scale=(1, 1, 1)):
        """
        シンプルなモデルを作成する
        
        引数:
            model_type (str): モデルタイプ (cube, sphere, cylinder, etc.)
            model_name (str): モデル名（省略時は自動生成）
            location (tuple): 位置座標
            scale (tuple): スケール
            
        戻り値:
            dict: 作成結果
        """
        try:
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
            elif model_type.lower() == "sword":
                # 剣のような形状を作成（簡易版）
                self._create_sword_model(model_name, location)
            else:
                self.report({'ERROR'}, f"未サポートのモデルタイプ: {model_type}")
                return {"status": "error", "message": f"Unsupported model type: {model_type}"}
            
            # 作成したオブジェクトを取得
            obj = bpy.context.active_object
            
            # オブジェクト名を設定
            obj.name = model_name
            
            # スケールを設定
            obj.scale = mathutils.Vector(scale)
            
            # 作成成功を報告
            self.report({'INFO'}, f"{model_name}を作成しました")
            
            return {
                "status": "success",
                "model_info": {
                    "name": model_name,
                    "type": model_type,
                    "location": location,
                    "scale": scale
                }
            }
        
        except Exception as e:
            logger.exception(f"モデル作成中にエラーが発生しました: {str(e)}")
            self.report({'ERROR'}, f"モデル作成中にエラーが発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _create_sword_model(self, model_name, location):
        """
        簡易的な剣モデルを作成する内部メソッド
        
        引数:
            model_name (str): モデル名
            location (tuple): 位置座標
        """
        # まず刀身（長い直方体）を作成
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        blade = bpy.context.active_object
        blade.name = f"{model_name}_blade"
        blade.scale = mathutils.Vector((0.1, 0.1, 1.0))
        
        # 刀の先端を尖らせる（モディファイア適用）
        bpy.ops.object.modifier_add(type='TAPER')
        blade.modifiers["Taper"].object = blade
        blade.modifiers["Taper"].factor = 0.5
        
        # ガード（横棒）を作成
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(location[0], location[1], location[2] - 0.8))
        guard = bpy.context.active_object
        guard.name = f"{model_name}_guard"
        guard.scale = mathutils.Vector((0.4, 0.05, 0.05))
        
        # グリップ（柄）を作成
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05, 
            depth=0.4, 
            location=(location[0], location[1], location[2] - 1.0)
        )
        grip = bpy.context.active_object
        grip.name = f"{model_name}_grip"
        
        # ポンメル（柄の先端）を作成
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.07, 
            location=(location[0], location[1], location[2] - 1.2)
        )
        pommel = bpy.context.active_object
        pommel.name = f"{model_name}_pommel"
        
        # 全てのパーツを選択
        blade.select_set(True)
        guard.select_set(True)
        grip.select_set(True)
        pommel.select_set(True)
        
        # 結合
        bpy.ops.object.join()
        bpy.context.active_object.name = model_name
    
    def apply_material(self, obj_name, material_name, color=(0.8, 0.8, 0.8, 1.0), 
                       metallic=0.0, roughness=0.5, specular=0.5):
        """
        オブジェクトにマテリアルを適用する
        
        引数:
            obj_name (str): オブジェクト名
            material_name (str): マテリアル名
            color (tuple): RGBA色
            metallic (float): メタリック度
            roughness (float): ラフネス
            specular (float): スペキュラ強度
            
        戻り値:
            dict: 適用結果
        """
        try:
            # オブジェクトが存在するか確認
            if obj_name not in bpy.data.objects:
                self.report({'ERROR'}, f"オブジェクト '{obj_name}' が見つかりません")
                return {"status": "error", "message": f"Object '{obj_name}' not found"}
            
            obj = bpy.data.objects[obj_name]
            
            # マテリアルが既に存在するか確認し、なければ作成
            if material_name not in bpy.data.materials:
                mat = bpy.data.materials.new(name=material_name)
                mat.use_nodes = True
                
                # ノードの取得
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    # マテリアルプロパティの設定
                    bsdf.inputs['Base Color'].default_value = color
                    bsdf.inputs['Metallic'].default_value = metallic
                    bsdf.inputs['Roughness'].default_value = roughness
                    bsdf.inputs['Specular'].default_value = specular
            else:
                mat = bpy.data.materials[material_name]
            
            # オブジェクトにマテリアルを割り当て
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
            
            # 適用成功を報告
            self.report({'INFO'}, f"{obj_name}に{material_name}マテリアルを適用しました")
            
            return {
                "status": "success",
                "material_info": {
                    "object": obj_name,
                    "material": material_name,
                    "color": color,
                    "metallic": metallic,
                    "roughness": roughness
                }
            }
        
        except Exception as e:
            logger.exception(f"マテリアル適用中にエラーが発生しました: {str(e)}")
            self.report({'ERROR'}, f"マテリアル適用中にエラーが発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}

    def send_to_ue5(self, model_name, export_format="fbx"):
        """
        モデルをUE5に送信する
        
        引数:
            model_name (str): モデル名
            export_format (str): エクスポート形式
            
        戻り値:
            dict: 送信結果
        """
        try:
            # まずモデルをエクスポート
            export_result = self.export_model(model_name, export_format)
            
            if export_result["status"] != "success":
                return export_result
            
            export_path = export_result["export_info"]["path"]
            
            # MCPサーバーを通じてUE5にインポートコマンドを送信
            response = requests.post(
                f"{self.server_url}/unreal/command",
                json={
                    "command": "import_asset",
                    "params": {
                        "path": export_path,
                        "destination": f"/Game/Assets/{model_name}"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                
                if status == "success":
                    self.report({'INFO'}, f"{model_name}をUE5に正常に送信しました")
                    return {
                        "status": "success",
                        "message": f"Model {model_name} successfully imported to UE5",
                        "asset_info": result.get("asset_info", {})
                    }
                else:
                    self.report({'ERROR'}, f"UE5へのインポートに失敗しました: {result.get('message', '')}")
                    return {
                        "status": "error",
                        "message": result.get("message", "Unknown error during UE5 import")
                    }
            else:
                self.report({'ERROR'}, f"UE5コマンド送信に失敗しました: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Failed to send command to UE5: HTTP {response.status_code}"
                }
        
        except Exception as e:
            logger.exception(f"UE5送信中にエラーが発生しました: {str(e)}")
            self.report({'ERROR'}, f"UE5送信中にエラーが発生しました: {str(e)}")
            return {"status": "error", "message": str(e)}

# Blenderのメインインタラクティブモードで実行
def run():
    """
    統合をテストするための実行関数
    """
    integration = BlenderMCPIntegration()
    
    # MCPサーバーへの接続をテスト
    if not integration.connect_to_server():
        return
    
    # シンプルなモデルを作成
    sword_result = integration.create_simple_model("sword", "GameSword", (0, 0, 0))
    
    if sword_result["status"] != "success":
        return
    
    # マテリアルを適用
    material_result = integration.apply_material(
        "GameSword", 
        "MetalSwordMaterial", 
        color=(0.7, 0.7, 0.9, 1.0),
        metallic=0.9,
        roughness=0.1
    )
    
    if material_result["status"] != "success":
        return
    
    # UE5に送信
    ue5_result = integration.send_to_ue5("GameSword", "fbx")
    
    print(f"\nBlender-MCP統合テスト結果: {ue5_result['status']}")
    print(f"メッセージ: {ue5_result.get('message', '')}")

# スクリプトが直接実行された場合にのみ実行
if __name__ == "__main__":
    run() 
