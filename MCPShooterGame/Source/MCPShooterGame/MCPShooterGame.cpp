// Copyright MCP Framework. All Rights Reserved.

#include "MCPShooterGame.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_PRIMARY_GAME_MODULE(FMCPShooterGameModule, MCPShooterGame, "MCPShooterGame");

void FMCPShooterGameModule::StartupModule()
{
    UE_LOG(LogTemp, Log, TEXT("MCPShooterGameモジュールが起動しました"));
}

void FMCPShooterGameModule::ShutdownModule()
{
    UE_LOG(LogTemp, Log, TEXT("MCPShooterGameモジュールがシャットダウンしました"));
} 
