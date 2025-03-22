// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MCPGameplayComponent.h"
#include "MCPShooterCharacter.generated.h"

/**
 * シューティングゲーム用プレイヤーキャラクタークラス
 * 
 * このクラスはプレイヤーが操作する宇宙船を実装します。
 * MCPフレームワークを使用してBlenderからインポートされたアセットを活用します。
 */
UCLASS()
class MCPSHOOTERGAME_API AMCPShooterCharacter : public ACharacter
{
    GENERATED_BODY()
    
public:
    /** コンストラクタ */
    AMCPShooterCharacter();
    
    /** ティック関数 */
    virtual void Tick(float DeltaTime) override;
    
    /** インプット設定 */
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    
    /** 体力値を取得 */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
    float GetHealth() const { return Health; }
    
    /** 体力値を設定 */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void SetHealth(float NewHealth);
    
    /** ダメージを受ける */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    virtual float TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;
    
    /** 射撃を行う */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void Fire();
    
    /** 射撃速度を設定する */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void SetFireRate(float NewFireRate);
    
    /** 射撃が可能かどうか */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
    bool CanFire() const;
    
protected:
    /** ゲーム開始時の初期化 */
    virtual void BeginPlay() override;
    
    /** 前後移動入力処理 */
    void MoveForward(float Value);
    
    /** 左右移動入力処理 */
    void MoveRight(float Value);
    
    /** プロジェクタイルのクラス */
    UPROPERTY(EditDefaultsOnly, Category = "Shooting")
    TSubclassOf<class AActor> ProjectileClass;
    
    /** 射撃位置の参照 */
    UPROPERTY(VisibleDefaultsOnly, Category = "Shooting")
    class USceneComponent* GunLocation;
    
    /** MCPゲームプレイコンポーネント */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP")
    UMCPGameplayComponent* MCPComponent;
    
    /** 体力値 */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "MCP|Shooter")
    float Health;
    
    /** 最大体力値 */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "MCP|Shooter")
    float MaxHealth;
    
    /** 射撃速度（秒間射撃回数） */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "MCP|Shooter")
    float FireRate;
    
    /** 射撃間隔（秒） */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP|Shooter")
    float FireInterval;
    
    /** 最後に射撃した時間 */
    float LastFireTime;
    
    /** 移動速度 */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "MCP|Shooter")
    float MoveSpeed;
    
    /** 敵との衝突時のダメージ */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "MCP|Shooter")
    float CollisionDamage;
    
    /** プレイヤーの見た目をBlenderアセットで設定 */
    void SetupPlayerMesh();
    
    /** プレイヤーのメッシュコンポーネント */
    UPROPERTY(VisibleDefaultsOnly, BlueprintReadOnly, Category = "Mesh")
    UStaticMeshComponent* ShipMeshComponent;
}; 
