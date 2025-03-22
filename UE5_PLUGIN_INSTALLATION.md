# MCP C++プラグインのUE5へのインストール手順

このガイドでは、MCP C++プラグインをUnreal Engine 5プロジェクトにインストールする方法を説明します。

## 前提条件

- Unreal Engine 5.3以上がインストールされていること
- C++プロジェクトが作成されていること
- 適切な開発環境（Visual StudioまたはXcode）がインストールされていること

## インストール手順

1. **プラグインディレクトリのコピー**

   `ue5_plugin/MCPCpp`フォルダを、UE5プロジェクトの`Plugins`ディレクトリにコピーします。
   
   ```bash
   # Pluginsディレクトリが存在しない場合は作成
   mkdir -p /path/to/your/UE5Project/Plugins
   
   # プラグインをコピー
   cp -r ue5_plugin/MCPCpp /path/to/your/UE5Project/Plugins/
   ```

2. **プロジェクトのBuild.csファイルの更新**

   UE5プロジェクトのBuild.csファイル（通常は`Source/YourProject/YourProject.Build.cs`）を開き、`MCPCpp`モジュールへの依存関係を追加します。
   
   ```csharp
   PublicDependencyModuleNames.AddRange(
       new string[]
       {
           "Core",
           "CoreUObject",
           "Engine",
           "InputCore",
           // 他の依存モジュール...
           "MCPCpp"  // この行を追加
       }
   );
   ```

3. **UE5エディタの起動**

   UE5エディタでプロジェクトを開きます。Visual StudioまたはXcodeでソリューションを再生成するように求められた場合、「はい」を選択します。

4. **プラグインの有効化**

   UE5エディタで、メニューから「編集」→「プラグイン」を選択します。
   「プロジェクト」タブで「MCP C++ Plugin」を探し、有効化にチェックを入れます。
   
   エディタの再起動を求められたら、再起動します。

5. **設定ファイルの作成**

   プロジェクトの`Config`ディレクトリに`mcp_settings.json`ファイルを作成し、MCPサーバーの接続設定を記述します。
   
   ```json
   {
     "server": {
       "host": "127.0.0.1",
       "port": 8080
     }
   }
   ```

## プラグインの使用方法

1. **MCPゲームプレイコンポーネントの追加**

   アクターまたはポーンに`MCPGameplayComponent`を追加します：
   
   - ブループリントエディタで「コンポーネントを追加」→「MCP」→「MCPGameplayComponent」を選択
   - または、C++で：
     ```cpp
     #include "MCPGameplayComponent.h"
     
     // アクターコンストラクタ内で
     MCPComponent = CreateDefaultSubobject<UMCPGameplayComponent>(TEXT("MCPComponent"));
     ```

2. **アセットの操作**

   Blenderからインポートしたアセットを操作するには、以下のAPIを使用します：
   
   ```cpp
   // アセットのロード
   MCPComponent->LoadBlenderAsset("/Game/BlenderAssets/GameSword", 
       FMCPGameplayComponent::FOnAssetLoaded::CreateUObject(this, &AMyActor::OnAssetLoaded));
   
   // アセットのスポーン
   AActor* SpawnedActor = MCPComponent->SpawnAssetActor("/Game/BlenderAssets/GameSword", 
       FVector(0, 0, 100), FRotator::ZeroRotator, FVector(1, 1, 1));
   ```

3. **カスタムゲームモードの使用**

   MCPゲームモードを使用するには、プロジェクト設定でゲームモードを変更します：
   
   - 「編集」→「プロジェクト設定」→「マップ＆モード」→「デフォルトゲームモード」で「MCPGameMode」を選択
   - または、C++で独自のゲームモードを作成：
     ```cpp
     #include "MCPGameMode.h"
     
     class MYGAME_API AMyGameMode : public AMCPGameMode
     {
         GENERATED_BODY()
         
     public:
         AMyGameMode();
         
         // MCPGameModeの機能をオーバーライド
     };
     ```

## トラブルシューティング

1. **コンパイルエラー**

   コンパイルエラーが発生した場合は、以下を確認してください：
   
   - プラグインディレクトリが正しい場所にあるか
   - Build.csファイルに依存関係が正しく追加されているか
   - UE5のバージョンが5.3以上か

2. **接続エラー**

   MCPサーバーに接続できない場合は、以下を確認してください：
   
   - MCPサーバーが実行されているか（`python run_mcp.py server`）
   - Blenderインテグレーションが実行されているか（`python run_mcp.py blender`）
   - `mcp_settings.json`の設定が正しいか

3. **アセットのインポートエラー**

   アセットのインポートに失敗する場合は、以下を確認してください：
   
   - FBXファイルが`exports`ディレクトリに存在するか
   - ファイルパスが正しいか
   - Blenderインテグレーションが正常に動作しているか

## テスト

プラグインが正常にインストールされたかテストするには：

1. MCPサーバーを起動：
   ```bash
   python run_mcp.py server
   ```

2. Blenderインテグレーションを起動：
   ```bash
   python run_mcp.py blender
   ```

3. UE5エディタでテストアクターを作成し、MCPGameplayComponentを追加

4. ブループリントまたはC++で以下のコードを実行：
   ```cpp
   // アセットのスポーン
   MCPComponent->SpawnAssetActor("/Game/BlenderAssets/GameSword", 
       FVector(0, 0, 100), FRotator::ZeroRotator, FVector(1, 1, 1));
   ```

5. シーンにGameSwordモデルが表示されれば、プラグインは正常に動作しています 
