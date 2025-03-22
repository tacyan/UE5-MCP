// Copyright MCP Framework. All Rights Reserved.

#include "MCPShooterCharacter.h"
#include "MCPShooterProjectile.h"
#include "MCPShooterGameMode.h"
#include "MCPAssetManager.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/FloatingPawnMovement.h"
#include "UObject/ConstructorHelpers.h"
#include "TimerManager.h"
#include "MCPShooterEnemy.h"

AMCPShooterCharacter::AMCPShooterCharacter()
    : Health(100.0f)
    , MaxHealth(100.0f)
    , FireRate(2.0f)
    , LastFireTime(0.0f)
    , MoveSpeed(500.0f)
    , CollisionDamage(10.0f)
{
    // キャラクター設定
    PrimaryActorTick.bCanEverTick = true;
    
    // カプセルコンポーネントのサイズを調整
    GetCapsuleComponent()->InitCapsuleSize(50.0f, 50.0f);
    
    // 移動設定
    GetCharacterMovement()->GravityScale = 0.0f; // 宇宙空間なので重力ゼロ
    GetCharacterMovement()->MaxFlySpeed = MoveSpeed;
    GetCharacterMovement()->SetMovementMode(MOVE_Flying);
    
    // メッシュコンポーネントの作成
    ShipMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ShipMesh"));
    ShipMeshComponent->SetupAttachment(GetCapsuleComponent());
    ShipMeshComponent->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
    ShipMeshComponent->SetCollisionProfileName(TEXT("CharacterMesh"));
    
    // 射撃位置コンポーネントの作成
    GunLocation = CreateDefaultSubobject<USceneComponent>(TEXT("GunLocation"));
    GunLocation->SetupAttachment(ShipMeshComponent);
    GunLocation->SetRelativeLocation(FVector(100.0f, 0.0f, 0.0f));
    
    // カメラブームの作成
    USpringArmComponent* CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 600.0f;
    CameraBoom->SetRelativeRotation(FRotator(-30.0f, 0.0f, 0.0f));
    CameraBoom->bUsePawnControlRotation = false;
    CameraBoom->bInheritPitch = false;
    CameraBoom->bInheritRoll = false;
    CameraBoom->bInheritYaw = false;
    CameraBoom->bDoCollisionTest = false;
    
    // カメラの作成
    UCameraComponent* Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    Camera->bUsePawnControlRotation = false;
    
    // 射撃間隔を計算
    FireInterval = 1.0f / FireRate;
    
    // MCPコンポーネントの作成
    MCPComponent = CreateDefaultSubobject<UMCPGameplayComponent>(TEXT("MCPComponent"));
    
    // デフォルトのプロジェクタイルクラス
    static ConstructorHelpers::FClassFinder<AActor> ProjectileClassFinder(TEXT("/Game/Blueprints/BP_MCPShooterProjectile"));
    if (ProjectileClassFinder.Succeeded())
    {
        ProjectileClass = ProjectileClassFinder.Class;
    }
    
    // AIコントローラによる制御を無効化
    AutoPossessAI = EAutoPossessAI::Disabled;

    // 移動コンポーネントを作成
    MovementComponent = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("MovementComponent"));
    MovementComponent->MaxSpeed = 1000.0f;
}

void AMCPShooterCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    // 体力を最大値に設定
    Health = MaxHealth;
    
    // プレイヤーメッシュの設定
    SetupPlayerMesh();
    
    // 最初の射撃時間を記録
    LastFireTime = GetWorld()->GetTimeSeconds();
    
    // コリジョンイベントを登録
    if (ShipMeshComponent)
    {
        ShipMeshComponent->OnComponentHit.AddDynamic(this, &AMCPShooterCharacter::OnHit);
    }
}

void AMCPShooterCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 必要に応じて追加のティック処理
}

void AMCPShooterCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    
    // 移動入力のバインド
    PlayerInputComponent->BindAxis("MoveForward", this, &AMCPShooterCharacter::MoveForward);
    PlayerInputComponent->BindAxis("MoveRight", this, &AMCPShooterCharacter::MoveRight);
    
    // 射撃入力のバインド
    PlayerInputComponent->BindAction("Fire", IE_Pressed, this, &AMCPShooterCharacter::Fire);
}

void AMCPShooterCharacter::MoveForward(float Value)
{
    if (Value != 0.0f)
    {
        // 前後移動
        AddMovementInput(FVector(1.0f, 0.0f, 0.0f), Value);
    }
}

void AMCPShooterCharacter::MoveRight(float Value)
{
    if (Value != 0.0f)
    {
        // 左右移動
        AddMovementInput(FVector(0.0f, 1.0f, 0.0f), Value);
    }
}

void AMCPShooterCharacter::SetHealth(float NewHealth)
{
    Health = FMath::Clamp(NewHealth, 0.0f, MaxHealth);
    
    // 体力が0になったらゲームオーバー
    if (Health <= 0.0f)
    {
        // ゲームモードにゲームオーバーを通知
        AMCPShooterGameMode* GameMode = Cast<AMCPShooterGameMode>(UGameplayStatics::GetGameMode(GetWorld()));
        if (GameMode)
        {
            GameMode->GameOver();
        }
        
        // プレイヤーを非表示にする
        SetActorHiddenInGame(true);
        SetActorEnableCollision(false);
    }
}

float AMCPShooterCharacter::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    
    if (ActualDamage > 0.0f)
    {
        // 体力を減少
        SetHealth(Health - ActualDamage);
        
        // ダメージログ
        UE_LOG(LogTemp, Display, TEXT("プレイヤーが %f ダメージを受けました。残り体力: %f"), ActualDamage, Health);
    }
    
    return ActualDamage;
}

void AMCPShooterCharacter::Fire()
{
    if (CanFire())
    {
        // 射撃時間を更新
        LastFireTime = GetWorld()->GetTimeSeconds();
        
        // プロジェクタイルクラスが設定されているか確認
        if (!ProjectileClass)
        {
            UE_LOG(LogTemp, Error, TEXT("プロジェクタイルクラスが設定されていません"));
            return;
        }
        
        // 射撃位置と方向を取得
        FVector SpawnLocation = GunLocation->GetComponentLocation();
        FRotator SpawnRotation = GetActorRotation();
        
        // スポーンパラメータの設定
        FActorSpawnParameters SpawnParams;
        SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
        SpawnParams.Owner = this;
        SpawnParams.Instigator = GetInstigator();
        
        // プロジェクタイルの生成
        AActor* SpawnedProjectile = GetWorld()->SpawnActor<AActor>(ProjectileClass, SpawnLocation, SpawnRotation, SpawnParams);
        if (SpawnedProjectile)
        {
            // プロジェクタイルのログ
            UE_LOG(LogTemp, Display, TEXT("プロジェクタイルを発射しました: %s"), *SpawnedProjectile->GetName());
        }
    }
}

void AMCPShooterCharacter::SetFireRate(float NewFireRate)
{
    if (NewFireRate > 0.0f)
    {
        FireRate = NewFireRate;
        FireInterval = 1.0f / FireRate;
    }
}

bool AMCPShooterCharacter::CanFire() const
{
    // 射撃間隔をチェック
    float CurrentTime = GetWorld()->GetTimeSeconds();
    return (CurrentTime - LastFireTime >= FireInterval);
}

void AMCPShooterCharacter::SetupPlayerMesh()
{
    // MCPアセットマネージャーを使ってBlenderからインポートしたメッシュを設定
    if (MCPComponent)
    {
        // PlayerShipアセットをロード
        MCPComponent->LoadBlenderAsset("/Game/BlenderAssets/PlayerShip", 
            UMCPGameplayComponent::FOnAssetLoaded::CreateLambda([this](bool bSuccess) {
                if (bSuccess)
                {
                    // アセットロード成功
                    UE_LOG(LogTemp, Log, TEXT("プレイヤーシップアセットのロードに成功しました"));
                    
                    // メッシュアセットを取得して設定
                    UObject* Asset = LoadObject<UObject>(nullptr, TEXT("/Game/BlenderAssets/PlayerShip"));
                    UStaticMesh* ShipMesh = Cast<UStaticMesh>(Asset);
                    if (ShipMesh)
                    {
                        ShipMeshComponent->SetStaticMesh(ShipMesh);
                        UE_LOG(LogTemp, Log, TEXT("プレイヤーシップメッシュを設定しました"));
                    }
                    else
                    {
                        UE_LOG(LogTemp, Warning, TEXT("PlayerShipメッシュアセットが見つかりませんでした"));
                    }
                }
                else
                {
                    // アセットロード失敗
                    UE_LOG(LogTemp, Warning, TEXT("プレイヤーシップアセットのロードに失敗しました"));
                }
            })
        );
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MCPコンポーネントが初期化されていません"));
    }
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
