// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "MCPShooterPlayerController.generated.h"

/**
 * シューティングゲームのプレイヤーコントローラー
 *
 * このクラスはプレイヤーの入力を処理し、
 * キャラクターの移動と射撃を制御します。
 */
UCLASS()
class SPACESHOOTERGAME_API AMCPShooterPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	/**
	 * コンストラクタ
	 * コントローラーの初期設定を行います
	 */
	AMCPShooterPlayerController();

protected:
	/**
	 * ゲーム開始時に呼び出される関数
	 */
	virtual void BeginPlay() override;

	/**
	 * 入力コンポーネントをセットアップする関数
	 */
	virtual void SetupInputComponent() override;

private:
	/**
	 * 前後方向の移動を処理する関数
	 * @param Value 移動量
	 */
	void MoveForward(float Value);

	/**
	 * 左右方向の移動を処理する関数
	 * @param Value 移動量
	 */
	void MoveRight(float Value);

	/**
	 * 発射ボタンを押した時に呼び出される関数
	 */
	void OnFire();
}; 
