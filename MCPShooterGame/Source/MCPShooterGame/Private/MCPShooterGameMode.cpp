// Copyright MCP Framework. All Rights Reserved.

#include "MCPShooterGameMode.h"
#include "MCPShooterCharacter.h"
#include "MCPShooterEnemy.h"
#include "MCPAssetManager.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "TimerManager.h"

AMCPShooterGameMode::AMCPShooterGameMode()
    : EnemySpawnInterval(2.0f)
    , MaxEnemyCount(10)
    , CurrentScore(0)
    , CurrentEnemyCount(0)
    , bGameStarted(false)
    , bGameOver(false)
{
    // デフォルト設定
    EnemySpawnLocation = FVector(1000.0f, 0.0f, 100.0f);
    
    // デフォルトプレイヤーキャラクタークラスの設定
    static ConstructorHelpers::FClassFinder<APawn> PlayerPawnClassFinder(TEXT("/Game/Blueprints/BP_MCPShooterCharacter"));
    if (PlayerPawnClassFinder.Succeeded())
    {
        DefaultPawnClass = PlayerPawnClassFinder.Class;
    }
    
    // デフォルト敵クラスの設定
    static ConstructorHelpers::FClassFinder<AActor> EnemyClassFinder(TEXT("/Game/Blueprints/BP_MCPShooterEnemy"));
    if (EnemyClassFinder.Succeeded())
    {
        EnemyClass = EnemyClassFinder.Class;
    }
    
    // デフォルトプレイヤーコントローラクラスの設定
    static ConstructorHelpers::FClassFinder<APlayerController> PlayerControllerClassFinder(TEXT("/Game/Blueprints/BP_MCPShooterPlayerController"));
    if (PlayerControllerClassFinder.Succeeded())
    {
        PlayerControllerClass = PlayerControllerClassFinder.Class;
    }
}

void AMCPShooterGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    // Blenderアセットをロード
    LoadBlenderAssets();
    
    // ゲームをスタート
    StartGame();
}

void AMCPShooterGameMode::StartGame()
{
    if (bGameStarted || bGameOver)
    {
        return;
    }
    
    // ゲームスタートフラグを設定
    bGameStarted = true;
    bGameOver = false;
    
    // スコアをリセット
    CurrentScore = 0;
    CurrentEnemyCount = 0;
    
    // プレイヤーキャラクターをスポーン
    SpawnPlayerCharacter();
    
    // 敵のスポーンを開始
    GetWorldTimerManager().SetTimer(
        EnemySpawnTimerHandle,
        this,
        &AMCPShooterGameMode::SpawnEnemy,
        EnemySpawnInterval,
        true,
        0.5f  // 初回スポーン遅延
    );
}

void AMCPShooterGameMode::GameOver()
{
    if (!bGameStarted || bGameOver)
    {
        return;
    }
    
    // ゲームオーバーフラグを設定
    bGameOver = true;
    bGameStarted = false;
    
    // 敵のスポーンタイマーを停止
    GetWorldTimerManager().ClearTimer(EnemySpawnTimerHandle);
    
    // 現在の敵を全て削除
    TArray<AActor*> FoundEnemies;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), AMCPShooterEnemy::StaticClass(), FoundEnemies);
    
    for (AActor* Enemy : FoundEnemies)
    {
        Enemy->Destroy();
    }
    
    // ゲームオーバーメッセージをログに出力
    UE_LOG(LogTemp, Warning, TEXT("Game Over! Final Score: %d"), CurrentScore);
}

void AMCPShooterGameMode::AddScore(int32 ScoreToAdd)
{
    if (!bGameStarted || bGameOver)
    {
        return;
    }
    
    CurrentScore += ScoreToAdd;
    
    // スコアを画面に表示（実際のプロジェクトではHUDを使用）
    UE_LOG(LogTemp, Display, TEXT("Score: %d"), CurrentScore);
}

void AMCPShooterGameMode::SetEnemySpawnInterval(float NewInterval)
{
    if (NewInterval > 0.0f)
    {
        EnemySpawnInterval = NewInterval;
        
        if (bGameStarted && !bGameOver)
        {
            // すでにタイマーが動いている場合は更新
            GetWorldTimerManager().SetTimer(
                EnemySpawnTimerHandle,
                this,
                &AMCPShooterGameMode::SpawnEnemy,
                EnemySpawnInterval,
                true
            );
        }
    }
}

void AMCPShooterGameMode::SpawnEnemy()
{
    if (!bGameStarted || bGameOver)
    {
        return;
    }
    
    // 最大敵数をチェック
    if (CurrentEnemyCount >= MaxEnemyCount)
    {
        return;
    }
    
    // 敵クラスが設定されているか確認
    if (!EnemyClass)
    {
        UE_LOG(LogTemp, Error, TEXT("敵クラスが設定されていません"));
        return;
    }
    
    // スポーン位置をランダムに調整
    FVector SpawnLocation = EnemySpawnLocation;
    SpawnLocation.Y = FMath::RandRange(-800.0f, 800.0f);
    
    // スポーン回転を設定
    FRotator SpawnRotation = FRotator(0.0f, 180.0f, 0.0f);  // プレイヤーの方を向くように
    
    // 敵をスポーン
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
    
    AActor* SpawnedEnemy = GetWorld()->SpawnActor<AActor>(EnemyClass, SpawnLocation, SpawnRotation, SpawnParams);
    if (SpawnedEnemy)
    {
        CurrentEnemyCount++;
        
        // スポーン成功をログに出力
        UE_LOG(LogTemp, Display, TEXT("敵をスポーンしました: %s"), *SpawnedEnemy->GetName());
        
        // 敵が倒されたときにカウントを減らすための処理を設定
        AMCPShooterEnemy* Enemy = Cast<AMCPShooterEnemy>(SpawnedEnemy);
        if (Enemy)
        {
            Enemy->OnEnemyDestroyed.AddDynamic(this, &AMCPShooterGameMode::OnEnemyDestroyed);
        }
    }
}

AActor* AMCPShooterGameMode::SpawnPlayerCharacter()
{
    // プレイヤーキャラクターをスポーン（既にスポーンされている場合があるため、参照を取得するだけ）
    APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
    if (PC)
    {
        if (PC->GetPawn())
        {
            return PC->GetPawn();
        }
        else
        {
            // スポーン位置を設定
            FVector SpawnLocation = FVector(0.0f, 0.0f, 100.0f);
            FRotator SpawnRotation = FRotator(0.0f, 0.0f, 0.0f);
            
            // プレイヤーをスポーン
            FActorSpawnParameters SpawnParams;
            SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
            
            AActor* SpawnedPlayer = GetWorld()->SpawnActor<APawn>(DefaultPawnClass, SpawnLocation, SpawnRotation, SpawnParams);
            if (SpawnedPlayer)
            {
                PC->Possess(Cast<APawn>(SpawnedPlayer));
                return SpawnedPlayer;
            }
        }
    }
    
    return nullptr;
}

void AMCPShooterGameMode::LoadBlenderAssets()
{
    // MCPアセットマネージャーを取得
    UMCPAssetManager* AssetManager = UMCPAssetManager::Get();
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーを取得できませんでした"));
        return;
    }
    
    // サーバー接続を確認
    AssetManager->CheckServerConnection([this](bool bSuccess, const FString& Message) {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("MCPサーバーに接続しました: %s"), *Message);
            
            // プレイヤーシップアセットをインポート
            ImportPlayerShipAsset();
            
            // 敵シップアセットをインポート
            ImportEnemyShipAsset();
            
            // プロジェクタイルアセットをインポート
            ImportProjectileAsset();
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("MCPサーバーに接続できませんでした: %s"), *Message);
        }
    });
}

void AMCPShooterGameMode::ImportPlayerShipAsset()
{
    UMCPAssetManager* AssetManager = UMCPAssetManager::Get();
    if (AssetManager)
    {
        AssetManager->ImportBlenderModel("exports/PlayerShip.fbx", "/Game/BlenderAssets", 
            [](const FMCPAssetImportResult& Result) {
                if (Result.bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("プレイヤーシップアセットのインポートに成功しました: %s"), *Result.AssetPath);
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("プレイヤーシップアセットのインポートに失敗しました"));
                }
            });
    }
}

void AMCPShooterGameMode::ImportEnemyShipAsset()
{
    UMCPAssetManager* AssetManager = UMCPAssetManager::Get();
    if (AssetManager)
    {
        AssetManager->ImportBlenderModel("exports/EnemyShip.fbx", "/Game/BlenderAssets", 
            [](const FMCPAssetImportResult& Result) {
                if (Result.bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("敵シップアセットのインポートに成功しました: %s"), *Result.AssetPath);
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("敵シップアセットのインポートに失敗しました"));
                }
            });
    }
}

void AMCPShooterGameMode::ImportProjectileAsset()
{
    UMCPAssetManager* AssetManager = UMCPAssetManager::Get();
    if (AssetManager)
    {
        AssetManager->ImportBlenderModel("exports/Projectile.fbx", "/Game/BlenderAssets", 
            [](const FMCPAssetImportResult& Result) {
                if (Result.bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("プロジェクタイルアセットのインポートに成功しました: %s"), *Result.AssetPath);
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("プロジェクタイルアセットのインポートに失敗しました"));
                }
            });
    }
}

void AMCPShooterGameMode::OnEnemyDestroyed(AMCPShooterEnemy* DestroyedEnemy)
{
    // 敵が倒されたときのカウント処理
    if (CurrentEnemyCount > 0)
    {
        CurrentEnemyCount--;
    }
} 
