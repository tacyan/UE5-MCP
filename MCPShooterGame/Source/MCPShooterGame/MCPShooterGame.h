// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * MCPShooterGameモジュール
 * 
 * MCPフレームワークを使用した簡単なシューティングゲームを実装するモジュール
 */
class FMCPShooterGameModule : public IModuleInterface
{
public:
    /** IModuleInterfaceの実装 */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
}; 
