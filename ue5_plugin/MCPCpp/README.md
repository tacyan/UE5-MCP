# MCP C++ プラグイン for Unreal Engine 5

## 概要

MCP C++プラグインは、Model Context Protocol (MCP) フレームワークをUnreal Engine 5と連携させるためのC++実装です。このプラグインを使用することで、Blenderで作成したアセットをUE5に取り込み、ゲームを動かすことができます。

## 主な機能

- MCPサーバーとの通信（REST API経由）
- Blenderで作成したアセットのUE5への自動インポート
- インポートしたアセットを使用したゲーム機能の提供
- ゲームレベルの自動セットアップ
- ブループリントからの簡単なアクセス

## インストール方法

1. `MCPCpp`フォルダを、UE5プロジェクトの`Plugins`ディレクトリにコピーします。
   - プロジェクトに`Plugins`フォルダがない場合は作成してください。

2. UE5エディタを起動し、プロジェクトを開きます。

3. メニューの「編集」→「プラグイン」を選択します。

4. 「プロジェクト」タブで「MCP C++ Plugin」を探し、有効化します。

5. エディタの再起動を求められたら、再起動します。

## 使用方法

### セットアップ

1. MCPサーバーが実行されていることを確認します。
   ```bash
   python run_mcp.py server
   ```

2. Blenderインテグレーションが実行されていることを確認します。
   ```bash
   python run_mcp.py blender
   ```

### C++で使用する場合

1. プロジェクトのBuild.csファイルで依存関係を追加します。

```csharp
PublicDependencyModuleNames.AddRange(
    new string[]
    {
        // 他の依存モジュール...
        "MCPCpp"
    }
);
```

2. ヘッダーファイルをインクルードします。

```cpp
#include "MCPAssetManager.h"
#include "MCPGameplayComponent.h"
#include "MCPGameMode.h"
```

3. コードでアセットマネージャーを使用してBlenderアセットをインポートします。

```cpp
UMCPAssetManager* AssetManager = UMCPAssetManager::Get();
AssetManager->ImportBlenderModel(AssetPath, DestinationPath, 
    [](const FMCPAssetImportResult& Result) {
        if (Result.bSuccess) {
            UE_LOG(LogTemp, Log, TEXT("アセットのインポートに成功しました: %s"), *Result.AssetPath);
        } else {
            UE_LOG(LogTemp, Error, TEXT("アセットのインポートに失敗しました: %s"), *Result.ErrorMessage);
        }
    });
```

### ブループリントで使用する場合

1. `MCPGameplayComponent`をアクターにアタッチします。

2. ブループリントエディタで、MCPコンポーネントの関数を呼び出します。
   - `LoadBlenderAsset`
   - `SpawnAssetActor`
   - `SpawnCustomBlenderAsset`

3. ゲームモードとして`MCPGameMode`を使用することもできます。

## 設定

プロジェクトの`Config`ディレクトリに`mcp_settings.json`ファイルを作成することで、MCPサーバーの接続設定をカスタマイズできます。

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080
  }
}
```

## サンプル

### シンプルなオブジェクト配置の例

```cpp
// MCPGameplayComponentを持つアクター内で
void AMyActor::PlaceBlenderModel()
{
    UMCPGameplayComponent* MCPComponent = FindComponentByClass<UMCPGameplayComponent>();
    if (MCPComponent)
    {
        // アセットをロード
        MCPComponent->LoadBlenderAsset("/Game/BlenderAssets/Cube", FMCPGameplayComponent::FOnAssetLoaded::CreateUObject(this, &AMyActor::OnAssetLoaded));
    }
}

void AMyActor::OnAssetLoaded(bool bSuccess)
{
    if (bSuccess)
    {
        UMCPGameplayComponent* MCPComponent = FindComponentByClass<UMCPGameplayComponent>();
        if (MCPComponent)
        {
            // アセットをスポーン
            AActor* SpawnedActor = MCPComponent->SpawnAssetActor("/Game/BlenderAssets/Cube", 
                FVector(0, 0, 100), FRotator::ZeroRotator, FVector(1, 1, 1));
        }
    }
}
```

## トラブルシューティング

- **MCPサーバーに接続できない場合**: MCPサーバーが起動していることを確認し、`mcp_settings.json`のホストとポートが正しく設定されていることを確認してください。

- **アセットのインポートが失敗する場合**: Blenderインテグレーションが正常に動作していることを確認し、エクスポートされたFBXファイルが正しいパスに存在することを確認してください。

- **コンパイルエラーが発生する場合**: プラグインが正しくインストールされていることを確認し、プロジェクトのBuild.csファイルにMCPCppモジュールが正しく追加されていることを確認してください。

## ライセンス

このプラグインはMITライセンスで提供されます。詳細は[LICENSE](LICENSE)ファイルを参照してください。 
