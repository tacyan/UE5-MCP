#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
簡易宇宙船モデル作成・エクスポートスクリプト

Blenderを使用してシンプルな宇宙船モデルを作成し、
FBX形式でエクスポートするスクリプト。

使用方法:
  blender --background --python create_simple_model.py
"""

import bpy
import os
import sys
import math

# エクスポートディレクトリを設定
EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def clean_scene():
    """シーンをクリアする"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # コレクションもクリア
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)

def create_player_ship():
    """プレイヤー宇宙船モデルを作成する"""
    # メインボディ（円錐を使用）
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0.2, depth=2.0, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "PlayerShipBody"
    body.rotation_euler[0] = math.radians(90)  # X軸を中心に90度回転
    
    # 翼を追加
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0.7, 0, -0.3))
    wing_right = bpy.context.active_object
    wing_right.name = "WingRight"
    wing_right.scale = (1.0, 0.5, 0.1)
    
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(-0.7, 0, -0.3))
    wing_left = bpy.context.active_object
    wing_left.name = "WingLeft"
    wing_left.scale = (1.0, 0.5, 0.1)
    
    # エンジン
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.5, location=(0, 0, -1.0))
    engine = bpy.context.active_object
    engine.name = "Engine"
    engine.rotation_euler[0] = math.radians(90)  # X軸を中心に90度回転
    
    # コックピット
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0.3, 0.2))
    cockpit = bpy.context.active_object
    cockpit.name = "Cockpit"
    cockpit.scale = (0.7, 0.7, 0.5)
    
    # すべてのパーツを選択
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    wing_right.select_set(True)
    wing_left.select_set(True)
    engine.select_set(True)
    cockpit.select_set(True)
    
    # アクティブオブジェクトをボディに設定
    bpy.context.view_layer.objects.active = body
    
    # オブジェクトを結合
    bpy.ops.object.join()
    
    # 名前を設定
    bpy.context.active_object.name = "PlayerShip"
    
    # スムーズシェーディング適用
    bpy.ops.object.shade_smooth()
    
    return bpy.context.active_object

def create_enemy_ship():
    """敵宇宙船モデルを作成する"""
    # メインボディ（円錐の組み合わせ）
    bpy.ops.mesh.primitive_cone_add(radius1=0.6, radius2=0.3, depth=1.5, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "EnemyShipBody"
    body.rotation_euler[0] = math.radians(90)  # X軸を中心に90度回転
    
    # 翼を追加（より攻撃的な形状）
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0.8, 0, 0))
    wing_right = bpy.context.active_object
    wing_right.name = "WingRight"
    wing_right.scale = (0.8, 0.3, 0.1)
    wing_right.rotation_euler[2] = math.radians(-30)  # Z軸を中心に回転
    
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(-0.8, 0, 0))
    wing_left = bpy.context.active_object
    wing_left.name = "WingLeft"
    wing_left.scale = (0.8, 0.3, 0.1)
    wing_left.rotation_euler[2] = math.radians(30)  # Z軸を中心に回転
    
    # 武器
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, location=(0.5, 0.5, 0.2))
    weapon_right = bpy.context.active_object
    weapon_right.name = "WeaponRight"
    weapon_right.rotation_euler[0] = math.radians(90)  # X軸を中心に90度回転
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, location=(-0.5, 0.5, 0.2))
    weapon_left = bpy.context.active_object
    weapon_left.name = "WeaponLeft"
    weapon_left.rotation_euler[0] = math.radians(90)  # X軸を中心に90度回転
    
    # すべてのパーツを選択
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    wing_right.select_set(True)
    wing_left.select_set(True)
    weapon_right.select_set(True)
    weapon_left.select_set(True)
    
    # アクティブオブジェクトをボディに設定
    bpy.context.view_layer.objects.active = body
    
    # オブジェクトを結合
    bpy.ops.object.join()
    
    # 名前を設定
    bpy.context.active_object.name = "EnemyShip"
    
    # スムーズシェーディング適用
    bpy.ops.object.shade_smooth()
    
    return bpy.context.active_object

def create_projectile():
    """弾丸モデルを作成する"""
    # 弾体（細長い楕円体）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, 0))
    projectile = bpy.context.active_object
    projectile.name = "Projectile"
    projectile.scale = (0.2, 0.2, 1.0)
    
    # スムーズシェーディング適用
    bpy.ops.object.shade_smooth()
    
    return projectile

def create_powerup():
    """パワーアップアイテムを作成する"""
    # ベースとなる球体
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 0, 0))
    powerup = bpy.context.active_object
    powerup.name = "PowerUp"
    
    # 装飾用リング
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.05, location=(0, 0, 0))
    ring = bpy.context.active_object
    ring.name = "PowerUpRing"
    
    # 90度回転させた2つ目のリング
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.05, location=(0, 0, 0))
    ring2 = bpy.context.active_object
    ring2.name = "PowerUpRing2"
    ring2.rotation_euler[0] = math.radians(90)  # X軸を中心に90度回転
    
    # すべてのパーツを選択
    bpy.ops.object.select_all(action='DESELECT')
    powerup.select_set(True)
    ring.select_set(True)
    ring2.select_set(True)
    
    # アクティブオブジェクトを本体に設定
    bpy.context.view_layer.objects.active = powerup
    
    # オブジェクトを結合
    bpy.ops.object.join()
    
    # 名前を設定
    bpy.context.active_object.name = "PowerUp"
    
    # スムーズシェーディング適用
    bpy.ops.object.shade_smooth()
    
    return powerup

def export_model(obj, export_format="fbx"):
    """モデルをエクスポートする"""
    model_name = obj.name
    export_path = os.path.join(EXPORT_DIR, f"{model_name}.{export_format.lower()}")
    
    print(f"エクスポート: {model_name} -> {export_path}")
    
    # 選択をクリアして対象オブジェクトのみ選択
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # エクスポート
    if export_format.lower() == "fbx":
        bpy.ops.export_scene.fbx(
            filepath=export_path,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            bake_space_transform=True,
            object_types={'MESH'},
            use_mesh_modifiers=True,
            mesh_smooth_type='OFF',
            use_mesh_edges=False,
            path_mode='AUTO'
        )
    elif export_format.lower() == "obj":
        bpy.ops.export_scene.obj(
            filepath=export_path,
            use_selection=True,
            global_scale=1.0
        )
    else:
        print(f"未サポートのエクスポート形式: {export_format}")
        return False
    
    print(f"{model_name}をエクスポートしました: {export_path}")
    return export_path

def main():
    """メイン実行関数"""
    print("シンプル宇宙船モデル作成開始")
    
    # シーンをクリア
    clean_scene()
    
    # モデルを作成してエクスポート
    print("プレイヤー宇宙船モデルを作成しています...")
    player_ship = create_player_ship()
    export_model(player_ship, "fbx")
    
    # シーンをクリア
    clean_scene()
    
    # 敵宇宙船を作成
    print("敵宇宙船モデルを作成しています...")
    enemy_ship = create_enemy_ship()
    export_model(enemy_ship, "fbx")
    
    # シーンをクリア
    clean_scene()
    
    # 弾丸を作成
    print("弾丸モデルを作成しています...")
    projectile = create_projectile()
    export_model(projectile, "fbx")
    
    # シーンをクリア
    clean_scene()
    
    # パワーアップを作成
    print("パワーアップモデルを作成しています...")
    powerup = create_powerup()
    export_model(powerup, "fbx")
    
    print("すべてのモデル作成が完了しました")

if __name__ == "__main__":
    main() 
