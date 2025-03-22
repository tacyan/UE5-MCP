#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲーム用3Dモデル作成スクリプト

このスクリプトは、MCPフレームワークを使用してBlenderで
シューティングゲーム用の3Dモデル（プレイヤー宇宙船、敵宇宙船、
弾丸、パワーアップアイテム）を作成し、FBXファイルとして
エクスポートします。
"""

import os
import sys
import time
import logging
import math
import random
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("create_shooter_assets.log")
    ]
)
logger = logging.getLogger("create_shooter_assets")

# エクスポートディレクトリ
EXPORT_DIR = "./exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# MCPクライアント（Blender用）のインポート
try:
    from mcp_blender_api import MCPBlenderAPI
except ImportError:
    logger.error("MCPBlenderAPIのインポートに失敗しました。パスが正しく設定されているか確認してください。")
    sys.exit(1)

class ShooterAssetCreator:
    """シューティングゲーム用アセット作成クラス"""
    
    def __init__(self):
        """初期化"""
        self.client = MCPBlenderAPI(server_url="127.0.0.1", port=8080)
        # 接続確認
        status = self.client.check_connection()
        if not status:
            logger.error(f"MCPサーバーに接続できませんでした")
            sys.exit(1)
        
        logger.info("MCPサーバーに接続しました")
        
        # シーンをクリア
        self.clear_scene()

    def clear_scene(self):
        """Blenderシーンをクリア"""
        logger.info("シーンをクリアしています...")
        result = self.client.execute_blender_code("""
import bpy

# すべてのオブジェクトを選択
bpy.ops.object.select_all(action='SELECT')
# 選択したオブジェクトを削除
bpy.ops.object.delete()

# カメラとライトを追加
bpy.ops.object.camera_add(location=(0, -10, 5), rotation=(math.radians(60), 0, 0))
bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 10))
""")
        
        if result.get("status") == "success":
            logger.info("シーンのクリアに成功しました")
        else:
            logger.error(f"シーンのクリアに失敗しました: {result}")

    def create_player_ship(self):
        """プレイヤー宇宙船のモデルを作成"""
        logger.info("プレイヤー宇宙船のモデルを作成しています...")
        
        # コードを実行して宇宙船を作成
        result = self.client.execute_blender_code("""
import bpy
import math

# 宇宙船の本体部分
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
body = bpy.context.active_object
body.name = "PlayerShipBody"
body.scale = (2.0, 1.0, 0.3)
body.location = (0, 0, 0)

# 宇宙船の前部
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.0, radius2=0, depth=2.0, location=(2.0, 0, 0))
nose = bpy.context.active_object
nose.name = "PlayerShipNose"
nose.rotation_euler = (0, math.radians(90), 0)
nose.scale = (0.5, 1.0, 0.3)

# 宇宙船の翼
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.2, 0))
wing_right = bpy.context.active_object
wing_right.name = "PlayerShipWingRight"
wing_right.scale = (1.5, 0.5, 0.1)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.2, 0))
wing_left = bpy.context.active_object
wing_left.name = "PlayerShipWingLeft"
wing_left.scale = (1.5, 0.5, 0.1)

# 宇宙船のエンジン部分
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(-1.2, 0.5, 0))
engine_right = bpy.context.active_object
engine_right.name = "PlayerShipEngineRight"
engine_right.rotation_euler = (0, math.radians(90), 0)

bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(-1.2, -0.5, 0))
engine_left = bpy.context.active_object
engine_left.name = "PlayerShipEngineLeft"
engine_left.rotation_euler = (0, math.radians(90), 0)

# コックピット
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0.5, 0, 0.3))
cockpit = bpy.context.active_object
cockpit.name = "PlayerShipCockpit"
cockpit.scale = (0.8, 0.5, 0.3)

# すべてのパーツを選択
body.select_set(True)
nose.select_set(True)
wing_right.select_set(True)
wing_left.select_set(True)
engine_right.select_set(True)
engine_left.select_set(True)
cockpit.select_set(True)

# bodyをアクティブオブジェクトに設定
bpy.context.view_layer.objects.active = body

# 結合
bpy.ops.object.join()

# 結合したオブジェクトの名前を設定
bpy.context.active_object.name = "PlayerShip"

# マテリアルを作成して適用
mat = bpy.data.materials.new(name="PlayerShipMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.0, 0.5, 1.0, 1.0)  # 青色
bsdf.inputs[7].default_value = 0.7  # メタリック

# マテリアルを適用
if bpy.context.active_object.data.materials:
    bpy.context.active_object.data.materials[0] = mat
else:
    bpy.context.active_object.data.materials.append(mat)

# 原点を中心に設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
""")
        
        if result.get("status") == "success":
            logger.info("プレイヤー宇宙船のモデル作成に成功しました")
        else:
            logger.error(f"プレイヤー宇宙船のモデル作成に失敗しました: {result}")

    def create_enemy_ship(self):
        """敵宇宙船のモデルを作成"""
        logger.info("敵宇宙船のモデルを作成しています...")
        
        # コードを実行して敵宇宙船を作成
        result = self.client.execute_blender_code("""
import bpy
import math

# 敵宇宙船の本体
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
body = bpy.context.active_object
body.name = "EnemyShipBody"
body.scale = (1.2, 1.0, 0.4)

# 敵宇宙船の上部
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 0.5))
top = bpy.context.active_object
top.name = "EnemyShipTop"
top.scale = (0.7, 0.7, 0.3)

# 敵宇宙船の翼
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.0, 0))
wing_right = bpy.context.active_object
wing_right.name = "EnemyShipWingRight"
wing_right.scale = (0.7, 0.5, 0.1)
wing_right.rotation_euler = (0, 0, math.radians(20))

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.0, 0))
wing_left = bpy.context.active_object
wing_left.name = "EnemyShipWingLeft"
wing_left.scale = (0.7, 0.5, 0.1)
wing_left.rotation_euler = (0, 0, math.radians(-20))

# 敵宇宙船の武器
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, location=(0.6, 0.4, -0.1))
weapon_right = bpy.context.active_object
weapon_right.name = "EnemyShipWeaponRight"

bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, location=(0.6, -0.4, -0.1))
weapon_left = bpy.context.active_object
weapon_left.name = "EnemyShipWeaponLeft"

# すべてのパーツを選択
body.select_set(True)
top.select_set(True)
wing_right.select_set(True)
wing_left.select_set(True)
weapon_right.select_set(True)
weapon_left.select_set(True)

# bodyをアクティブオブジェクトに設定
bpy.context.view_layer.objects.active = body

# 結合
bpy.ops.object.join()

# 結合したオブジェクトの名前を設定
bpy.context.active_object.name = "EnemyShip"

# マテリアルを作成して適用
mat = bpy.data.materials.new(name="EnemyShipMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (1.0, 0.2, 0.2, 1.0)  # 赤色
bsdf.inputs[7].default_value = 0.5  # メタリック

# マテリアルを適用
if bpy.context.active_object.data.materials:
    bpy.context.active_object.data.materials[0] = mat
else:
    bpy.context.active_object.data.materials.append(mat)

# 原点を中心に設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# オブジェクトを非表示に
bpy.context.active_object.hide_set(True)
""")
        
        if result.get("status") == "success":
            logger.info("敵宇宙船のモデル作成に成功しました")
        else:
            logger.error(f"敵宇宙船のモデル作成に失敗しました: {result}")

    def create_projectile(self):
        """弾丸のモデルを作成"""
        logger.info("弾丸のモデルを作成しています...")
        
        # コードを実行して弾丸を作成
        result = self.client.execute_blender_code("""
import bpy

# 弾丸の本体
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, 0))
proj = bpy.context.active_object
proj.name = "Projectile"

# 後部のトレイル（火花）
bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0, depth=0.5, location=(-0.25, 0, 0))
trail = bpy.context.active_object
trail.name = "ProjectileTrail"
trail.rotation_euler = (0, 1.5708, 0)  # 90度回転（ラジアン）

# 両方を選択して結合
proj.select_set(True)
trail.select_set(True)
bpy.context.view_layer.objects.active = proj
bpy.ops.object.join()

# マテリアルを作成して適用
mat = bpy.data.materials.new(name="ProjectileMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (1.0, 0.8, 0.0, 1.0)  # 黄色
bsdf.inputs[5].default_value = 1.0  # 発光効果
bsdf.inputs[7].default_value = 0.3  # メタリック

# マテリアルを適用
if bpy.context.active_object.data.materials:
    bpy.context.active_object.data.materials[0] = mat
else:
    bpy.context.active_object.data.materials.append(mat)

# 原点を中心に設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# オブジェクトを非表示に
bpy.context.active_object.hide_set(True)
""")
        
        if result.get("status") == "success":
            logger.info("弾丸のモデル作成に成功しました")
        else:
            logger.error(f"弾丸のモデル作成に失敗しました: {result}")

    def create_power_up(self):
        """パワーアップアイテムのモデルを作成"""
        logger.info("パワーアップアイテムのモデルを作成しています...")
        
        # コードを実行してパワーアップアイテムを作成
        result = self.client.execute_blender_code("""
import bpy
import math

# パワーアップのベース
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.2, location=(0, 0, 0))
base = bpy.context.active_object
base.name = "PowerUpBase"

# パワーアップのシンボル
bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.1, location=(0, 0, 0.2))
symbol = bpy.context.active_object
symbol.name = "PowerUpSymbol"

# シンボルの中央部分
bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 0.2))
center = bpy.context.active_object
center.name = "PowerUpCenter"

# すべてのパーツを選択
base.select_set(True)
symbol.select_set(True)
center.select_set(True)

# baseをアクティブオブジェクトに設定
bpy.context.view_layer.objects.active = base

# 結合
bpy.ops.object.join()

# 結合したオブジェクトの名前を設定
bpy.context.active_object.name = "PowerUp"

# マテリアルを作成して適用
mat = bpy.data.materials.new(name="PowerUpMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.0, 1.0, 0.5, 1.0)  # 緑色
bsdf.inputs[5].default_value = 0.8  # 発光効果

# マテリアルを適用
if bpy.context.active_object.data.materials:
    bpy.context.active_object.data.materials[0] = mat
else:
    bpy.context.active_object.data.materials.append(mat)

# 原点を中心に設定
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# オブジェクトを非表示に
bpy.context.active_object.hide_set(True)
""")
        
        if result.get("status") == "success":
            logger.info("パワーアップアイテムのモデル作成に成功しました")
        else:
            logger.error(f"パワーアップアイテムのモデル作成に失敗しました: {result}")

    def export_models(self):
        """モデルをFBXとしてエクスポート"""
        logger.info("モデルをFBXとしてエクスポートしています...")
        
        models = ["PlayerShip", "EnemyShip", "Projectile", "PowerUp"]
        
        for model in models:
            # モデルを表示状態に変更
            self.client.execute_blender_code(f"""
import bpy
obj = bpy.data.objects.get("{model}")
if obj:
    obj.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
""")

            # モデルをエクスポート
            export_path = os.path.join(EXPORT_DIR, f"{model}.fbx")
            abs_path = os.path.abspath(export_path)
            # バックスラッシュをスラッシュに変換してエラーを回避
            safe_path = abs_path.replace("\\", "/")
            result = self.client.execute_blender_code(f"""
import bpy
import os

# エクスポートパス
export_path = "{safe_path}"

# FBXエクスポート設定
bpy.ops.export_scene.fbx(
    filepath=export_path,
    use_selection=True,
    object_types={{'MESH'}},
    mesh_smooth_type='EDGE',
    add_leaf_bones=False,
    bake_anim=False,
    use_mesh_modifiers=True,
    axis_forward='-Z',
    axis_up='Y'
)

# エクスポート結果
if os.path.exists(export_path):
    result = f"{{model}}を{{export_path}}にエクスポートしました"
else:
    result = f"{{model}}のエクスポートに失敗しました"

result
""")
            
            if "エクスポートしました" in str(result):
                logger.info(f"{model}のエクスポートに成功しました: {export_path}")
            else:
                logger.error(f"{model}のエクスポートに失敗しました: {result}")
            
            # モデルを再度非表示に
            self.client.execute_blender_code(f"""
import bpy
obj = bpy.data.objects.get("{model}")
if obj:
    obj.hide_set(True)
""")
        
        logger.info("すべてのモデルのエクスポートが完了しました")

def main():
    """メイン実行関数"""
    logger.info("===== シューティングゲーム用3Dモデルの作成を開始します =====")
    
    creator = ShooterAssetCreator()
    
    # モデル作成
    creator.create_player_ship()
    creator.create_enemy_ship()
    creator.create_projectile()
    creator.create_power_up()
    
    # モデルをエクスポート
    creator.export_models()
    
    logger.info("===== 3Dモデルの作成が完了しました =====")

if __name__ == "__main__":
    main() 
