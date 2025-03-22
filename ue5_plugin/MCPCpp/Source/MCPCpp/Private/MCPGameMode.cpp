// Copyright MCP Framework. All Rights Reserved.

#include "MCPGameMode.h"
#include "Misc/Paths.h"
#include "HAL/FileManagerGeneric.h"

AMCPGameMode::AMCPGameMode()
    : bConnectedToServer(false)
{
    // ゲームモードの初期設定
    PrimaryActorTick.bCanEverTick = true;
    
    // アセットマネージャーの取得
    AssetManager = UMCPAssetManager::Get();
}

void AMCPGameMode::StartPlay()
{
    Super::StartPlay();
    
    // MCPサーバーへの接続を確認
    if (AssetManager)
    {
        AssetManager->CheckServerConnection([this](bool bSuccess, const FString& Message) {
            bConnectedToServer = bSuccess;
            
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("MCPサーバーに接続しました: %s"), *Message);
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("MCPサーバーに接続できませんでした: %s"), *Message);
            }
        });
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
    }
}

void AMCPGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    
    // 必要に応じてリソースのクリーンアップ
}

void AMCPGameMode::ImportBlenderAsset(const FString& AssetPath, const FString& DestinationPath, 
                                  FImportAssetCompleteDelegate OnComplete)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false);
        }
        return;
    }
    
    if (!bConnectedToServer)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPサーバーに接続されていません"));
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false);
        }
        return;
    }
    
    // アセットのインポート処理
    AssetManager->ImportBlenderModel(AssetPath, DestinationPath, 
        [OnComplete](const FMCPAssetImportResult& Result) {
            if (OnComplete.IsBound())
            {
                OnComplete.Execute(Result.bSuccess);
            }
        });
}

void AMCPGameMode::ImportAllAssetsInDirectory(const FString& DirectoryPath, const FString& DestinationPath,
                                          FImportAssetCompleteDelegate OnComplete)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false);
        }
        return;
    }
    
    if (!bConnectedToServer)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPサーバーに接続されていません"));
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false);
        }
        return;
    }
    
    // ディレクトリ内のファイル一覧を取得
    TArray<FString> Files;
    IFileManager::Get().FindFiles(Files, *DirectoryPath, TEXT("*.fbx"));
    
    if (Files.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("ディレクトリ内にFBXアセットが見つかりませんでした: %s"), *DirectoryPath);
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false);
        }
        return;
    }
    
    // 各ファイルをインポート
    // 注：実際にはもっと洗練された非同期処理が必要
    bool bAllSucceeded = true;
    for (const FString& File : Files)
    {
        FString FullPath = FPaths::Combine(DirectoryPath, File);
        
        // ここでは同期的に処理していますが、実際には非同期処理が望ましい
        AssetManager->ImportBlenderModel(FullPath, DestinationPath, 
            [&bAllSucceeded](const FMCPAssetImportResult& Result) {
                if (!Result.bSuccess)
                {
                    bAllSucceeded = false;
                }
            });
    }
    
    if (OnComplete.IsBound())
    {
        OnComplete.Execute(bAllSucceeded);
    }
}

bool AMCPGameMode::CreateCustomLevel(const FString& LevelName, const FString& Template)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        return false;
    }
    
    if (!bConnectedToServer)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPサーバーに接続されていません"));
        return false;
    }
    
    // レベル作成コマンドの実行（実装例）
    TSharedPtr<FJsonObject> Params = MakeShared<FJsonObject>();
    Params->SetStringField(TEXT("name"), LevelName);
    Params->SetStringField(TEXT("template"), Template);
    
    // ToDo: 実際のMCPサーバーへのコマンド送信を実装
    UE_LOG(LogTemp, Warning, TEXT("レベル作成機能は現在実装中です"));
    
    return true;
}

void AMCPGameMode::SetupLevelWithBlenderAssets(const FString& LevelName, const FString& LevelType,
                                           FSetupLevelCompleteDelegate OnComplete)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false, TEXT(""));
        }
        return;
    }
    
    if (!bConnectedToServer)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPサーバーに接続されていません"));
        if (OnComplete.IsBound())
        {
            OnComplete.Execute(false, TEXT(""));
        }
        return;
    }
    
    // レベルセットアップコマンドの実行（実装例）
    TSharedPtr<FJsonObject> Params = MakeShared<FJsonObject>();
    Params->SetStringField(TEXT("level_name"), LevelName);
    Params->SetStringField(TEXT("level_type"), LevelType);
    
    // ToDo: 実際のMCPサーバーへのコマンド送信を実装
    UE_LOG(LogTemp, Warning, TEXT("レベルセットアップ機能は現在実装中です"));
    
    if (OnComplete.IsBound())
    {
        FString LevelPath = FString::Printf(TEXT("/Game/Levels/%s"), *LevelName);
        OnComplete.Execute(true, LevelPath);
    }
} 
