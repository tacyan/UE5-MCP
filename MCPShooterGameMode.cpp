// Copyright MCP Framework. All Rights Reserved.

#include "MCPShooterGameMode.h"
#include "MCPShooterCharacter.h"
#include "MCPShooterEnemy.h"
#include "MCPAssetManager.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "MCPShooterPlayerController.h"
#include "GameFramework/PlayerStart.h"
#include "GameFramework/PlayerController.h"

AMCPShooterGameMode::AMCPShooterGameMode()
    : Super()
    , EnemySpawnInterval(3.0f)
    , MaxEnemies(10)
    , CurrentEnemies(0)
    , bGameStarted(false)
    , bGameOver(false)
    , SpawnWidth(1000.0f)
    , SpawnHeight(500.0f)
    , SpawnDistance(1500.0f)
{
    // デフォルトのポーンクラスを設定
    DefaultPawnClass = AMCPShooterCharacter::StaticClass();
    
    // 初期スコアを設定
    Score = 0;
    
    // ゲームは毎フレーム更新
    PrimaryActorTick.bCanEverTick = true;
}

void AMCPShooterGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    // ゲーム開始の準備
    StartGame();
}

void AMCPShooterGameMode::StartGame()
{
    // ゲーム状態を初期化
    Score = 0;
    CurrentEnemies = 0;
    bGameStarted = true;
    bGameOver = false;
    
    // Blenderアセットをロード
    LoadBlenderAssets();
    // スコアをリセット
    CurrentScore = 0;
    CurrentEnemyCount = 0;
    
    // プレイヤーキャラクターをスポーン
    SpawnPlayerCharacter();
    
    // 敵のスポーンを開始
    GetWorldTimerManager().SetTimer(
        EnemySpawnTimerHandle,
        this,
        &AMCPShooterGameMode::SpawnEnemyTimerHandler,
        EnemySpawnInterval,
        true,
        0.5f  // 初回スポーン遅延
    );
}

void AMCPShooterGameMode::GameOver()
{
    if (bGameOver)
    {
        return; // 既にゲームオーバー処理済み
    }
    
    // ゲームオーバー状態に設定
    bGameOver = true;
    bGameStarted = false;
    
    // 敵のスポーンタイマーを停止
    GetWorldTimerManager().ClearTimer(EnemySpawnTimerHandle);
    
    // 既存の敵を全て破棄（オプション）
    TArray<AActor*> FoundEnemies;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), AMCPShooterEnemy::StaticClass(), FoundEnemies);
    
    for (AActor* Enemy : FoundEnemies)
    {
        Enemy->Destroy();
    }
    
    // ゲームオーバー画面の表示など
    // UE5のC++では直接UIを操作するのは難しいため、Blueprint側でUI表示を行うことが多い
    
    // 一定時間後にリスタート（オプション）
    FTimerHandle RestartTimerHandle;
    GetWorldTimerManager().SetTimer(
        RestartTimerHandle,
        this,
        &AMCPShooterGameMode::RestartGame,
        5.0f, // 5秒後にリスタート
        false);
}

void AMCPShooterGameMode::RestartGame()
{
    // 現在のレベルを再読み込み
    UGameplayStatics::OpenLevel(this, FName(*GetWorld()->GetName()), false);
}

void AMCPShooterGameMode::AddScore(int32 Points)
{
    Score += Points;
    // スコア更新イベントがある場合はここで発火
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
                &AMCPShooterGameMode::SpawnEnemyTimerHandler,
                EnemySpawnInterval,
                true
            );
        }
    }
}

void AMCPShooterGameMode::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // ゲームロジックの追加処理があればここに実装
}

void AMCPShooterGameMode::SpawnEnemyTimerHandler()
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
    
    // プレイヤーの位置を取得
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(GetWorld(), 0);
    if (PlayerPawn)
    {
        FVector PlayerLocation = PlayerPawn->GetActorLocation();
        
        // 生成位置をランダムに決定
        float RandomX = FMath::FRandRange(-SpawnWidth/2, SpawnWidth/2);
        float RandomY = FMath::FRandRange(-SpawnHeight/2, SpawnHeight/2);
        
        // プレイヤーの前方に敵を生成
        FVector SpawnLocation = PlayerLocation + FVector(SpawnDistance, RandomX, RandomY);
        
        // 敵を生成
        AMCPShooterEnemy* Enemy = SpawnEnemy(SpawnLocation);
        if (Enemy)
        {
            CurrentEnemyCount++;
            
            // 敵が破壊された時のデリゲートを設定
            Enemy->OnEnemyDestroyed.AddDynamic(this, &AMCPShooterGameMode::OnEnemyDestroyed);
        }
    }
}

AMCPShooterEnemy* AMCPShooterGameMode::SpawnEnemy(const FVector& SpawnLocation)
{
    // 敵を生成
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
    
    // 向きはプレイヤーの方向を向くように設定
    FRotator SpawnRotation = FRotator(0.0f, 180.0f, 0.0f);
    
    return GetWorld()->SpawnActor<AMCPShooterEnemy>(EnemyClass, SpawnLocation, SpawnRotation, SpawnParams);
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
        
        // 破壊された敵のスコア値を追加
        if (DestroyedEnemy)
        {
            AddScore(DestroyedEnemy->GetScoreValue());
        }
    }
} 
