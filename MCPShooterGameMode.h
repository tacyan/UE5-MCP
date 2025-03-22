// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MCPShooterGameMode.generated.h"

class AMCPShooterEnemy;

/**
 * MCPシューティングゲームモード
 * 
 * このゲームモードは、簡単なシューティングゲームを実装するためのものです。
 * MCPフレームワークを使用してBlenderからインポートされたアセットを活用します。
 */
UCLASS()
class SPACESHOOTERGAME_API AMCPShooterGameMode : public AGameModeBase
{
	GENERATED_BODY()
	
public:
	/**
	 * コンストラクタ
	 * ゲームモードの初期設定を行います
	 */
	AMCPShooterGameMode();

	/**
	 * スコアを追加する関数
	 * @param Points 追加するスコアポイント
	 */
	UFUNCTION(BlueprintCallable, Category = "Game")
	void AddScore(int32 Points);

	/**
	 * 現在のスコアを取得する関数
	 * @return 現在のスコア
	 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Game")
	int32 GetScore() const { return Score; }

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
	 * 敵が破壊された時のハンドラ
	 * @param DestroyedEnemy 破壊された敵
	 */
	UFUNCTION()
	void OnEnemyDestroyed(AMCPShooterEnemy* DestroyedEnemy);

	/**
	 * 敵の生成タイマーハンドラ
	 */
	UFUNCTION()
	void SpawnEnemyTimerHandler();

	/**
	 * 敵を生成する関数
	 * @param SpawnLocation 生成位置
	 * @return 生成された敵
	 */
	AMCPShooterEnemy* SpawnEnemy(const FVector& SpawnLocation);

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

private:
	/** 現在のスコア */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Game", meta = (AllowPrivateAccess = "true"))
	int32 Score;

	/** 敵の生成間隔（秒） */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Enemy Spawning", meta = (AllowPrivateAccess = "true"))
	float EnemySpawnInterval;

	/** 同時に存在できる敵の最大数 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Enemy Spawning", meta = (AllowPrivateAccess = "true"))
	int32 MaxEnemies;

	/** 現在存在する敵の数 */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy Spawning", meta = (AllowPrivateAccess = "true"))
	int32 CurrentEnemies;

	/** 敵の生成クラス */
	UPROPERTY(EditDefaultsOnly, Category = "Enemy Spawning")
	TSubclassOf<AMCPShooterEnemy> EnemyClass;

	/** 敵の生成タイマーハンドル */
	FTimerHandle EnemySpawnTimerHandle;

	/** 敵の生成可能範囲の幅 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Enemy Spawning", meta = (AllowPrivateAccess = "true"))
	float SpawnWidth;

	/** 敵の生成可能範囲の高さ */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Enemy Spawning", meta = (AllowPrivateAccess = "true"))
	float SpawnHeight;

	/** 敵の生成距離（プレイヤーからの距離） */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Enemy Spawning", meta = (AllowPrivateAccess = "true"))
	float SpawnDistance;
}; 
