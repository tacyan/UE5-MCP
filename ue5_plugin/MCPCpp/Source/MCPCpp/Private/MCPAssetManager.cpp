// Copyright MCP Framework. All Rights Reserved.

#include "MCPAssetManager.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/StaticMeshActor.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/GameModeBase.h"
#include "Engine/World.h"
#include "Editor.h"
#include "EditorLevelLibrary.h"

// シングルトンインスタンスの初期化
UMCPAssetManager* UMCPAssetManager::Instance = nullptr;

UMCPAssetManager::UMCPAssetManager()
    : bInitialized(false)
{
    // MCPClientの作成
    MCPClient = MakeShared<FMCPClient>();
}

UMCPAssetManager* UMCPAssetManager::Get()
{
    if (!Instance)
    {
        Instance = NewObject<UMCPAssetManager>(GetTransientPackage(), NAME_None, RF_Standalone);
        Instance->Initialize();
    }
    
    return Instance;
}

bool UMCPAssetManager::Initialize()
{
    if (bInitialized)
    {
        return true;
    }
    
    // 設定ファイルからMCPサーバーURLの読み込みを試みる
    FString ConfigFilePath = FPaths::ProjectConfigDir() / TEXT("mcp_settings.json");
    if (FPaths::FileExists(ConfigFilePath))
    {
        FString JsonContent;
        if (FFileHelper::LoadFileToString(JsonContent, *ConfigFilePath))
        {
            TSharedPtr<FJsonObject> JsonObject;
            TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonContent);
            if (FJsonSerializer::Deserialize(Reader, JsonObject))
            {
                const TSharedPtr<FJsonObject>* ServerObj;
                if (JsonObject->TryGetObjectField(TEXT("server"), ServerObj))
                {
                    FString Host = (*ServerObj)->GetStringField(TEXT("host"));
                    int32 Port = (*ServerObj)->GetIntegerField(TEXT("port"));
                    FString ServerUrl = FString::Printf(TEXT("http://%s:%d"), *Host, Port);
                    MCPClient->SetServerURL(ServerUrl);
                }
            }
        }
    }
    
    bInitialized = true;
    return true;
}

void UMCPAssetManager::CheckServerConnection(TFunction<void(bool bSuccess, const FString& Message)> OnCompleteCallback)
{
    MCPClient->CheckConnection(OnCompleteCallback);
}

void UMCPAssetManager::ImportBlenderModel(const FString& ModelPath, const FString& DestinationPath,
                                     TFunction<void(const FMCPAssetImportResult& Result)> OnCompleteCallback)
{
    MCPClient->ImportAsset(ModelPath, DestinationPath, 
        [OnCompleteCallback, ModelPath, DestinationPath](bool bSuccess, const FString& AssetName)
        {
            FMCPAssetImportResult Result;
            Result.bSuccess = bSuccess;
            
            if (bSuccess)
            {
                Result.AssetName = AssetName;
                Result.AssetPath = DestinationPath / AssetName;
                
                // インポートされたアセットを取得するための処理（必要に応じて）
                FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
                TArray<FAssetData> AssetData;
                FARFilter Filter;
                Filter.PackagePaths.Add(*DestinationPath);
                Filter.bRecursivePaths = true;
                AssetRegistryModule.Get().GetAssets(Filter, AssetData);
                
                // ログ出力
                UE_LOG(LogTemp, Log, TEXT("Blenderモデル '%s' をインポートしました: %s"), *ModelPath, *Result.AssetPath);
            }
            else
            {
                Result.ErrorMessage = FString::Printf(TEXT("アセットのインポートに失敗しました: %s"), *ModelPath);
                UE_LOG(LogTemp, Error, TEXT("%s"), *Result.ErrorMessage);
            }
            
            OnCompleteCallback(Result);
        });
}

bool UMCPAssetManager::PlaceAssetInLevel(const FString& AssetPath, const FVector& Location, 
                                      const FRotator& Rotation, const FVector& Scale,
                                      const FString& ActorName)
{
#if WITH_EDITOR
    if (!IsInGameThread())
    {
        // ゲームスレッドでの実行が必要な場合は、ゲームスレッドに処理を移譲
        AsyncTask(ENamedThreads::GameThread, [this, AssetPath, Location, Rotation, Scale, ActorName]() {
            PlaceAssetInLevel(AssetPath, Location, Rotation, Scale, ActorName);
        });
        return true;
    }
    
    // アセットのロード
    UObject* Asset = LoadObject<UObject>(nullptr, *AssetPath);
    if (!Asset)
    {
        UE_LOG(LogTemp, Error, TEXT("アセットを読み込めませんでした: %s"), *AssetPath);
        return false;
    }
    
    // スタティックメッシュの場合
    UStaticMesh* StaticMesh = Cast<UStaticMesh>(Asset);
    if (StaticMesh)
    {
        // エディタの場合
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (World)
        {
            AStaticMeshActor* MeshActor = World->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Location, Rotation);
            if (MeshActor)
            {
                MeshActor->GetStaticMeshComponent()->SetStaticMesh(StaticMesh);
                MeshActor->SetActorScale3D(Scale);
                
                if (!ActorName.IsEmpty())
                {
                    MeshActor->SetActorLabel(ActorName);
                }
                
                UE_LOG(LogTemp, Log, TEXT("アセット '%s' をレベルに配置しました"), *AssetPath);
                return true;
            }
        }
    }
    else
    {
        // ブループリントの場合
        UBlueprint* Blueprint = Cast<UBlueprint>(Asset);
        if (Blueprint)
        {
            UClass* BPClass = Blueprint->GeneratedClass;
            if (BPClass)
            {
                UWorld* World = GEditor->GetEditorWorldContext().World();
                if (World)
                {
                    AActor* Actor = World->SpawnActor(BPClass, &Location, &Rotation);
                    if (Actor)
                    {
                        Actor->SetActorScale3D(Scale);
                        
                        if (!ActorName.IsEmpty())
                        {
                            Actor->SetActorLabel(ActorName);
                        }
                        
                        UE_LOG(LogTemp, Log, TEXT("ブループリント '%s' をレベルに配置しました"), *AssetPath);
                        return true;
                    }
                }
            }
        }
    }
#endif
    
    UE_LOG(LogTemp, Error, TEXT("アセットの配置に失敗しました: %s"), *AssetPath);
    return false;
}

bool UMCPAssetManager::SetGameMode(TSubclassOf<AGameModeBase> GameModeClass)
{
    if (!GameModeClass)
    {
        UE_LOG(LogTemp, Error, TEXT("ゲームモードクラスが無効です"));
        return false;
    }
    
    FString GameModePath = GameModeClass->GetPathName();
    
    MCPClient->SetGameMode(GameModePath, [](bool bSuccess) {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("ゲームモードを設定しました"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("ゲームモードの設定に失敗しました"));
        }
    });
    
    return true;
} 
