// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "MCPGameMode.h"
#include "MCPShooterGameMode.generated.h"

/**
 * MCPシューティングゲームモード
 * 
 * このゲームモードは、簡単なシューティングゲームを実装するためのものです。
 * MCPフレームワークを使用してBlenderからインポートされたアセットを活用します。
 */
UCLASS()
class MCPSHOOTERGAME_API AMCPShooterGameMode : public AMCPGameMode
{
    GENERATED_BODY()
    
public:
    /** コンストラクタ */
    AMCPShooterGameMode();
    
    /** ゲーム開始時の初期化 */
    virtual void BeginPlay() override;
    
    /** スコアを追加する */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void AddScore(int32 ScoreToAdd);
    
    /** 現在のスコアを取得する */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
    int32 GetScore() const { return CurrentScore; }
    
    /** 敵をスポーンする間隔を設定する */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void SetEnemySpawnInterval(float NewInterval);
    
    /** 敵をスポーンする */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void SpawnEnemy();
    
    /** ゲームオーバー処理 */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void GameOver();
    
    /** ゲームがスタートしたかどうか */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
    bool HasGameStarted() const { return bGameStarted; }
    
    /** ゲームがオーバーしたかどうか */
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MCP|Shooter")
    bool IsGameOver() const { return bGameOver; }
    
protected:
    /** 敵のスポーンタイマーハンドラ */
    FTimerHandle EnemySpawnTimerHandle;
    
    /** 敵をスポーンする間隔（秒） */
    UPROPERTY(EditDefaultsOnly, Category = "MCP|Shooter")
    float EnemySpawnInterval;
    
    /** 敵の最大数 */
    UPROPERTY(EditDefaultsOnly, Category = "MCP|Shooter")
    int32 MaxEnemyCount;
    
    /** 敵のクラス */
    UPROPERTY(EditDefaultsOnly, Category = "MCP|Shooter")
    TSubclassOf<class AActor> EnemyClass;
    
    /** 敵のスポーン位置 */
    UPROPERTY(EditDefaultsOnly, Category = "MCP|Shooter")
    FVector EnemySpawnLocation;
    
    /** 現在のスコア */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP|Shooter")
    int32 CurrentScore;
    
    /** 現在スポーンされている敵の数 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP|Shooter")
    int32 CurrentEnemyCount;
    
    /** ゲームがスタートしたかどうか */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP|Shooter")
    bool bGameStarted;
    
    /** ゲームがオーバーしたかどうか */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MCP|Shooter")
    bool bGameOver;
    
    /** ゲームを開始する */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    void StartGame();
    
    /** プレイヤーキャラクターを生成する */
    UFUNCTION(BlueprintCallable, Category = "MCP|Shooter")
    AActor* SpawnPlayerCharacter();
    
    /** Blenderアセットをロードする */
    void LoadBlenderAssets();
    
    /** 敵が倒された時のイベントハンドラ */
    UFUNCTION()
    void OnEnemyDestroyed(class AMCPShooterEnemy* DestroyedEnemy);
    
protected:
    /** プレイヤーシップアセットをインポートする */
    void ImportPlayerShipAsset();
    
    /** 敵シップアセットをインポートする */
    void ImportEnemyShipAsset();
    
    /** プロジェクタイルアセットをインポートする */
    void ImportProjectileAsset();
}; 
