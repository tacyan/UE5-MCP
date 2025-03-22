// Copyright MCP Framework. All Rights Reserved.

using UnrealBuildTool;

public class MCPShooterGame : ModuleRules
{
    public MCPShooterGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
    
        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core", 
            "CoreUObject", 
            "Engine", 
            "InputCore",
            "MCPCpp" // MCPCppプラグインへの依存関係を追加
        });

        PrivateDependencyModuleNames.AddRange(new string[] {  });

        // ターゲットに適した設定を使用
        if (Target.Type == TargetType.Editor)
        {
            PrivateDependencyModuleNames.AddRange(new string[] { 
                "UnrealEd",
                "LevelEditor",
                "AssetRegistry"
            });
        }

        // Uncomment if you are using Slate UI
        // PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });
    }
} 
