// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "MCPGameplayComponent.h"
#include "MCPShooterProjectile.generated.h"

class UStaticMeshComponent;
class USphereComponent;

/**
 * シューティングゲームの弾丸クラス
 *
 * このクラスはプレイヤーと敵の両方が発射する弾を表現します。
 * 移動と衝突判定を担当します。
 */
UCLASS()
class SPACESHOOTERGAME_API AMCPShooterProjectile : public AActor
{
	GENERATED_BODY()
	
public:	
	/**
	 * コンストラクタ
	 * 弾丸の初期設定を行います
	 */
	AMCPShooterProjectile();

	/**
	 * ダメージ量の取得
	 * @return 弾丸が与えるダメージ量
	 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Shooting")
	float GetDamage() const { return Damage; }

	/**
	 * ダメージ量の設定
	 * @param NewDamage 新しいダメージ量
	 */
	UFUNCTION(BlueprintCallable, Category = "Shooting")
	void SetDamage(float NewDamage) { Damage = NewDamage; }

	/** プロジェクタイルが敵のものかを設定 */
	UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
	void SetIsEnemyProjectile(bool bNewIsEnemyProjectile);

	/** プロジェクタイルが敵のものかを取得 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
	bool IsEnemyProjectile() const { return bIsEnemyProjectile; }

	/**
	 * 毎フレーム呼び出される関数
	 * @param DeltaTime 前フレームからの経過時間
	 */
	virtual void Tick(float DeltaTime) override;

	/**
	 * 衝突時のイベントハンドラ
	 * @param HitComp 衝突したコンポーネント
	 * @param OtherActor 衝突した相手のアクター
	 * @param OtherComp 衝突した相手のコンポーネント
	 * @param NormalImpulse 衝突の力
	 * @param Hit 衝突情報
	 */
	UFUNCTION()
	void OnHit(UPrimitiveComponent* HitComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);

protected:
	/**
	 * ゲーム開始時に呼び出される関数
	 */
	virtual void BeginPlay() override;

	/** プロジェクタイルの見た目をBlenderアセットで設定 */
	void SetupProjectileMesh();

	/** MCPゲームプレイコンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP")
	UMCPGameplayComponent* MCPComponent;

	/** 弾丸のメッシュコンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UStaticMeshComponent* ProjectileMesh;

	/** 衝突判定用のスフィアコンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	USphereComponent* CollisionComponent;

	/** 弾丸の移動コンポーネント */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UProjectileMovementComponent* ProjectileMovement;

	/** 弾丸が与えるダメージ量 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Shooting", meta = (AllowPrivateAccess = "true"))
	float Damage;

	/** 弾丸の寿命（秒） */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Shooting", meta = (AllowPrivateAccess = "true"))
	float Lifetime;

	/** 敵のプロジェクタイルかどうか */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Projectile")
	bool bIsEnemyProjectile;

public:
	/** コンポーネントのゲッター */
	FORCEINLINE UStaticMeshComponent* GetProjectileMesh() const { return ProjectileMesh; }
	FORCEINLINE UProjectileMovementComponent* GetProjectileMovement() const { return ProjectileMovement; }
}; 
