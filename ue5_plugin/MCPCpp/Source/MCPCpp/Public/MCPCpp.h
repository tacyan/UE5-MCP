// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * MCPモジュール
 * 
 * このモジュールはMCPサーバーとUE5を連携させるための機能を提供します。
 * Blenderで作成したアセットをUE5に取り込み、ゲーム開発を支援します。
 */
class FMCPCppModule : public IModuleInterface
{
public:
	/** IModuleInterface の実装 */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
    
    /** シングルトンの取得 */
    static FMCPCppModule& Get();

private:
    /** モジュールシングルトンへの参照を取得 */
    static inline FMCPCppModule& GetPrivate() 
    { 
        return FModuleManager::GetModuleChecked<FMCPCppModule>("MCPCpp"); 
    }

    /** メニュー拡張を登録 */
    void RegisterMenuExtensions();
    
    /** メニュー拡張を解除 */
    void UnregisterMenuExtensions();
}; 
