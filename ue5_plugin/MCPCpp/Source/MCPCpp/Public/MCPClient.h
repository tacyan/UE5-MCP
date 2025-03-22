// Copyright MCP Framework. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Http.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

/**
 * MCPクライアント
 * 
 * このクラスはMCPサーバーとの通信を担当します。
 * RESTful APIを通じてサーバーにコマンドを送信し、結果を受け取ります。
 */
class MCPCPP_API FMCPClient
{
public:
    /** コンストラクタ */
    FMCPClient();
    
    /** デストラクタ */
    ~FMCPClient();
    
    /**
     * サーバーURLを設定
     * 
     * @param InServerURL サーバーのURL
     */
    void SetServerURL(const FString& InServerURL);
    
    /**
     * サーバーへの接続を確認
     * 
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void CheckConnection(TFunction<void(bool bSuccess, const FString& Message)> OnCompleteCallback);
    
    /**
     * Blenderコマンドを実行
     * 
     * @param Command 実行するコマンド
     * @param Params コマンドのパラメータ
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void ExecuteBlenderCommand(const FString& Command, const TSharedPtr<FJsonObject>& Params, 
                              TFunction<void(bool bSuccess, const TSharedPtr<FJsonObject>& Response)> OnCompleteCallback);
    
    /**
     * アセットをインポート
     * 
     * @param AssetPath インポートするアセットのパス
     * @param DestinationPath UE5内の保存先パス
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void ImportAsset(const FString& AssetPath, const FString& DestinationPath,
                    TFunction<void(bool bSuccess, const FString& AssetName)> OnCompleteCallback);
    
    /**
     * ゲームモードを設定
     * 
     * @param GameModePath ゲームモードのパス
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void SetGameMode(const FString& GameModePath, 
                    TFunction<void(bool bSuccess)> OnCompleteCallback);
    
    /**
     * レベルを保存
     * 
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void SaveLevel(TFunction<void(bool bSuccess)> OnCompleteCallback);

private:
    /** サーバーURL */
    FString ServerURL;
    
    /**
     * HTTP POSTリクエストを送信
     * 
     * @param URL リクエスト先のURL
     * @param JsonPayload JSONペイロード
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void SendPostRequest(const FString& URL, const FString& JsonPayload,
                        TFunction<void(bool bSuccess, const TSharedPtr<FJsonObject>& Response)> OnCompleteCallback);
    
    /**
     * HTTP GETリクエストを送信
     * 
     * @param URL リクエスト先のURL
     * @param OnCompleteCallback 完了時のコールバック関数
     */
    void SendGetRequest(const FString& URL,
                       TFunction<void(bool bSuccess, const TSharedPtr<FJsonObject>& Response)> OnCompleteCallback);
}; 
