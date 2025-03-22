// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MCPAssetManager.h"
#include "MCPGameplayComponent.generated.h"

/**
 * MCPゲームプレイコンポーネント
 * 
 * このコンポーネントは、BlenderからUE5に取り込んだアセットを使って
 * ゲームプレイの実装を行うための機能を提供します。
 * ゲームアクターにアタッチして使用します。
 */
UCLASS(ClassGroup=(MCP), meta=(BlueprintSpawnableComponent))
class MCPCPP_API UMCPGameplayComponent : public UActorComponent
{
    GENERATED_BODY()

public:    
    /** コンストラクタ */
    UMCPGameplayComponent();

    /** コンポーネントの初期化処理 */
    virtual void InitializeComponent() override;
    
    /** ティック関数 */
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    /**
     * Blenderアセットをロードして使用可能にする
     * 
     * @param AssetPath アセットのパス
     * @param OnLoaded アセットがロードされた時に呼ばれるデリゲート
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Gameplay")
    void LoadBlenderAsset(const FString& AssetPath, FOnAssetLoaded OnLoaded);
    
    /**
     * アセットをスポーンする
     * 
     * @param AssetPath アセットのパス
     * @param Location スポーン位置
     * @param Rotation スポーン時の回転
     * @param Scale スケール
     * @return スポーンされたアクター
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Gameplay")
    AActor* SpawnAssetActor(const FString& AssetPath, FVector Location, FRotator Rotation, FVector Scale = FVector(1.0f));
    
    /**
     * カスタムBlenderアセットをスポーンする
     * 
     * @param ModelType モデルタイプ
     * @param Location スポーン位置
     * @param Rotation スポーン時の回転
     * @param Scale スケール
     * @param OnSpawned スポーン完了時に呼ばれるデリゲート
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Gameplay")
    void SpawnCustomBlenderAsset(const FString& ModelType, FVector Location, FRotator Rotation, FVector Scale, FOnActorSpawned OnSpawned);

public:
    /** アセットロード時デリゲート */
    DECLARE_DYNAMIC_DELEGATE_OneParam(FOnAssetLoaded, bool, bSuccess);
    
    /** アクタースポーン時デリゲート */
    DECLARE_DYNAMIC_DELEGATE_OneParam(FOnActorSpawned, AActor*, SpawnedActor);
    
protected:
    /** コンポーネントの初期化処理 */
    virtual void BeginPlay() override;
    
private:
    /** MCPアセットマネージャーへの参照 */
    UMCPAssetManager* AssetManager;
}; 
