// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MCPGameplayComponent.h"
#include "MCPShooterCharacter.generated.h"

class UStaticMeshComponent;
class UCameraComponent;
class USceneComponent;
class UFloatingPawnMovement;
class AMCPShooterProjectile;

/**
 * シューティングゲームのプレイヤーキャラクター
 *
 * このクラスはプレイヤーが操作する宇宙船を表現します。
 * 移動機能と射撃機能を提供します。
 */
UCLASS()
class SPACESHOOTERGAME_API AMCPShooterCharacter : public APawn
{
	GENERATED_BODY()

public:
	/**
	 * コンストラクタ
	 * キャラクターの初期設定を行います
	 */
	AMCPShooterCharacter();

	/**
	 * 射撃を行う関数
	 * プロジェクタイルを発射します
	 */
	void Fire();

	/** 体力値を取得 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
	float GetHealth() const { return Health; }

	/** 体力値を設定 */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	void SetHealth(float NewHealth);

	/** ダメージを受ける */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	virtual float TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

	/** 射撃速度を設定する */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	void SetFireRate(float NewFireRate);

	/** 射撃が可能かどうか */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
	bool CanFire() const;

protected:
	/**
	 * ゲーム開始時に呼び出される関数
	 */
	virtual void BeginPlay() override;

	/**
	 * 毎フレーム呼び出される関数
	 * @param DeltaTime 前フレームからの経過時間
	 */
	virtual void Tick(float DeltaTime) override;

	/**
	 * 入力と処理をバインドする関数
	 * @param PlayerInputComponent 入力コンポーネント
	 */
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	/** 前後移動入力処理 */
	void MoveForward(float Value);

	/** 左右移動入力処理 */
	void MoveRight(float Value);

	/** プロジェクタイルのクラス */
	UPROPERTY(EditDefaultsOnly, Category = "Shooting")
	TSubclassOf<AMCPShooterProjectile> ProjectileClass;

	/** 射撃位置の参照 */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Shooting")
	USceneComponent* ProjectileSpawnPoint;

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
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	UStaticMeshComponent* ShipMeshComponent;

	/** カメラコンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* CameraComponent;

	/** 移動コンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UFloatingPawnMovement* MovementComponent;

public:
	/** コンポーネントのゲッター */
	FORCEINLINE UStaticMeshComponent* GetShipMeshComponent() const { return ShipMeshComponent; }
	FORCEINLINE UCameraComponent* GetCameraComponent() const { return CameraComponent; }
	FORCEINLINE UFloatingPawnMovement* GetMovementComponent() const { return MovementComponent; }
}; 
