// Copyright MCP Framework. All Rights Reserved.

#include "MCPClient.h"
#include "JsonObjectConverter.h"

FMCPClient::FMCPClient()
    : ServerURL(TEXT("http://127.0.0.1:8080"))
{
    // HTTPモジュールの初期化を確認
    check(FHttpModule::Get().IsHttpEnabled());
}

FMCPClient::~FMCPClient()
{
    // 必要に応じてリソースをクリーンアップ
}

void FMCPClient::SetServerURL(const FString& InServerURL)
{
    ServerURL = InServerURL;
    UE_LOG(LogTemp, Log, TEXT("MCPサーバーURLを設定しました: %s"), *ServerURL);
}

void FMCPClient::CheckConnection(TFunction<void(bool bSuccess, const FString& Message)> OnCompleteCallback)
{
    SendGetRequest(ServerURL + TEXT("/status"), 
        [OnCompleteCallback](bool bSuccess, const TSharedPtr<FJsonObject>& Response)
        {
            if (bSuccess)
            {
                FString Status = Response->GetStringField(TEXT("status"));
                if (Status == TEXT("running"))
                {
                    OnCompleteCallback(true, TEXT("MCPサーバーに接続しました"));
                }
                else
                {
                    OnCompleteCallback(false, FString::Printf(TEXT("MCPサーバーの状態が異常です: %s"), *Status));
                }
            }
            else
            {
                // 通常のエンドポイントで失敗したら、APIエンドポイントを試す
                OnCompleteCallback(false, TEXT("MCPサーバーに接続できませんでした"));
            }
        });
}

void FMCPClient::ExecuteBlenderCommand(const FString& Command, const TSharedPtr<FJsonObject>& Params, 
                                     TFunction<void(bool bSuccess, const TSharedPtr<FJsonObject>& Response)> OnCompleteCallback)
{
    // リクエストペイロードの作成
    TSharedPtr<FJsonObject> RequestObj = MakeShared<FJsonObject>();
    RequestObj->SetStringField(TEXT("command"), Command);
    RequestObj->SetObjectField(TEXT("params"), Params);
    
    FString JsonPayload;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonPayload);
    FJsonSerializer::Serialize(RequestObj.ToSharedRef(), Writer);
    
    // リクエストの送信
    SendPostRequest(ServerURL + TEXT("/api/blender/command"), JsonPayload, OnCompleteCallback);
}

void FMCPClient::ImportAsset(const FString& AssetPath, const FString& DestinationPath,
                           TFunction<void(bool bSuccess, const FString& AssetName)> OnCompleteCallback)
{
    // パラメータの作成
    TSharedPtr<FJsonObject> Params = MakeShared<FJsonObject>();
    Params->SetStringField(TEXT("path"), AssetPath);
    Params->SetStringField(TEXT("destination"), DestinationPath);
    
    // リクエストペイロードの作成
    TSharedPtr<FJsonObject> RequestObj = MakeShared<FJsonObject>();
    RequestObj->SetStringField(TEXT("command"), TEXT("import_asset"));
    RequestObj->SetObjectField(TEXT("params"), Params);
    
    FString JsonPayload;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonPayload);
    FJsonSerializer::Serialize(RequestObj.ToSharedRef(), Writer);
    
    // リクエストの送信
    SendPostRequest(ServerURL + TEXT("/api/unreal/command"), JsonPayload, 
        [OnCompleteCallback](bool bSuccess, const TSharedPtr<FJsonObject>& Response)
        {
            if (bSuccess)
            {
                FString AssetName;
                const TSharedPtr<FJsonObject>* ResultObj;
                if (Response->TryGetObjectField(TEXT("result"), ResultObj))
                {
                    const TSharedPtr<FJsonObject>* AssetInfoObj;
                    if ((*ResultObj)->TryGetObjectField(TEXT("asset_info"), AssetInfoObj))
                    {
                        AssetName = (*AssetInfoObj)->GetStringField(TEXT("name"));
                    }
                }
                
                OnCompleteCallback(true, AssetName);
            }
            else
            {
                OnCompleteCallback(false, TEXT(""));
            }
        });
}

void FMCPClient::SetGameMode(const FString& GameModePath, 
                           TFunction<void(bool bSuccess)> OnCompleteCallback)
{
    // パラメータの作成
    TSharedPtr<FJsonObject> Params = MakeShared<FJsonObject>();
    Params->SetStringField(TEXT("game_mode"), GameModePath);
    
    // リクエストペイロードの作成
    TSharedPtr<FJsonObject> RequestObj = MakeShared<FJsonObject>();
    RequestObj->SetStringField(TEXT("command"), TEXT("set_game_mode"));
    RequestObj->SetObjectField(TEXT("params"), Params);
    
    FString JsonPayload;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonPayload);
    FJsonSerializer::Serialize(RequestObj.ToSharedRef(), Writer);
    
    // リクエストの送信
    SendPostRequest(ServerURL + TEXT("/api/unreal/command"), JsonPayload, 
        [OnCompleteCallback](bool bSuccess, const TSharedPtr<FJsonObject>& Response)
        {
            OnCompleteCallback(bSuccess);
        });
}

void FMCPClient::SaveLevel(TFunction<void(bool bSuccess)> OnCompleteCallback)
{
    // リクエストペイロードの作成
    TSharedPtr<FJsonObject> RequestObj = MakeShared<FJsonObject>();
    RequestObj->SetStringField(TEXT("command"), TEXT("save_level"));
    RequestObj->SetObjectField(TEXT("params"), MakeShared<FJsonObject>());
    
    FString JsonPayload;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonPayload);
    FJsonSerializer::Serialize(RequestObj.ToSharedRef(), Writer);
    
    // リクエストの送信
    SendPostRequest(ServerURL + TEXT("/api/unreal/command"), JsonPayload, 
        [OnCompleteCallback](bool bSuccess, const TSharedPtr<FJsonObject>& Response)
        {
            OnCompleteCallback(bSuccess);
        });
}

void FMCPClient::SendPostRequest(const FString& URL, const FString& JsonPayload,
                               TFunction<void(bool bSuccess, const TSharedPtr<FJsonObject>& Response)> OnCompleteCallback)
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
    HttpRequest->SetURL(URL);
    HttpRequest->SetVerb(TEXT("POST"));
    HttpRequest->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    HttpRequest->SetContentAsString(JsonPayload);
    
    HttpRequest->OnProcessRequestComplete().BindLambda(
        [OnCompleteCallback](FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnectedSuccessfully)
        {
            bool bSuccess = false;
            TSharedPtr<FJsonObject> JsonResponse;
            
            if (bConnectedSuccessfully && Response.IsValid())
            {
                if (Response->GetResponseCode() == EHttpResponseCodes::Ok)
                {
                    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());
                    if (FJsonSerializer::Deserialize(Reader, JsonResponse))
                    {
                        bSuccess = true;
                    }
                    else
                    {
                        UE_LOG(LogTemp, Error, TEXT("JSONのパースに失敗しました: %s"), *Response->GetContentAsString());
                    }
                }
                else
                {
                    UE_LOG(LogTemp, Error, TEXT("HTTPリクエストが失敗しました: %d"), Response->GetResponseCode());
                }
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("HTTPリクエストの接続に失敗しました"));
            }
            
            OnCompleteCallback(bSuccess, JsonResponse);
        });
    
    HttpRequest->ProcessRequest();
}

void FMCPClient::SendGetRequest(const FString& URL,
                              TFunction<void(bool bSuccess, const TSharedPtr<FJsonObject>& Response)> OnCompleteCallback)
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
    HttpRequest->SetURL(URL);
    HttpRequest->SetVerb(TEXT("GET"));
    
    HttpRequest->OnProcessRequestComplete().BindLambda(
        [OnCompleteCallback](FHttpRequestPtr Request, FHttpResponsePtr Response, bool bConnectedSuccessfully)
        {
            bool bSuccess = false;
            TSharedPtr<FJsonObject> JsonResponse;
            
            if (bConnectedSuccessfully && Response.IsValid())
            {
                if (Response->GetResponseCode() == EHttpResponseCodes::Ok)
                {
                    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());
                    if (FJsonSerializer::Deserialize(Reader, JsonResponse))
                    {
                        bSuccess = true;
                    }
                    else
                    {
                        UE_LOG(LogTemp, Error, TEXT("JSONのパースに失敗しました: %s"), *Response->GetContentAsString());
                    }
                }
                else
                {
                    UE_LOG(LogTemp, Error, TEXT("HTTPリクエストが失敗しました: %d"), Response->GetResponseCode());
                }
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("HTTPリクエストの接続に失敗しました"));
            }
            
            OnCompleteCallback(bSuccess, JsonResponse);
        });
    
    HttpRequest->ProcessRequest();
} 
