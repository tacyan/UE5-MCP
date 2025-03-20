#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blenderゲームオブジェクト作成スクリプト

このスクリプトはBlenderから直接実行でき、シンプルなゲームオブジェクトを
作成してFBXでエクスポートします。MCPフレームワークを使わなくても
単独で動作します。

使用方法:
1. Blenderを起動
2. スクリプトエディタでこのファイルを開く
3. 実行ボタンを押すか、Alt+Pでスクリプトを実行
"""

import bpy
import os
import math
import sys

# エクスポートディレクトリの設定
EXPORT_DIR = "./exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def clear_scene():
    """
    シーンをクリアする
    """
    # 既存のオブジェクトを削除
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # コレクションをクリア
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)
    
    # マテリアルをクリア
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def create_treasure_chest():
    """
    宝箱を作成する
    """
    # 新しいコレクションを作成
    chest_collection = bpy.data.collections.new("TreasureChest")
    bpy.context.scene.collection.children.link(chest_collection)
    
    # 箱の本体を作成
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    chest_base = bpy.context.active_object
    chest_base.name = "ChestBase"
    chest_base.scale = (1.0, 0.7, 0.5)
    chest_collection.objects.link(chest_base)
    bpy.context.scene.collection.objects.unlink(chest_base)
    
    # 箱の蓋を作成
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.0))
    chest_lid = bpy.context.active_object
    chest_lid.name = "ChestLid"
    chest_lid.scale = (1.0, 0.7, 0.1)
    # 蓋の回転軸を設定
    chest_lid.location.z = 0.8
    chest_lid.location.y = -0.7 * 0.5
    chest_collection.objects.link(chest_lid)
    bpy.context.scene.collection.objects.unlink(chest_lid)
    
    # 宝箱用マテリアルを作成
    wood_material = bpy.data.materials.new(name="WoodMaterial")
    wood_material.use_nodes = True
    bsdf = wood_material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.3, 0.1, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.7
    
    # 金属部分用マテリアルを作成
    metal_material = bpy.data.materials.new(name="MetalMaterial")
    metal_material.use_nodes = True
    bsdf = metal_material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.2, 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.2
    
    # マテリアルを適用
    chest_base.data.materials.append(wood_material)
    chest_lid.data.materials.append(wood_material)
    
    # 装飾を追加（金属部分）
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, location=(0, 0, 0.5))
    lock = bpy.context.active_object
    lock.name = "ChestLock"
    lock.rotation_euler[0] = math.radians(90)
    lock.location = (0, -0.35, 0.8)
    lock.data.materials.append(metal_material)
    chest_collection.objects.link(lock)
    bpy.context.scene.collection.objects.unlink(lock)
    
    # エッジを出すためのモディファイアを追加
    for obj in [chest_base, chest_lid]:
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.02
        bevel.segments = 3
    
    return [chest_base, chest_lid, lock]

def create_potion_bottle():
    """
    ポーション瓶を作成する
    """
    # 新しいコレクションを作成
    potion_collection = bpy.data.collections.new("PotionBottle")
    bpy.context.scene.collection.children.link(potion_collection)
    
    # 瓶の本体を作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4, location=(0, 0, 0.2))
    bottle = bpy.context.active_object
    bottle.name = "PotionBottle"
    potion_collection.objects.link(bottle)
    bpy.context.scene.collection.objects.unlink(bottle)
    
    # 瓶の首部分を作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.15, location=(0, 0, 0.475))
    neck = bpy.context.active_object
    neck.name = "BottleNeck"
    potion_collection.objects.link(neck)
    bpy.context.scene.collection.objects.unlink(neck)
    
    # 栓を作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.05, location=(0, 0, 0.575))
    cork = bpy.context.active_object
    cork.name = "BottleCork"
    potion_collection.objects.link(cork)
    bpy.context.scene.collection.objects.unlink(cork)
    
    # ガラス用マテリアルを作成
    glass_material = bpy.data.materials.new(name="GlassMaterial")
    glass_material.use_nodes = True
    bsdf = glass_material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.1, 0.5, 0.8, 0.7)  # 青いポーション
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.1
        bsdf.inputs['Transmission'].default_value = 0.8  # 透明度
        
    # コルク用マテリアルを作成
    cork_material = bpy.data.materials.new(name="CorkMaterial")
    cork_material.use_nodes = True
    bsdf = cork_material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.8, 0.5, 0.2, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.9
    
    # マテリアルを適用
    bottle.data.materials.append(glass_material)
    neck.data.materials.append(glass_material)
    cork.data.materials.append(cork_material)
    
    # エッジを滑らかにする
    for obj in [bottle, neck, cork]:
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = math.radians(60)
        
        # サブディビジョンモディファイアを追加
        subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 2
    
    return [bottle, neck, cork]

def create_game_coin():
    """
    ゲーム用コインを作成する
    """
    # 新しいコレクションを作成
    coin_collection = bpy.data.collections.new("GameCoin")
    bpy.context.scene.collection.children.link(coin_collection)
    
    # コインを作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.05, location=(0, 0, 0.025))
    coin = bpy.context.active_object
    coin.name = "Coin"
    coin_collection.objects.link(coin)
    bpy.context.scene.collection.objects.unlink(coin)
    
    # コインの装飾を作成
    bpy.ops.mesh.primitive_circle_add(radius=0.2, fill_type='NGON', location=(0, 0, 0.051))
    coin_deco = bpy.context.active_object
    coin_deco.name = "CoinDecoration"
    coin_collection.objects.link(coin_deco)
    bpy.context.scene.collection.objects.unlink(coin_deco)
    
    # 金属用マテリアルを作成
    gold_material = bpy.data.materials.new(name="GoldMaterial")
    gold_material.use_nodes = True
    bsdf = gold_material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.0, 0.8, 0.0, 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.1
        bsdf.inputs['Specular'].default_value = 0.9
    
    # マテリアルを適用
    coin.data.materials.append(gold_material)
    coin_deco.data.materials.append(gold_material)
    
    # エッジを滑らかにする
    for obj in [coin, coin_deco]:
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = math.radians(60)
        
        # ベベルモディファイアを追加
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.02
        bevel.segments = 3
    
    return [coin, coin_deco]

def export_objects(name, objects, export_format="fbx"):
    """
    オブジェクトをエクスポートする
    
    引数:
        name (str): エクスポートファイル名
        objects (list): エクスポートするオブジェクトリスト
        export_format (str): エクスポート形式
    """
    # 現在選択を解除
    bpy.ops.object.select_all(action='DESELECT')
    
    # 指定オブジェクトを選択
    for obj in objects:
        obj.select_set(True)
    
    # エクスポートパスを設定
    export_path = os.path.join(EXPORT_DIR, f"{name}.{export_format.lower()}")
    
    # エクスポート
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
    
    print(f"{name}を{export_path}にエクスポートしました")
    return export_path

def main():
    """
    メイン関数
    """
    try:
        # 開始メッセージ
        print("======================================")
        print("Blenderゲームオブジェクト作成スクリプト")
        print("======================================")
        
        # シーンをクリア
        clear_scene()
        
        # 宝箱を作成
        print("\n1. 宝箱を作成しています...")
        chest_objects = create_treasure_chest()
        export_objects("TreasureChest", chest_objects)
        
        # シーンをクリア
        clear_scene()
        
        # ポーション瓶を作成
        print("\n2. ポーション瓶を作成しています...")
        potion_objects = create_potion_bottle()
        export_objects("PotionBottle", potion_objects)
        
        # シーンをクリア
        clear_scene()
        
        # コインを作成
        print("\n3. ゲームコインを作成しています...")
        coin_objects = create_game_coin()
        export_objects("GameCoin", coin_objects)
        
        # 完了メッセージ
        print("\n======================================")
        print("すべてのオブジェクトが正常に作成され、エクスポートされました")
        print(f"エクスポート先: {os.path.abspath(EXPORT_DIR)}")
        print("======================================")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

# Blenderから直接実行された場合のみ実行
if __name__ == "__main__":
    main() 
