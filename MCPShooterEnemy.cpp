// Copyright MCP Framework. All Rights Reserved.

#include "MCPShooterEnemy.h"
#include "MCPShooterCharacter.h"
#include "MCPShooterGameMode.h"
#include "MCPAssetManager.h"
#include "MCPShooterProjectile.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/FloatingPawnMovement.h"
#include "UObject/ConstructorHelpers.h"
#include "Components/SceneComponent.h"
#include "Kismet/KismetMathLibrary.h"
#include "TimerManager.h"

AMCPShooterEnemy::AMCPShooterEnemy()
    : Health(100.0f)
    , MaxHealth(100.0f)
    , MoveSpeed(200.0f)
    , AttackDamage(10.0f)
    , AttackInterval(3.0f)
    , LastAttackTime(0.0f)
    , ScoreValue(100)
{
    // ティックを有効化
    PrimaryActorTick.bCanEverTick = true;
    
    // 敵のルートコンポーネントとなるメッシュコンポーネントを作成
    EnemyMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("EnemyMeshComponent"));
    RootComponent = EnemyMeshComponent;
    
    // 衝突設定
    EnemyMeshComponent->SetCollisionProfileName(TEXT("EnemyProfile"));
    EnemyMeshComponent->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    
    // 衝突イベントをバインド
    EnemyMeshComponent->OnComponentHit.AddDynamic(this, &AMCPShooterEnemy::OnHit);
    
    // 射撃位置コンポーネントの作成
    ProjectileSpawnPoint = CreateDefaultSubobject<USceneComponent>(TEXT("ProjectileSpawnPoint"));
    ProjectileSpawnPoint->SetupAttachment(EnemyMeshComponent);
    ProjectileSpawnPoint->SetRelativeLocation(FVector(100.0f, 0.0f, 0.0f));
    
    // MCPコンポーネントの作成
    MCPComponent = CreateDefaultSubobject<UMCPGameplayComponent>(TEXT("MCPComponent"));
    
    // メッシュを設定
    static ConstructorHelpers::FObjectFinder<UStaticMesh> EnemyMeshAsset(TEXT("/Game/ShooterGame/Assets/EnemyShip"));
    if (EnemyMeshAsset.Succeeded())
    {
        EnemyMeshComponent->SetStaticMesh(EnemyMeshAsset.Object);
    }
    
    // タグを追加
    Tags.Add(TEXT("Enemy"));
    
    // 移動コンポーネントを作成
    MovementComponent = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("MovementComponent"));
    MovementComponent->MaxSpeed = MoveSpeed;
    
    // デフォルトのプロジェクタイルクラス
    static ConstructorHelpers::FClassFinder<AActor> ProjectileClassFinder(TEXT("/Game/Blueprints/BP_MCPShooterProjectile"));
    if (ProjectileClassFinder.Succeeded())
    {
        ProjectileClass = ProjectileClassFinder.Class;
    }
}

void AMCPShooterEnemy::BeginPlay()
{
    Super::BeginPlay();
    
    // 体力を最大値に設定
    Health = MaxHealth;
    
    // 敵のメッシュを設定
    SetupEnemyMesh();
    
    // 最初の攻撃時間を記録
    LastAttackTime = GetWorld()->GetTimeSeconds();
    
    // タイマーをセット
    GetWorldTimerManager().SetTimer(FireTimerHandle, this, &AMCPShooterEnemy::FireTimerHandler, AttackInterval, true);
    GetWorldTimerManager().SetTimer(MoveTimerHandle, this, &AMCPShooterEnemy::MoveTimerHandler, 0.1f, true);
}

void AMCPShooterEnemy::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AMCPShooterEnemy::FireTimerHandler()
{
    // 射撃を実行
    Fire();
}

void AMCPShooterEnemy::MoveTimerHandler()
{
    // プレイヤーを検索
    AActor* PlayerActor = UGameplayStatics::GetPlayerPawn(GetWorld(), 0);
    if (PlayerActor)
    {
        // プレイヤーに向かって移動
        MoveTowardsPlayer(PlayerActor->GetActorLocation());
    }
}

void AMCPShooterEnemy::Fire()
{
    // 発射位置と向きを取得
    const FVector SpawnLocation = ProjectileSpawnPoint->GetComponentLocation();
    const FRotator SpawnRotation = ProjectileSpawnPoint->GetComponentRotation();
    
    // 弾丸クラスが設定されていることを確認
    if (ProjectileClass)
    {
        // 弾丸を発射
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        SpawnParams.Instigator = GetInstigator();
        
        AMCPShooterProjectile* Projectile = GetWorld()->SpawnActor<AMCPShooterProjectile>(ProjectileClass, SpawnLocation, SpawnRotation, SpawnParams);
        if (Projectile)
        {
            // 敵の弾として設定
            Projectile->SetIsEnemyProjectile(true);
        }
    }
}

void AMCPShooterEnemy::MoveTowardsPlayer(const FVector& PlayerLocation)
{
    // プレイヤーへの方向ベクトルを計算
    FVector Direction = PlayerLocation - GetActorLocation();
    Direction.Z = 0.0f; // 高さは無視
    
    // 方向を正規化
    if (Direction.SizeSquared() > 0.0f)
    {
        Direction.Normalize();
        
        // 移動方向を設定
        AddMovementInput(Direction, MoveSpeed * 0.01f);
        
        // 方向に向きを変える
        FRotator TargetRotation = Direction.Rotation();
        SetActorRotation(FMath::RInterpTo(GetActorRotation(), TargetRotation, GetWorld()->GetDeltaSeconds(), 2.0f));
    }
}

float AMCPShooterEnemy::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    
    if (ActualDamage > 0.0f)
    {
        // 体力を減少
        SetHealth(Health - ActualDamage);
        
        // ダメージログ
        UE_LOG(LogTemp, Display, TEXT("敵が %f ダメージを受けました。残り体力: %f"), ActualDamage, Health);
    }
    
    return ActualDamage;
}

void AMCPShooterEnemy::SetHealth(float NewHealth)
{
    Health = FMath::Clamp(NewHealth, 0.0f, MaxHealth);
    
    // 体力が0になったら敵を破壊
    if (Health <= 0.0f)
    {
        HandleDestruction();
    }
}

void AMCPShooterEnemy::HandleDestruction()
{
    // 敵が破壊されたことをゲームモードに通知
    AMCPShooterGameMode* GameMode = Cast<AMCPShooterGameMode>(UGameplayStatics::GetGameMode(GetWorld()));
    if (GameMode)
    {
        GameMode->AddScore(ScoreValue);
    }
    
    // 敵が破壊されたイベントを発行
    OnEnemyDestroyed.Broadcast(this);
    
    // アクターを破壊
    Destroy();
}

void AMCPShooterEnemy::OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
    // プレイヤーとの衝突を処理
    AMCPShooterCharacter* Player = Cast<AMCPShooterCharacter>(OtherActor);
    if (Player)
    {
        // プレイヤーにダメージを与える
        float DamageToPlayer = AttackDamage * 2.0f;  // 衝突時は通常攻撃の2倍のダメージ
        FDamageEvent DamageEvent;
        Player->TakeDamage(DamageToPlayer, DamageEvent, nullptr, this);
        
        // 敵自身も破壊
        HandleDestruction();
    }
}

void AMCPShooterEnemy::SetupEnemyMesh()
{
    // MCPアセットマネージャーを使ってBlenderからインポートしたメッシュを設定
    if (MCPComponent)
    {
        // EnemyShipアセットをロード
        MCPComponent->LoadBlenderAsset("/Game/BlenderAssets/EnemyShip", 
            UMCPGameplayComponent::FOnAssetLoaded::CreateLambda([this](bool bSuccess) {
                if (bSuccess)
                {
                    // アセットロード成功
                    UE_LOG(LogTemp, Log, TEXT("敵シップアセットのロードに成功しました"));
                    
                    // メッシュアセットを取得して設定
                    UObject* Asset = LoadObject<UObject>(nullptr, TEXT("/Game/BlenderAssets/EnemyShip"));
                    UStaticMesh* ShipMesh = Cast<UStaticMesh>(Asset);
                    if (ShipMesh)
                    {
                        EnemyMeshComponent->SetStaticMesh(ShipMesh);
                        UE_LOG(LogTemp, Log, TEXT("敵シップメッシュを設定しました"));
                    }
                    else
                    {
                        UE_LOG(LogTemp, Warning, TEXT("EnemyShipメッシュアセットが見つかりませんでした"));
                    }
                }
                else
                {
                    // アセットロード失敗
                    UE_LOG(LogTemp, Warning, TEXT("敵シップアセットのロードに失敗しました"));
                }
            })
        );
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MCPコンポーネントが初期化されていません"));
    }
}

bool AMCPShooterEnemy::CanAttack() const
{
    // ここでは常に攻撃可能とする
    return true;
}

void AMCPShooterEnemy::Attack()
{
    // 射撃を実行
    Fire();
}

void AMCPShooterEnemy::SetMoveSpeed(float NewSpeed)
{
    MoveSpeed = FMath::Max(0.0f, NewSpeed);
    
    // 移動コンポーネントの速度も更新
    if (MovementComponent)
    {
        MovementComponent->MaxSpeed = MoveSpeed;
    }
} 
