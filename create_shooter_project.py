#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UE5シューティングゲームプロジェクト作成スクリプト

このスクリプトは、UE5を使用してシューティングゲームプロジェクトを
一から作成し、基本的なゲームプレイ要素を実装します。
"""

import os
import sys
import subprocess
import time
import shutil
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_shooter_project")

# 設定
PROJECT_NAME = "SpaceShooterGame"
PROJECT_DIR = "/Users/tacyan/Documents/SpaceShooterGame2"
PROJECT_PATH = os.path.join(PROJECT_DIR, f"{PROJECT_NAME}.uproject")
UE5_PATH = "/Users/Shared/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
UE5_TEMPLATE = "TP_Blank"  # 空のテンプレート

# エクスポートとインポートディレクトリ
EXPORTS_DIR = "./exports"
IMPORTS_DIR = "./imports"
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(IMPORTS_DIR, exist_ok=True)

def run_cmd(cmd, desc=None):
    """コマンドを実行する"""
    if desc:
        logger.info(desc)
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            shell=isinstance(cmd, str)
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"コマンド実行エラー: {stderr.decode()}")
            return False
        return True
    except Exception as e:
        logger.error(f"コマンド実行例外: {str(e)}")
        return False

def create_project():
    """UE5プロジェクトを作成する"""
    if os.path.exists(PROJECT_PATH):
        logger.warning(f"プロジェクト '{PROJECT_PATH}' は既に存在します。既存のプロジェクトを使用します。")
        return True
    
    logger.info(f"UE5プロジェクト '{PROJECT_NAME}' を作成しています...")
    
    # プロジェクトディレクトリを作成
    os.makedirs(PROJECT_DIR, exist_ok=True)
    
    # UE5を使用してプロジェクトを作成
    cmd = [
        UE5_PATH,
        "-createproject",
        "-projectname", PROJECT_NAME,
        "-templatename", UE5_TEMPLATE,
        "-projectpath", PROJECT_DIR,
        "-game", "-rocket", "-nologo"
    ]
    
    if not run_cmd(cmd, f"UE5でプロジェクト '{PROJECT_NAME}' を作成しています..."):
        logger.error("UE5プロジェクトの作成に失敗しました。")
        return False
    
    logger.info(f"UE5プロジェクト '{PROJECT_NAME}' の作成に成功しました。")
    return True

def copy_models():
    """Blenderで作成したモデルをプロジェクトにコピーする"""
    if not os.path.exists(EXPORTS_DIR):
        logger.error(f"エクスポートディレクトリが見つかりません: {EXPORTS_DIR}")
        return False
    
    models = {
        "PlayerShip.fbx": "Content/ShooterGame/Assets/PlayerShip.fbx",
        "EnemyShip.fbx": "Content/ShooterGame/Assets/EnemyShip.fbx",
        "Projectile.fbx": "Content/ShooterGame/Assets/Projectile.fbx",
        "PowerUp.fbx": "Content/ShooterGame/Assets/PowerUp.fbx"
    }
    
    # 必要なディレクトリを作成
    os.makedirs(os.path.join(PROJECT_DIR, "Content/ShooterGame/Assets"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "Content/ShooterGame/Blueprints"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "Content/ShooterGame/Maps"), exist_ok=True)
    
    success = True
    for source_name, dest_path in models.items():
        source_path = os.path.join(EXPORTS_DIR, source_name)
        dest_full_path = os.path.join(PROJECT_DIR, dest_path)
        
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_full_path)
                logger.info(f"モデルをコピーしました: {source_path} -> {dest_full_path}")
            except Exception as e:
                logger.error(f"モデルコピー中にエラーが発生しました: {str(e)}")
                success = False
        else:
            logger.warning(f"モデルが見つかりません: {source_path}")
            success = False
    
    return success

def setup_cpp_module():
    """C++モジュールをセットアップする"""
    # ソースディレクトリを作成
    source_dir = os.path.join(PROJECT_DIR, "Source", PROJECT_NAME)
    os.makedirs(source_dir, exist_ok=True)
    
    # モジュール定義ファイルを作成
    build_cs = os.path.join(source_dir, f"{PROJECT_NAME}.Build.cs")
    with open(build_cs, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;

public class SpaceShooterGame : ModuleRules
{
    public SpaceShooterGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    
        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core", 
            "CoreUObject", 
            "Engine", 
            "InputCore",
            "EnhancedInput"
        });

        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}""")
    
    # モジュールヘッダーを作成
    module_h = os.path.join(source_dir, f"{PROJECT_NAME}.h")
    with open(module_h, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FSpaceShooterGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};""")
    
    # モジュール実装を作成
    module_cpp = os.path.join(source_dir, f"{PROJECT_NAME}.cpp")
    with open(module_cpp, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

#include "SpaceShooterGame.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FSpaceShooterGameModule, SpaceShooterGame, "SpaceShooterGame");

void FSpaceShooterGameModule::StartupModule()
{
    // モジュール起動時の処理
}

void FSpaceShooterGameModule::ShutdownModule()
{
    // モジュール終了時の処理
}""")
    
    # ゲームモードを作成
    gamemode_h = os.path.join(source_dir, f"{PROJECT_NAME}GameMode.h")
    with open(gamemode_h, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "SpaceShooterGameGameMode.generated.h"

UCLASS()
class SPACESHOOTERGAME_API ASpaceShooterGameGameMode : public AGameModeBase
{
    GENERATED_BODY()
    
public:
    ASpaceShooterGameGameMode();
    
    // スコア管理
    UPROPERTY(BlueprintReadWrite, Category = "Game")
    int32 Score;
    
    // 敵生成間隔
    UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Game")
    float EnemySpawnInterval;
    
    // 敵生成最大数
    UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Game")
    int32 MaxEnemies;
    
    // スコア加算
    UFUNCTION(BlueprintCallable, Category = "Game")
    void AddScore(int32 ScoreToAdd);
};""")
    
    # ゲームモード実装を作成
    gamemode_cpp = os.path.join(source_dir, f"{PROJECT_NAME}GameMode.cpp")
    with open(gamemode_cpp, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

#include "SpaceShooterGameGameMode.h"

ASpaceShooterGameGameMode::ASpaceShooterGameGameMode()
{
    // デフォルト値の設定
    Score = 0;
    EnemySpawnInterval = 2.0f;
    MaxEnemies = 10;
}

void ASpaceShooterGameGameMode::AddScore(int32 ScoreToAdd)
{
    Score += ScoreToAdd;
}""")
    
    # ターゲットファイル作成
    target_cs = os.path.join(PROJECT_DIR, "Source", f"{PROJECT_NAME}.Target.cs")
    with open(target_cs, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;
using System.Collections.Generic;

public class SpaceShooterGameTarget : TargetRules
{
    public SpaceShooterGameTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V4;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("SpaceShooterGame");
    }
}""")
    
    # エディターターゲットファイル作成
    editor_target_cs = os.path.join(PROJECT_DIR, "Source", f"{PROJECT_NAME}Editor.Target.cs")
    with open(editor_target_cs, "w") as f:
        f.write("""// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;
using System.Collections.Generic;

public class SpaceShooterGameEditorTarget : TargetRules
{
    public SpaceShooterGameEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V4;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("SpaceShooterGame");
    }
}""")
    
    return True

def create_bp_player_ship():
    """PlayerShipブループリントの実装を作成するためのダミーファイル"""
    blueprint_dir = os.path.join(PROJECT_DIR, "Content/ShooterGame/Blueprints")
    os.makedirs(blueprint_dir, exist_ok=True)
    
    # Blueprintの設計を.txtファイルとして保存（あとでUE5で実装するための参考）
    with open(os.path.join(blueprint_dir, "BP_PlayerShip_Design.txt"), "w") as f:
        f.write("""PlayerShipブループリント設計:

コンポーネント:
1. StaticMesh - プレイヤー宇宙船モデル
2. FloatingPawnMovement - 移動コンポーネント
3. SphericalComponent - コリジョン
4. CameraComponent - プレイヤーカメラ
5. ParticleSystem - エンジンエフェクト

変数:
- MoveSpeed (float) - 移動速度
- RotationSpeed (float) - 回転速度
- FireRate (float) - 発射速度
- Health (float) - 体力
- ProjectileClass (TSubclassOf<Actor>) - 発射する弾のクラス

関数:
- MoveForward(float AxisValue) - 前後移動
- MoveRight(float AxisValue) - 左右移動
- Fire() - 弾を発射
- TakeDamage(float DamageAmount) - ダメージ処理
- CollectPowerUp(PowerUpType Type) - パワーアップ収集

イベントグラフ:
- Event BeginPlay: 初期化処理
- Event Tick: 毎フレーム処理
- Input Events: 入力イベント処理
""")
    
    return True

def create_bp_enemy_ship():
    """EnemyShipブループリントの実装を作成するためのダミーファイル"""
    blueprint_dir = os.path.join(PROJECT_DIR, "Content/ShooterGame/Blueprints")
    os.makedirs(blueprint_dir, exist_ok=True)
    
    with open(os.path.join(blueprint_dir, "BP_EnemyShip_Design.txt"), "w") as f:
        f.write("""EnemyShipブループリント設計:

コンポーネント:
1. StaticMesh - 敵宇宙船モデル
2. FloatingPawnMovement - 移動コンポーネント
3. SphericalComponent - コリジョン
4. ParticleSystem - エンジンエフェクト

変数:
- MoveSpeed (float) - 移動速度
- RotationSpeed (float) - 回転速度
- FireRate (float) - 発射速度
- Health (float) - 体力
- DetectionRadius (float) - プレイヤー検出半径
- ProjectileClass (TSubclassOf<Actor>) - 発射する弾のクラス
- ScoreValue (int) - 撃墜時のスコア

関数:
- MoveTowardsPlayer() - プレイヤーに向かって移動
- FireAtPlayer() - プレイヤーに向かって発射
- TakeDamage(float DamageAmount) - ダメージ処理
- Die() - 撃墜時の処理

イベントグラフ:
- Event BeginPlay: 初期化処理
- Event Tick: プレイヤー追尾とAI処理
- Timer Events: 定期的な発射処理
""")
    
    return True

def create_bp_projectile():
    """Projectileブループリントの実装を作成するためのダミーファイル"""
    blueprint_dir = os.path.join(PROJECT_DIR, "Content/ShooterGame/Blueprints")
    os.makedirs(blueprint_dir, exist_ok=True)
    
    with open(os.path.join(blueprint_dir, "BP_Projectile_Design.txt"), "w") as f:
        f.write("""Projectileブループリント設計:

コンポーネント:
1. StaticMesh - 弾モデル
2. ProjectileMovement - 弾の移動コンポーネント
3. SphereCollision - 衝突判定
4. ParticleSystem - 飛行時のエフェクト
5. ParticleSystem - 衝突時のエフェクト

変数:
- Damage (float) - 与えるダメージ量
- Speed (float) - 速度
- LifeSpan (float) - 存在時間

関数:
- OnHit(Actor OtherActor) - 衝突時の処理
- Explode() - 爆発エフェクト再生と消滅

イベントグラフ:
- Event BeginPlay: 初期化と自動消滅タイマー設定
- Event Hit: 衝突判定と処理
""")
    
    return True

def create_bp_power_up():
    """PowerUpブループリントの実装を作成するためのダミーファイル"""
    blueprint_dir = os.path.join(PROJECT_DIR, "Content/ShooterGame/Blueprints")
    os.makedirs(blueprint_dir, exist_ok=True)
    
    with open(os.path.join(blueprint_dir, "BP_PowerUp_Design.txt"), "w") as f:
        f.write("""PowerUpブループリント設計:

コンポーネント:
1. StaticMesh - パワーアップモデル
2. SphereCollision - 収集判定
3. RotatingMovement - 回転アニメーション
4. PointLight - 発光エフェクト
5. ParticleSystem - 収集時のエフェクト

変数:
- PowerUpType (Enum) - パワーアップの種類（速度アップ、攻撃力アップなど）
- PowerUpAmount (float) - 効果量
- Duration (float) - 効果持続時間

関数:
- Collect(PlayerShip Collector) - プレイヤーへの効果適用
- ActivateEffect() - エフェクト有効化
- DeactivateEffect() - エフェクト無効化

イベントグラフ:
- Event BeginPlay: 初期化と浮遊アニメーション開始
- Event ActorBeginOverlap: プレイヤーとの接触判定と収集処理
- Timer Events: 浮遊アニメーションの更新
""")
    
    return True

def create_game_level():
    """ゲームレベルのプレースホルダーを作成"""
    maps_dir = os.path.join(PROJECT_DIR, "Content/ShooterGame/Maps")
    os.makedirs(maps_dir, exist_ok=True)
    
    with open(os.path.join(maps_dir, "ShooterGameLevel_Design.txt"), "w") as f:
        f.write("""ShooterGameLevelの設計:

アクター配置:
1. PlayerStart - 座標(0, 0, 100)
2. EnemyShip_1 - 座標(1000, 500, 100)
3. EnemyShip_2 - 座標(-500, 1200, 100)
4. EnemyShip_3 - 座標(800, -700, 100)
5. EnemyShip_4 - 座標(-1000, -500, 100)
6. EnemyShip_5 - 座標(0, 1500, 100)
7. PowerUp_1 - 座標(500, 0, 100)
8. PowerUp_2 - 座標(-700, 300, 100)
9. PowerUp_3 - 座標(200, -900, 100)
10. SkyLight - 環境光源
11. DirectionalLight - 主光源

ゲーム設定:
- GameMode: BP_ShooterGameMode
- DefaultPawn: BP_PlayerShip
- HUD: BP_ShooterHUD

レベル設定:
- ワールドの大きさ: 5000 x 5000 x 1000
- 背景: 宇宙空間テクスチャ
- エフェクト: 星のパーティクル
""")
    
    return True

def create_readme():
    """READMEファイルを作成する"""
    readme_path = os.path.join(PROJECT_DIR, "README.md")
    with open(readme_path, "w") as f:
        f.write(f"""# {PROJECT_NAME}

シンプルな3Dシューティングゲームプロジェクト。

## 操作方法

- W/S: 前後移動
- A/D: 左右移動
- マウス: 方向転換
- 左クリック: 発射

## ゲームの目的

敵宇宙船を撃破してスコアを稼ぎ、パワーアップを集めて能力を強化しましょう。

## 実装手順

1. UE5エディタでプロジェクトを開く
2. 以下のブループリントを実装:
   - BP_PlayerShip
   - BP_EnemyShip
   - BP_Projectile
   - BP_PowerUp
   - BP_ShooterGameMode
   - BP_ShooterHUD
3. ShooterGameLevelマップを作成し、敵とパワーアップを配置
4. ゲームモードとHUDを設定して実行

## 技術的な詳細

各ブループリントの実装詳細は、Content/ShooterGame/Blueprints/ディレクトリ内の設計ファイルを参照してください。
""")
    
    return True

def main():
    """メイン実行関数"""
    logger.info("===== UE5シューティングゲームプロジェクト作成を開始 =====")
    
    # プロジェクト作成
    if not create_project():
        logger.error("プロジェクト作成に失敗しました。終了します。")
        return
    
    # C++モジュールセットアップ
    if not setup_cpp_module():
        logger.error("C++モジュールのセットアップに失敗しました。")
    
    # モデルファイルをコピー
    copy_models()
    
    # ブループリント設計ファイル作成
    create_bp_player_ship()
    create_bp_enemy_ship()
    create_bp_projectile()
    create_bp_power_up()
    
    # ゲームレベル設計
    create_game_level()
    
    # READMEファイル作成
    create_readme()
    
    logger.info(f"プロジェクトの初期設定が完了しました: {PROJECT_PATH}")
    logger.info("UE5エディタでプロジェクトを開き、ブループリントを実装してゲームを完成させてください。")
    logger.info("===== プロジェクト作成完了 =====")

if __name__ == "__main__":
    main() 
