// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MCPGameplayComponent.h"
#include "MCPShooterEnemy.generated.h"

class UStaticMeshComponent;
class UFloatingPawnMovement;
class USceneComponent;
class AMCPShooterProjectile;

/** 敵が破壊されたときのデリゲート */
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnEnemyDestroyedSignature, class AMCPShooterEnemy*, DestroyedEnemy);

/**
 * シューティングゲームの敵キャラクター
 *
 * このクラスは敵の宇宙船を表現します。
 * 自動で移動し、プレイヤーに向かって攻撃を行います。
 */
UCLASS()
class SPACESHOOTERGAME_API AMCPShooterEnemy : public APawn
{
	GENERATED_BODY()

public:
	/**
	 * コンストラクタ
	 * 敵キャラクターの初期設定を行います
	 */
	AMCPShooterEnemy();

	/**
	 * 射撃を行う関数
	 * プロジェクタイルを発射します
	 */
	UFUNCTION(BlueprintCallable, Category = "Shooting")
	void Fire();

	/**
	 * プレイヤーの方向に移動する関数
	 * @param PlayerLocation プレイヤーの位置
	 */
	UFUNCTION(BlueprintCallable, Category = "Movement")
	void MoveTowardsPlayer(const FVector& PlayerLocation);

	/**
	 * 体力値を設定する関数
	 * @param NewHealth 新しい体力値
	 */
	UFUNCTION(BlueprintCallable, Category = "Health")
	void SetHealth(float NewHealth);

	/**
	 * 体力値を取得する関数
	 * @return 現在の体力値
	 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Health")
	float GetHealth() const { return Health; }

	/**
	 * ダメージを受けた時の処理
	 * @param DamageAmount 受けるダメージ量
	 * @param DamageEvent ダメージイベント
	 * @param EventInstigator ダメージを与えたコントローラー
	 * @param DamageCauser ダメージを与えたアクター
	 * @return 実際に適用されたダメージ量
	 */
	virtual float TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

	/** 敵が破壊されたときに呼ばれるデリゲート */
	UPROPERTY(BlueprintAssignable, Category = "MCP|Shooter")
	FOnEnemyDestroyedSignature OnEnemyDestroyed;

	/** 敵が攻撃可能かどうか */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
	bool CanAttack() const;

	/** 敵の攻撃を実行 */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	void Attack();

	/** 敵の移動速度を設定 */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	void SetMoveSpeed(float NewSpeed);

	/** 敵の得点を取得 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
	int32 GetScoreValue() const { return ScoreValue; }

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
	 * 射撃タイマーのハンドラ
	 */
	void FireTimerHandler();

	/**
	 * 移動タイマーのハンドラ
	 */
	void MoveTimerHandler();

	/**
	 * 敵が破壊されたときの処理
	 */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	void HandleDestruction();

	/**
	 * 敵の衝突処理
	 */
	UFUNCTION()
	void OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);

	/** MCPゲームプレイコンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP")
	UMCPGameplayComponent* MCPComponent;

	/** 敵機体のメッシュコンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UStaticMeshComponent* EnemyMeshComponent;

	/** 移動コンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UFloatingPawnMovement* MovementComponent;

	/** 発射位置コンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	USceneComponent* ProjectileSpawnPoint;

	/** 発射する弾丸のクラス */
	UPROPERTY(EditDefaultsOnly, Category = "Shooting")
	TSubclassOf<AMCPShooterProjectile> ProjectileClass;

	/** 体力値 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Health", meta = (AllowPrivateAccess = "true"))
	float Health;

	/** 最大体力値 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Health", meta = (AllowPrivateAccess = "true"))
	float MaxHealth;

	/** 射撃間隔（秒） */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Shooting", meta = (AllowPrivateAccess = "true"))
	float FireInterval;

	/** 移動速度 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Movement", meta = (AllowPrivateAccess = "true"))
	float MoveSpeed;

	/** 射撃タイマーハンドル */
	FTimerHandle FireTimerHandle;

	/** 移動タイマーハンドル */
	FTimerHandle MoveTimerHandle;

	/** 得点価値 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "MCP|Shooter")
	int32 ScoreValue;

public:
	/** コンポーネントのゲッター */
	FORCEINLINE UStaticMeshComponent* GetEnemyMeshComponent() const { return EnemyMeshComponent; }
	FORCEINLINE UFloatingPawnMovement* GetMovementComponent() const { return MovementComponent; }
}; 
