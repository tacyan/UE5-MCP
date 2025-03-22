// Copyright MCP Framework. All Rights Reserved.

#include "MCPShooterProjectile.h"
#include "MCPShooterCharacter.h"
#include "MCPShooterEnemy.h"
#include "MCPAssetManager.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"

AMCPShooterProjectile::AMCPShooterProjectile()
{
	// このアクターが毎フレーム更新されるように設定
	PrimaryActorTick.bCanEverTick = true;
	
	// 衝突コンポーネントをルートとして作成
	CollisionComponent = CreateDefaultSubobject<USphereComponent>(TEXT("CollisionComponent"));
	CollisionComponent->SetSphereRadius(13.0f);
	CollisionComponent->SetCollisionProfileName(TEXT("ProjectileProfile"));
	CollisionComponent->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	RootComponent = CollisionComponent;
	
	// メッシュコンポーネントを作成
	ProjectileMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ProjectileMesh"));
	ProjectileMesh->SetupAttachment(RootComponent);
	ProjectileMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	
	// メッシュを設定
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ProjectileMeshAsset(TEXT("/Game/ShooterGame/Assets/Projectile"));
	if (ProjectileMeshAsset.Succeeded())
	{
		ProjectileMesh->SetStaticMesh(ProjectileMeshAsset.Object);
		ProjectileMesh->SetRelativeScale3D(FVector(0.2f, 0.2f, 1.0f));
	}
	
	// 移動コンポーネントを作成
	ProjectileMovement = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("ProjectileMovement"));
	ProjectileMovement->SetUpdatedComponent(RootComponent);
	ProjectileMovement->InitialSpeed = 2000.0f;
	ProjectileMovement->MaxSpeed = 2000.0f;
	ProjectileMovement->bRotationFollowsVelocity = true;
	ProjectileMovement->ProjectileGravityScale = 0.0f;
	
	// デフォルト値設定
	Damage = 10.0f;
	Lifetime = 5.0f;
	bIsEnemyProjectile = false;
	
	// MCPコンポーネント設定
	MCPComponent = CreateDefaultSubobject<UMCPGameplayComponent>(TEXT("MCPComponent"));
}

void AMCPShooterProjectile::BeginPlay()
{
	Super::BeginPlay();
	
	// コリジョンコンポーネントのヒットイベントを登録
	if (CollisionComponent)
	{
		CollisionComponent->OnComponentHit.AddDynamic(this, &AMCPShooterProjectile::OnHit);
	}
	
	// 寿命を設定
	SetLifeSpan(Lifetime);
	
	// 見た目をセットアップ
	SetupProjectileMesh();
}

void AMCPShooterProjectile::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AMCPShooterProjectile::OnHit(UPrimitiveComponent* HitComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
	// 自分自身や発射者との衝突は無視
	AActor* MyOwner = GetOwner();
	if (OtherActor && OtherActor != this && OtherActor != MyOwner)
	{
		// 敵のプロジェクタイルの場合はプレイヤーにのみダメージ
		if (bIsEnemyProjectile)
		{
			AMCPShooterCharacter* PlayerCharacter = Cast<AMCPShooterCharacter>(OtherActor);
			if (PlayerCharacter)
			{
				// ダメージ適用
				FDamageEvent DamageEvent;
				PlayerCharacter->TakeDamage(Damage, DamageEvent, nullptr, this);
			}
		}
		// プレイヤーのプロジェクタイルの場合は敵にのみダメージ
		else
		{
			AMCPShooterEnemy* Enemy = Cast<AMCPShooterEnemy>(OtherActor);
			if (Enemy)
			{
				// ダメージ適用
				FDamageEvent DamageEvent;
				Enemy->TakeDamage(Damage, DamageEvent, nullptr, this);
			}
		}
		
		// エフェクト再生（必要に応じて）
		UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), nullptr, GetActorLocation(), GetActorRotation());
		
		// サウンド再生（必要に応じて）
		UGameplayStatics::PlaySoundAtLocation(this, nullptr, GetActorLocation());
		
		// 弾を破壊
		Destroy();
	}
}

void AMCPShooterProjectile::SetupProjectileMesh()
{
	// Blenderからインポートしたメッシュアセットを検索
	FString MeshPath = TEXT("/Game/ShooterGame/Assets/Projectile");
	UStaticMesh* ProjectileStaticMesh = LoadObject<UStaticMesh>(nullptr, *MeshPath);
	
	// メッシュがロードできたら適用
	if (ProjectileStaticMesh && ProjectileMesh)
	{
		ProjectileMesh->SetStaticMesh(ProjectileStaticMesh);
		
		// マテリアルを適用
		FString MaterialPath = TEXT("/Game/ShooterGame/Assets/Materials/ProjectileMaterial");
		UMaterialInterface* ProjectileMaterial = LoadObject<UMaterialInterface>(nullptr, *MaterialPath);
		if (ProjectileMaterial)
		{
			ProjectileMesh->SetMaterial(0, ProjectileMaterial);
		}
	}
}

void AMCPShooterProjectile::SetIsEnemyProjectile(bool bNewIsEnemyProjectile)
{
	bIsEnemyProjectile = bNewIsEnemyProjectile;
	
	// 敵の弾の場合は色を変更
	if (bIsEnemyProjectile)
	{
		// 敵の弾は赤色に
		if (ProjectileMesh && ProjectileMesh->GetMaterial(0))
		{
			UMaterialInstanceDynamic* Material = UMaterialInstanceDynamic::Create(ProjectileMesh->GetMaterial(0), this);
			if (Material)
			{
				Material->SetVectorParameterValue(TEXT("Color"), FLinearColor::Red);
				ProjectileMesh->SetMaterial(0, Material);
			}
		}
	}
} 
