// Copyright MCP Framework. All Rights Reserved.

#include "MCPCpp.h"
#include "LevelEditor.h"
#include "Framework/Commands/Commands.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "EditorStyleSet.h"

#define LOCTEXT_NAMESPACE "FMCPCppModule"

// モジュールシングルトンの取得
FMCPCppModule& FMCPCppModule::Get()
{
    return GetPrivate();
}

void FMCPCppModule::StartupModule()
{
    // MCPモジュールが起動したことをログに出力
    UE_LOG(LogTemp, Log, TEXT("MCP C++ モジュールが起動しました"));
    
    // メニューを登録
    RegisterMenuExtensions();
}

void FMCPCppModule::ShutdownModule()
{
    // メニューの登録を解除
    UnregisterMenuExtensions();
    
    // MCPモジュールがシャットダウンしたことをログに出力
    UE_LOG(LogTemp, Log, TEXT("MCP C++ モジュールがシャットダウンしました"));
}

void FMCPCppModule::RegisterMenuExtensions()
{
    // メニュー拡張の実装
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    
    // ここにメニュー拡張コードを追加
}

void FMCPCppModule::UnregisterMenuExtensions()
{
    // メニュー拡張の解除
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FMCPCppModule, MCPCpp) 
