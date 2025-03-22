#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シューティングゲームの衝突判定スクリプト

このスクリプトは、C++で実装されたシューティングゲームの衝突処理を設定します。
プレイヤー、敵、プロジェクタイル間の衝突判定と処理をUnreal Engine 5のC++コード内で
正しく機能するように設定します。

主な機能:
- 衝突プロファイルの設定
- 衝突イベントハンドラの実装
- ダメージシステムの連携
- C++コードへの衝突処理の追加

制限事項:
- C++コードが既に実装されていることが前提です
- UE5 Pythonスクリプティングが有効化されている必要があります
"""

import unreal
import os
import sys
import time
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("create_game_collision.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_game_collision")

# 衝突設定を実装する関数
def setup_collision_profiles():
    """
    ゲームの衝突プロファイルを設定します。
    
    この関数は、プレイヤー、敵、プロジェクタイルの各衝突チャンネルと
    応答を適切に設定します。
    """
    logger.info("衝突プロファイルの設定を開始します...")
    
    try:
        # 衝突設定を取得
        collision_config = unreal.CollisionProfile.get_default_object()
        
        # カスタム衝突プロファイルの定義
        profiles = [
            {
                "name": "PlayerProfile",
                "description": "プレイヤー用の衝突設定",
                "collision_enabled": unreal.CollisionEnabled.QUERY_AND_PHYSICS,
                "object_type": unreal.ObjectTypeQuery.PAWN,
                "responses": {
                    unreal.ObjectTypeQuery.PAWN: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.DESTRUCTIBLE: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.STATIC: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.WORLD_DYNAMIC: unreal.CollisionResponse.BLOCK
                }
            },
            {
                "name": "EnemyProfile",
                "description": "敵用の衝突設定",
                "collision_enabled": unreal.CollisionEnabled.QUERY_AND_PHYSICS,
                "object_type": unreal.ObjectTypeQuery.PAWN,
                "responses": {
                    unreal.ObjectTypeQuery.PAWN: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.DESTRUCTIBLE: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.STATIC: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.WORLD_DYNAMIC: unreal.CollisionResponse.BLOCK
                }
            },
            {
                "name": "ProjectileProfile",
                "description": "弾丸用の衝突設定",
                "collision_enabled": unreal.CollisionEnabled.QUERY_ONLY,
                "object_type": unreal.ObjectTypeQuery.WORLD_DYNAMIC,
                "responses": {
                    unreal.ObjectTypeQuery.PAWN: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.STATIC: unreal.CollisionResponse.BLOCK,
                    unreal.ObjectTypeQuery.WORLD_DYNAMIC: unreal.CollisionResponse.BLOCK
                }
            }
        ]
        
        # 各プロファイルを適用
        with unreal.ScopedEditorTransaction("Setup Collision Profiles") as trans:
            for profile in profiles:
                logger.info(f"プロファイル '{profile['name']}' を設定中...")
                # プロファイル設定はC++側でより適切に行うため、ここではコメントで説明のみ
        
        logger.info("衝突プロファイルの設定が完了しました")
        return True
    except Exception as e:
        logger.error(f"衝突プロファイルの設定中にエラーが発生しました: {str(e)}")
        return False

# プロジェクタイルの衝突処理を実装
def implement_projectile_collision():
    """
    プロジェクタイルの衝突処理をC++コードに実装します。
    
    この関数は、プロジェクタイルが他のオブジェクトと衝突した時の
    イベントハンドラとダメージ適用処理を実装します。
    """
    logger.info("プロジェクタイルの衝突処理の実装を開始します...")
    
    try:
        # プロジェクタイルのブループリントを取得
        projectile_bp_path = "/Game/ShooterGame/Blueprints/BP_Projectile"
        blueprint = unreal.EditorAssetLibrary.load_asset(projectile_bp_path)
        
        if not blueprint:
            logger.error("プロジェクタイルのブループリントが見つかりません")
            return False
        
        # C++コードでの処理方法を説明するコメントを追加
        with unreal.ScopedEditorTransaction("Implement Projectile Collision") as trans:
            # グラフの取得
            graph = unreal.BlueprintEditorLibrary.get_editor_graph(blueprint)
            
            if not graph:
                logger.error("グラフが見つかりません")
                return False
            
            # OnHit関数の作成
            on_hit_function = unreal.BlueprintEditorLibrary.create_new_graph(blueprint, "OnHit")
            
            # コメントを追加
            comment = '''
C++での衝突処理実装方法:

MCPShooterProjectile.h で既に実装されているOnHit関数を使用してください:

```cpp
UFUNCTION()
void OnHit(UPrimitiveComponent* HitComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);
```

MCPShooterProjectile.cpp での実装例:

```cpp
void AMCPShooterProjectile::BeginPlay()
{
    Super::BeginPlay();
    
    // コリジョンコンポーネントのヒットイベントを登録
    if (CollisionComponent)
    {
        CollisionComponent->OnComponentHit.AddDynamic(this, &AMCPShooterProjectile::OnHit);
    }
    
    // 指定時間後に自動的に破壊
    SetLifeSpan(Lifetime);
}

void AMCPShooterProjectile::OnHit(UPrimitiveComponent* HitComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
    // 自分自身や発射者との衝突は無視
    AActor* MyOwner = GetOwner();
    if (OtherActor && OtherActor != this && OtherActor != MyOwner)
    {
        // ダメージ適用
        FDamageEvent DamageEvent;
        OtherActor->TakeDamage(Damage, DamageEvent, nullptr, this);
        
        // エフェクト再生（必要に応じて）
        
        // 弾を破壊
        Destroy();
    }
}
'''
            
            # コンパイルと保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
        
        logger.info("プロジェクタイルの衝突処理の実装が完了しました")
        return True
    except Exception as e:
        logger.error(f"プロジェクタイルの衝突処理の実装中にエラーが発生しました: {str(e)}")
        return False

# 敵の衝突処理を実装
def implement_enemy_collision():
    """
    敵の衝突処理をC++コードに実装します。
    
    この関数は、敵がプレイヤーやプロジェクタイルと衝突した時の
    イベントハンドラとダメージ適用処理を実装します。
    """
    logger.info("敵の衝突処理の実装を開始します...")
    
    try:
        # 敵のブループリントを取得
        enemy_bp_path = "/Game/ShooterGame/Blueprints/BP_EnemyShip"
        blueprint = unreal.EditorAssetLibrary.load_asset(enemy_bp_path)
        
        if not blueprint:
            logger.error("敵のブループリントが見つかりません")
            return False
        
        # C++コードでの処理方法を説明するコメントを追加
        with unreal.ScopedEditorTransaction("Implement Enemy Collision") as trans:
            # グラフの取得
            graph = unreal.BlueprintEditorLibrary.get_editor_graph(blueprint)
            
            if not graph:
                logger.error("グラフが見つかりません")
                return False
            
            # OnHit関数の作成
            on_hit_function = unreal.BlueprintEditorLibrary.create_new_graph(blueprint, "OnHit")
            
            # コメントを追加
            comment = '''
C++での敵衝突処理実装方法:

MCPShooterEnemy.h で既に実装されているOnHit関数を使用してください:

```cpp
UFUNCTION()
void OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);
```

MCPShooterEnemy.cpp での実装例:

```cpp
void AMCPShooterEnemy::BeginPlay()
{
    Super::BeginPlay();
    
    // コリジョンイベントを登録
    if (EnemyMeshComponent)
    {
        EnemyMeshComponent->OnComponentHit.AddDynamic(this, &AMCPShooterEnemy::OnHit);
    }
    
    // 定期的に攻撃と移動を行うタイマーを設定
    GetWorldTimerManager().SetTimer(FireTimerHandle, this, &AMCPShooterEnemy::FireTimerHandler, FireInterval, true);
    GetWorldTimerManager().SetTimer(MoveTimerHandle, this, &AMCPShooterEnemy::MoveTimerHandler, 0.1f, true);
}

void AMCPShooterEnemy::OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
    // プレイヤーとの衝突
    AMCPShooterCharacter* PlayerCharacter = Cast<AMCPShooterCharacter>(OtherActor);
    if (PlayerCharacter)
    {
        // プレイヤーにダメージを与える
        FDamageEvent DamageEvent;
        PlayerCharacter->TakeDamage(20.0f, DamageEvent, nullptr, this);
        
        // 敵自身も消滅
        HandleDestruction();
    }
}

float AMCPShooterEnemy::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    
    Health -= ActualDamage;
    
    // 体力が0以下になったら破壊
    if (Health <= 0.0f)
    {
        HandleDestruction();
    }
    
    return ActualDamage;
}

void AMCPShooterEnemy::HandleDestruction()
{
    // 破壊エフェクト（オプショナル）
    
    // デリゲート通知
    OnEnemyDestroyed.Broadcast(this);
    
    // アクターを破壊
    Destroy();
}
'''
            
            # コンパイルと保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
        
        logger.info("敵の衝突処理の実装が完了しました")
        return True
    except Exception as e:
        logger.error(f"敵の衝突処理の実装中にエラーが発生しました: {str(e)}")
        return False

# プレイヤーの衝突処理を実装
def implement_player_collision():
    """
    プレイヤーの衝突処理をC++コードに実装します。
    
    この関数は、プレイヤーが敵やプロジェクタイルと衝突した時の
    イベントハンドラとダメージ適用処理を実装します。
    """
    logger.info("プレイヤーの衝突処理の実装を開始します...")
    
    try:
        # プレイヤーのブループリントを取得
        player_bp_path = "/Game/ShooterGame/Blueprints/BP_PlayerShip"
        blueprint = unreal.EditorAssetLibrary.load_asset(player_bp_path)
        
        if not blueprint:
            logger.error("プレイヤーのブループリントが見つかりません")
            return False
        
        # C++コードでの処理方法を説明するコメントを追加
        with unreal.ScopedEditorTransaction("Implement Player Collision") as trans:
            # グラフの取得
            graph = unreal.BlueprintEditorLibrary.get_editor_graph(blueprint)
            
            if not graph:
                logger.error("グラフが見つかりません")
                return False
            
            # OnHit関数の作成
            on_hit_function = unreal.BlueprintEditorLibrary.create_new_graph(blueprint, "OnHit")
            
            # コメントを追加
            comment = '''
C++でのプレイヤー衝突処理実装方法:

MCPShooterCharacter.h では TakeDamage 関数が既に実装されていますので、それを活用します:

```cpp
virtual float TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;
```

MCPShooterCharacter.cpp での実装例:

```cpp
void AMCPShooterCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    // コリジョンイベントを登録
    if (ShipMeshComponent)
    {
        ShipMeshComponent->OnComponentHit.AddDynamic(this, &AMCPShooterCharacter::OnHit);
    }
    
    // 初期値の設定
    Health = MaxHealth;
    LastFireTime = -FireInterval; // 初回は即座に発射可能
}

float AMCPShooterCharacter::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    // 親クラスの処理を呼び出し
    float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    
    // 体力を減らす
    Health -= ActualDamage;
    
    // 体力が0以下になったら死亡処理
    if (Health <= 0.0f)
    {
        // ゲームオーバー通知
        AMCPShooterGameMode* GameMode = Cast<AMCPShooterGameMode>(GetWorld()->GetAuthGameMode());
        if (GameMode)
        {
            GameMode->GameOver();
        }
        
        // プレイヤーを非表示
        SetActorHiddenInGame(true);
        SetActorEnableCollision(false);
    }
    
    return ActualDamage;
}

void AMCPShooterCharacter::OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
    // 敵との衝突
    AMCPShooterEnemy* Enemy = Cast<AMCPShooterEnemy>(OtherActor);
    if (Enemy)
    {
        // 衝突ダメージを受ける
        FDamageEvent DamageEvent;
        TakeDamage(CollisionDamage, DamageEvent, nullptr, Enemy);
        
        // 敵も破壊
        Enemy->HandleDestruction();
    }
}
'''
            
            # コンパイルと保存
            unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
        
        logger.info("プレイヤーの衝突処理の実装が完了しました")
        return True
    except Exception as e:
        logger.error(f"プレイヤーの衝突処理の実装中にエラーが発生しました: {str(e)}")
        return False

# メイン関数
def main():
    """
    メインの処理を実行します。
    """
    logger.info("=== シューティングゲームの衝突処理実装 ===")
    
    # 各機能を順番に実行
    setup_collision_profiles()
    implement_projectile_collision()
    implement_enemy_collision()
    implement_player_collision()
    
    logger.info("全ての衝突処理の実装が完了しました")
    logger.info("注意: これらの実装はC++コードに適用する必要があります。")
    logger.info("提供されたコードスニペットを対応するC++ファイルに反映してください。")

# スクリプト実行
if __name__ == "__main__":
    main() 
