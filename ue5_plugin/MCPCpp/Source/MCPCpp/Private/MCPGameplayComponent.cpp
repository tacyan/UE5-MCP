// Copyright MCP Framework. All Rights Reserved.

#include "MCPGameplayComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"

UMCPGameplayComponent::UMCPGameplayComponent()
{
    // コンポーネントをティック有効に設定
    PrimaryComponentTick.bCanEverTick = true;
    
    // 初期設定
    AssetManager = nullptr;
}

void UMCPGameplayComponent::InitializeComponent()
{
    Super::InitializeComponent();
    
    // アセットマネージャーの参照を取得
    AssetManager = UMCPAssetManager::Get();
    
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーの取得に失敗しました"));
    }
}

void UMCPGameplayComponent::BeginPlay()
{
    Super::BeginPlay();
    
    // 初期化確認
    if (AssetManager)
    {
        // サーバー接続を確認
        AssetManager->CheckServerConnection([](bool bSuccess, const FString& Message) {
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
}

void UMCPGameplayComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 必要に応じてティック処理を実装
}

void UMCPGameplayComponent::LoadBlenderAsset(const FString& AssetPath, FOnAssetLoaded OnLoaded)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        if (OnLoaded.IsBound())
        {
            OnLoaded.Execute(false);
        }
        return;
    }
    
    // アセットのロード（すでにインポート済みの場合）
    UObject* Asset = LoadObject<UObject>(nullptr, *AssetPath);
    if (Asset)
    {
        UE_LOG(LogTemp, Log, TEXT("アセット '%s' はすでにロードされています"), *AssetPath);
        if (OnLoaded.IsBound())
        {
            OnLoaded.Execute(true);
        }
        return;
    }
    
    // アセットのインポート処理が必要な場合
    // この実装はアセットの場所によって変わるため、ここでは簡略化
    UE_LOG(LogTemp, Warning, TEXT("アセット '%s' のロードに失敗しました。インポートが必要かもしれません。"), *AssetPath);
    if (OnLoaded.IsBound())
    {
        OnLoaded.Execute(false);
    }
}

AActor* UMCPGameplayComponent::SpawnAssetActor(const FString& AssetPath, FVector Location, FRotator Rotation, FVector Scale)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        return nullptr;
    }
    
    // アセットのロード
    UObject* Asset = LoadObject<UObject>(nullptr, *AssetPath);
    if (!Asset)
    {
        UE_LOG(LogTemp, Error, TEXT("アセット '%s' をロードできませんでした"), *AssetPath);
        return nullptr;
    }
    
    // スタティックメッシュの場合
    UStaticMesh* StaticMesh = Cast<UStaticMesh>(Asset);
    if (StaticMesh)
    {
        // ワールドが有効か確認
        UWorld* World = GetWorld();
        if (!World)
        {
            UE_LOG(LogTemp, Error, TEXT("ワールドが無効です"));
            return nullptr;
        }
        
        // メッシュアクターの生成
        AStaticMeshActor* MeshActor = World->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Location, Rotation);
        if (MeshActor)
        {
            // メッシュの設定
            MeshActor->GetStaticMeshComponent()->SetStaticMesh(StaticMesh);
            MeshActor->SetActorScale3D(Scale);
            
            UE_LOG(LogTemp, Log, TEXT("アセット '%s' のアクターをスポーンしました"), *AssetPath);
            return MeshActor;
        }
    }
    else
    {
        // ブループリントの場合
        UBlueprint* Blueprint = Cast<UBlueprint>(Asset);
        if (Blueprint && Blueprint->GeneratedClass)
        {
            UWorld* World = GetWorld();
            if (!World)
            {
                UE_LOG(LogTemp, Error, TEXT("ワールドが無効です"));
                return nullptr;
            }
            
            // ブループリントアクターの生成
            AActor* Actor = World->SpawnActor(Blueprint->GeneratedClass, &Location, &Rotation);
            if (Actor)
            {
                Actor->SetActorScale3D(Scale);
                
                UE_LOG(LogTemp, Log, TEXT("ブループリント '%s' のアクターをスポーンしました"), *AssetPath);
                return Actor;
            }
        }
    }
    
    UE_LOG(LogTemp, Error, TEXT("アセット '%s' のアクター生成に失敗しました"), *AssetPath);
    return nullptr;
}

void UMCPGameplayComponent::SpawnCustomBlenderAsset(const FString& ModelType, FVector Location, FRotator Rotation, FVector Scale, FOnActorSpawned OnSpawned)
{
    if (!AssetManager)
    {
        UE_LOG(LogTemp, Error, TEXT("MCPアセットマネージャーが初期化されていません"));
        if (OnSpawned.IsBound())
        {
            OnSpawned.Execute(nullptr);
        }
        return;
    }
    
    // Blenderでのモデル生成とUE5へのインポートプロセス
    // MCPサーバー経由でBlenderにモデル生成をリクエストする
    TSharedPtr<FJsonObject> Params = MakeShared<FJsonObject>();
    Params->SetStringField(TEXT("model_type"), ModelType);
    Params->SetArrayField(TEXT("location"), {
        MakeShared<FJsonValueNumber>(Location.X),
        MakeShared<FJsonValueNumber>(Location.Y),
        MakeShared<FJsonValueNumber>(Location.Z)
    });
    Params->SetArrayField(TEXT("scale"), {
        MakeShared<FJsonValueNumber>(Scale.X),
        MakeShared<FJsonValueNumber>(Scale.Y),
        MakeShared<FJsonValueNumber>(Scale.Z)
    });
    
    // ToDo: 実際のBlenderコマンド実行と結果の取得処理を実装
    UE_LOG(LogTemp, Warning, TEXT("カスタムBlenderアセットの生成は現在実装中です"));
    
    // ダミー実装（実際にはBlenderとの通信処理を実装）
    if (OnSpawned.IsBound())
    {
        OnSpawned.Execute(nullptr);
    }
} 
