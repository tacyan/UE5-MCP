#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲーム用Blender自動モデリングスクリプト

このスクリプトは、Blenderを使用してシューティングゲームに必要な
基本的な3Dモデルを作成し、MCPサーバー経由でUE5に送信します。

作成するモデル:
- プレイヤー宇宙船
- 敵宇宙船（複数種類）
- 弾丸
- パワーアップアイテム

使用方法:
  python blender_shooter_game.py
"""

import os
import sys
import json
import time
import logging
import requests
import subprocess
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shooter_game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("blender_shooter_game")

# MCPサーバー設定
MCP_SERVER = "http://127.0.0.1:8080"

# 必要なディレクトリの作成
EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

class BlenderShooterGameModeler:
    """Blenderでシューティングゲーム用モデルを作成するクラス"""
    
    def __init__(self):
        """初期化"""
        self.blender_path = self._get_blender_path()
        self.server_url = MCP_SERVER
        
        # モデル名とエクスポートパスを保持する辞書
        self.models = {}
    
    def _get_blender_path(self):
        """Blenderのパスを取得する"""
        # 環境変数から取得
        blender_path = os.getenv("BLENDER_PATH", "")
        
        # 環境変数にない場合はデフォルトパスを使用
        if not blender_path:
            if sys.platform == "darwin":  # macOS
                blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
            elif sys.platform == "win32":  # Windows
                blender_path = r"C:\Program Files\Blender Foundation\Blender\blender.exe"
            else:  # Linux その他
                blender_path = "blender"
        
        logger.info(f"Blenderパス: {blender_path}")
        return blender_path
    
    def check_mcp_server(self):
        """MCPサーバーの接続を確認する"""
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    logger.info("MCPサーバーに接続しました")
                    return True
                else:
                    logger.error(f"MCPサーバーのステータスが異常: {data.get('status')}")
                    return False
            else:
                logger.error(f"MCPサーバーへの接続に失敗しました: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"MCPサーバーへの接続中にエラーが発生しました: {str(e)}")
            return False
    
    def create_player_ship(self):
        """プレイヤー宇宙船モデルを作成するBlenderスクリプト"""
        model_name = "PlayerShip"
        export_path = os.path.join(EXPORTS_DIR, model_name + '.fbx')
        script = f"""
import bpy
import math
import os

# シーンをクリア
bpy.ops.wm.read_factory_settings(use_empty=True)

# プレイヤー宇宙船の作成
def create_player_ship():
    # ベースの立方体を作成
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    ship_body = bpy.context.active_object
    ship_body.name = "ShipBody"
    
    # 船体の形状を調整
    ship_body.scale = (1.5, 2.0, 0.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 前方を先細りにする
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 前部の頂点を選択して移動
    for v in ship_body.data.vertices:
        if v.co.y > 0:
            v.select = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(0.6, 1, 1))
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 翼を作成
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    wing = bpy.context.active_object
    wing.name = "Wing"
    wing.scale = (3.0, 1.2, 0.1)
    wing.location = (0, 0, 0)
    
    # コックピットを作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.6, location=(0, 0.5, 0.3))
    cockpit = bpy.context.active_object
    cockpit.name = "Cockpit"
    cockpit.rotation_euler = (math.pi/2, 0, 0)
    cockpit.scale = (0.6, 0.6, 0.6)
    
    # 推進器を作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4, location=(0, -1.5, 0))
    engine = bpy.context.active_object
    engine.name = "Engine"
    engine.rotation_euler = (math.pi/2, 0, 0)
    
    # サイドエンジンを作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(0.8, -1.3, 0))
    engine_right = bpy.context.active_object
    engine_right.name = "EngineRight"
    engine_right.rotation_euler = (math.pi/2, 0, 0)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(-0.8, -1.3, 0))
    engine_left = bpy.context.active_object
    engine_left.name = "EngineLeft"
    engine_left.rotation_euler = (math.pi/2, 0, 0)
    
    # すべてのオブジェクトを選択
    ship_body.select_set(True)
    wing.select_set(True)
    cockpit.select_set(True)
    engine.select_set(True)
    engine_right.select_set(True)
    engine_left.select_set(True)
    
    # アクティブオブジェクトを設定
    bpy.context.view_layer.objects.active = ship_body
    
    # オブジェクトを結合
    bpy.ops.object.join()
    
    # 名前を設定
    bpy.context.active_object.name = "PlayerShip"
    
    # 青い艦体マテリアルを作成
    mat = bpy.data.materials.new(name="ShipMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.1, 0.2, 0.8, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.2
    
    # マテリアルを割り当て
    ship_body.data.materials.append(mat)
    
    return ship_body

# モデルを作成
player_ship = create_player_ship()

# 原点を設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# FBXにエクスポート
export_path = r"{os.path.join(EXPORTS_DIR, model_name + '.fbx')}"
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

print(f"プレイヤー宇宙船モデルを作成しました: {export_path}")
"""
        self._run_blender_script(script, model_name)
        self.models["player_ship"] = model_name
        return model_name
    
    def create_enemy_ship(self):
        """敵宇宙船モデルを作成するBlenderスクリプト"""
        model_name = "EnemyShip"
        export_path = os.path.join(EXPORTS_DIR, model_name + '.fbx')
        script = f"""
import bpy
import math
import os

# シーンをクリア
bpy.ops.wm.read_factory_settings(use_empty=True)

# 敵宇宙船の作成
def create_enemy_ship():
    # ベースの立方体を作成
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    ship_body = bpy.context.active_object
    ship_body.name = "EnemyShipBody"
    
    # 船体の形状を調整
    ship_body.scale = (1.2, 1.0, 0.3)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 前方を先細りにする
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 前部の頂点を選択して移動
    for v in ship_body.data.vertices:
        if v.co.y > 0:
            v.select = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(0.7, 1.2, 0.7))
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 翼を作成
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    wing = bpy.context.active_object
    wing.name = "EnemyWing"
    wing.scale = (2.0, 0.8, 0.1)
    wing.location = (0, -0.2, 0)
    
    # 砲台を作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4, location=(0, 0.5, -0.2))
    turret = bpy.context.active_object
    turret.name = "EnemyTurret"
    turret.rotation_euler = (0, 0, 0)
    
    # 推進器を作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(0.6, -0.8, 0))
    engine_right = bpy.context.active_object
    engine_right.name = "EnemyEngineRight"
    engine_right.rotation_euler = (math.pi/2, 0, 0)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(-0.6, -0.8, 0))
    engine_left = bpy.context.active_object
    engine_left.name = "EnemyEngineLeft"
    engine_left.rotation_euler = (math.pi/2, 0, 0)
    
    # すべてのオブジェクトを選択
    ship_body.select_set(True)
    wing.select_set(True)
    turret.select_set(True)
    engine_right.select_set(True)
    engine_left.select_set(True)
    
    # アクティブオブジェクトを設定
    bpy.context.view_layer.objects.active = ship_body
    
    # オブジェクトを結合
    bpy.ops.object.join()
    
    # 名前を設定
    bpy.context.active_object.name = "EnemyShip"
    
    # 赤い艦体マテリアルを作成
    mat = bpy.data.materials.new(name="EnemyShipMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.7
    bsdf.inputs['Roughness'].default_value = 0.3
    
    # マテリアルを割り当て
    ship_body.data.materials.append(mat)
    
    return ship_body

# モデルを作成
enemy_ship = create_enemy_ship()

# 原点を設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# FBXにエクスポート
export_path = r"{os.path.join(EXPORTS_DIR, model_name + '.fbx')}"
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

print(f"敵宇宙船モデルを作成しました: {export_path}")
"""
        self._run_blender_script(script, model_name)
        self.models["enemy_ship"] = model_name
        return model_name
    
    def create_projectile(self):
        """弾丸モデルを作成するBlenderスクリプト"""
        model_name = "Projectile"
        export_path = os.path.join(EXPORTS_DIR, model_name + '.fbx')
        script = f"""
import bpy
import os

# シーンをクリア
bpy.ops.wm.read_factory_settings(use_empty=True)

# 弾丸の作成
def create_projectile():
    # ベースのカプセルを作成
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
    projectile = bpy.context.active_object
    projectile.name = "Projectile"
    projectile.scale = (0.2, 0.5, 0.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 弾丸用マテリアルを作成（エネルギー弾のような発光マテリアル）
    mat = bpy.data.materials.new(name="ProjectileMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.0, 0.8, 1.0, 1.0)  # 青い光
    bsdf.inputs['Emission'].default_value = (0.0, 0.8, 1.0, 1.0)    # 発光
    bsdf.inputs['Emission Strength'].default_value = 5.0           # 発光強度
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.0
    
    # マテリアルを割り当て
    projectile.data.materials.append(mat)
    
    return projectile

# モデルを作成
projectile = create_projectile()

# 原点を設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# FBXにエクスポート
export_path = r"{os.path.join(EXPORTS_DIR, model_name + '.fbx')}"
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

print(f"弾丸モデルを作成しました: {export_path}")
"""
        self._run_blender_script(script, model_name)
        self.models["projectile"] = model_name
        return model_name
    
    def create_powerup(self):
        """パワーアップアイテムモデルを作成するBlenderスクリプト"""
        model_name = "PowerUp"
        export_path = os.path.join(EXPORTS_DIR, model_name + '.fbx')
        script = f"""
import bpy
import math
import os

# シーンをクリア
bpy.ops.wm.read_factory_settings(use_empty=True)

# パワーアップアイテムの作成
def create_powerup():
    # ベースの立方体を作成
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.5, subdivisions=2, location=(0, 0, 0))
    powerup = bpy.context.active_object
    powerup.name = "PowerUpCore"
    
    # リングを作成
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.8, 
        minor_radius=0.05, 
        major_segments=32, 
        minor_segments=12,
        location=(0, 0, 0)
    )
    ring = bpy.context.active_object
    ring.name = "PowerUpRing"
    
    # 内側のリングを作成
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.6, 
        minor_radius=0.03, 
        major_segments=32, 
        minor_segments=12,
        location=(0, 0, 0),
        rotation=(math.pi/2, 0, 0)
    )
    inner_ring = bpy.context.active_object
    inner_ring.name = "PowerUpInnerRing"
    
    # 発光コアマテリアルを作成
    core_mat = bpy.data.materials.new(name="PowerUpCoreMaterial")
    core_mat.use_nodes = True
    bsdf = core_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (1.0, 0.8, 0.0, 1.0)  # 金色
    bsdf.inputs['Emission'].default_value = (1.0, 0.8, 0.0, 1.0)    # 発光
    bsdf.inputs['Emission Strength'].default_value = 3.0           # 発光強度
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.1
    
    # リングマテリアルを作成
    ring_mat = bpy.data.materials.new(name="PowerUpRingMaterial")
    ring_mat.use_nodes = True
    bsdf = ring_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.9, 1.0)  # 銀色
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.1
    
    # マテリアルを割り当て
    powerup.data.materials.append(core_mat)
    ring.data.materials.append(ring_mat)
    inner_ring.data.materials.append(ring_mat)
    
    # すべてのオブジェクトを選択
    powerup.select_set(True)
    ring.select_set(True)
    inner_ring.select_set(True)
    
    # アクティブオブジェクトを設定
    bpy.context.view_layer.objects.active = powerup
    
    # オブジェクトを結合
    bpy.ops.object.join()
    
    # 名前を設定
    bpy.context.active_object.name = "PowerUp"
    
    return powerup

# モデルを作成
powerup = create_powerup()

# 原点を設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# FBXにエクスポート
export_path = r"{os.path.join(EXPORTS_DIR, model_name + '.fbx')}"
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

print(f"パワーアップアイテムモデルを作成しました: {export_path}")
"""
        self._run_blender_script(script, model_name)
        self.models["powerup"] = model_name
        return model_name
    
    def _run_blender_script(self, script, model_name):
        """Blenderでスクリプトを実行する"""
        script_path = os.path.join(EXPORTS_DIR, f"{model_name}_script.py")
        
        # スクリプトをファイルに保存
        with open(script_path, "w") as f:
            f.write(script)
        
        # Blenderを起動してスクリプトを実行
        logger.info(f"{model_name}モデルを作成しています...")
        try:
            process = subprocess.Popen([
                self.blender_path,
                "--background",
                "--python", script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"{model_name}モデルの作成に成功しました")
                return True
            else:
                logger.error(f"{model_name}モデル作成中にエラーが発生しました: {stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Blender実行エラー: {str(e)}")
            return False
    
    def send_to_ue5(self, model_name):
        """モデルをUE5に送信する"""
        logger.info(f"{model_name}をUE5に送信しています...")
        try:
            model_path = os.path.join(EXPORTS_DIR, f"{model_name}.fbx")
            
            # MCPサーバーを通じてUE5にインポートコマンドを送信
            response = requests.post(
                f"{self.server_url}/api/unreal/execute",
                json={
                    "command": "import_asset",
                    "params": {
                        "path": model_path,
                        "destination": f"/Game/ShooterGame/Assets/{model_name}"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                
                if status == "success":
                    logger.info(f"{model_name}をUE5に正常に送信しました")
                    return True
                else:
                    logger.error(f"UE5へのインポートに失敗しました: {result.get('message', '')}")
                    return False
            else:
                logger.error(f"UE5コマンド送信に失敗しました: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"UE5送信中にエラーが発生しました: {str(e)}")
            return False
    
    def create_all_models(self):
        """すべてのモデルを作成してUE5に送信する"""
        if not self.check_mcp_server():
            logger.error("MCPサーバーに接続できません。終了します。")
            return False
        
        # 宇宙船モデルを作成
        self.create_player_ship()
        self.create_enemy_ship()
        
        # 弾丸モデルを作成
        self.create_projectile()
        
        # パワーアップモデルを作成
        self.create_powerup()
        
        # UE5に送信
        for model_type, model_name in self.models.items():
            if not self.send_to_ue5(model_name):
                logger.warning(f"{model_name}のUE5送信に失敗しました")
        
        logger.info("すべてのモデルの作成と送信が完了しました")
        return True

def main():
    """メイン実行関数"""
    logger.info("===== シューティングゲームモデラーを開始 =====")
    
    modeler = BlenderShooterGameModeler()
    success = modeler.create_all_models()
    
    if success:
        logger.info("===== シューティングゲームモデラーが完了しました =====")
        logger.info("次のステップ: UE5でゲームロジックを作成してください。")
    else:
        logger.error("シューティングゲームモデラーの実行中にエラーが発生しました")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
