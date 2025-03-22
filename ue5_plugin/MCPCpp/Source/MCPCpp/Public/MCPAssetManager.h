// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Dom/JsonObject.h"
#include "MCPClient.h"
#include "MCPAssetManager.generated.h"

/**
 * MCPAssetManagerでのアセットインポート結果を表す構造体
 */
USTRUCT(BlueprintType)
struct FMCPAssetImportResult
{
    GENERATED_BODY()
    
    /** インポートが成功したかどうか */
    UPROPERTY(BlueprintReadOnly, Category = "MCP|Asset")
    bool bSuccess;
    
    /** インポートされたアセットのパス */
    UPROPERTY(BlueprintReadOnly, Category = "MCP|Asset")
    FString AssetPath;
    
    /** アセット名 */
    UPROPERTY(BlueprintReadOnly, Category = "MCP|Asset")
    FString AssetName;
    
    /** エラーメッセージ（失敗時） */
    UPROPERTY(BlueprintReadOnly, Category = "MCP|Asset")
    FString ErrorMessage;
    
    /** コンストラクタ */
    FMCPAssetImportResult()
        : bSuccess(false)
    {
    }
};

/**
 * MCPアセットマネージャー
 * 
 * このクラスはBlenderから生成されたアセットのインポートと管理を担当します。
 * UE5内でBlenderアセットを簡単に使用できるようにするためのインターフェースを提供します。
 */
UCLASS(config=Engine, defaultconfig)
class MCPCPP_API UMCPAssetManager : public UObject
{
    GENERATED_BODY()
    
public:
    /** コンストラクタ */
    UMCPAssetManager();
    
    /** シングルトンインスタンスを取得 */
    static UMCPAssetManager* Get();
    
    /**
     * MCPクライアントを初期化
     * 
     * @return 初期化に成功したかどうか
     */
    bool Initialize();
    
    /**
     * サーバー接続を確認
     * 
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void CheckServerConnection(TFunction<void(bool bSuccess, const FString& Message)> OnCompleteCallback);
    
    /**
     * Blenderモデルをインポート
     * 
     * @param ModelPath Blenderモデルのパス
     * @param DestinationPath UE5内の保存先パス
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void ImportBlenderModel(const FString& ModelPath, const FString& DestinationPath,
                          TFunction<void(const FMCPAssetImportResult& Result)> OnCompleteCallback);
    
    /**
     * アセットをレベルに配置
     * 
     * @param AssetPath アセットパス
     * @param Location 配置場所
     * @param Rotation 回転
     * @param Scale スケール
     * @param ActorName アクター名（省略可）
     * @return 配置に成功したかどうか
     */
    bool PlaceAssetInLevel(const FString& AssetPath, const FVector& Location, 
                         const FRotator& Rotation, const FVector& Scale,
                         const FString& ActorName = TEXT(""));
    
    /**
     * ゲームモードを設定
     * 
     * @param GameModeClass ゲームモードクラス
     * @return 設定に成功したかどうか
     */
    bool SetGameMode(TSubclassOf<AGameModeBase> GameModeClass);
    
private:
    /** MCPクライアント */
    TSharedPtr<FMCPClient> MCPClient;
    
    /** 初期化済みフラグ */
    bool bInitialized;
    
    /** シングルトンインスタンス */
    static UMCPAssetManager* Instance;
}; 
