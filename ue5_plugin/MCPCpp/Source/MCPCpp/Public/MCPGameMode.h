// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MCPAssetManager.h"
#include "MCPGameMode.generated.h"

/**
 * MCPゲームモード
 * 
 * このゲームモードは、BlenderからUE5に取り込んだアセットを使って
 * ゲームを構築するための基本機能を提供します。
 */
UCLASS()
class MCPCPP_API AMCPGameMode : public AGameModeBase
{
    GENERATED_BODY()
    
public:
    /** コンストラクタ */
    AMCPGameMode();
    
    /** ゲーム開始時の処理 */
    virtual void StartPlay() override;
    
    /** ゲーム終了時の処理 */
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    
    /**
     * アセットのインポート
     * 
     * @param AssetPath アセットのパス
     * @param DestinationPath UE5内の保存先パス
     * @param OnComplete 完了時に呼ばれるコールバック
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Game")
    void ImportBlenderAsset(const FString& AssetPath, const FString& DestinationPath, 
                          FImportAssetCompleteDelegate OnComplete);
    
    /**
     * アセットディレクトリ内のすべてのアセットをインポート
     * 
     * @param DirectoryPath インポートするディレクトリパス
     * @param DestinationPath UE5内の保存先パス
     * @param OnComplete 完了時に呼ばれるコールバック
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Game")
    void ImportAllAssetsInDirectory(const FString& DirectoryPath, const FString& DestinationPath,
                                  FImportAssetCompleteDelegate OnComplete);
    
    /**
     * カスタムゲームレベルの作成
     * 
     * @param LevelName レベル名
     * @param Template テンプレート名
     * @return 成功したかどうか
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Game")
    bool CreateCustomLevel(const FString& LevelName, const FString& Template = TEXT("Empty"));
    
    /**
     * Blenderからのアセットでレベルをセットアップするリクエストを送信
     * 
     * @param LevelName レベル名
     * @param LevelType レベルタイプ（"シューティング", "RPG", "パズル"など）
     * @param OnComplete 完了時に呼ばれるコールバック
     */
    UFUNCTION(BlueprintCallable, Category = "MCP|Game")
    void SetupLevelWithBlenderAssets(const FString& LevelName, const FString& LevelType,
                                   FSetupLevelCompleteDelegate OnComplete);
    
public:
    /** アセットインポート完了デリゲート */
    DECLARE_DYNAMIC_DELEGATE_OneParam(FImportAssetCompleteDelegate, bool, bSuccess);
    
    /** レベルセットアップ完了デリゲート */
    DECLARE_DYNAMIC_DELEGATE_TwoParams(FSetupLevelCompleteDelegate, bool, bSuccess, const FString&, LevelPath);
    
protected:
    /** MCPアセットマネージャーへの参照 */
    UMCPAssetManager* AssetManager;
    
    /** Blenderサーバーとの接続状態 */
    bool bConnectedToServer;
}; 
