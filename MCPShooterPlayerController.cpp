// Fill out your copyright notice in the Description page of Project Settings.

#include "MCPShooterPlayerController.h"
#include "MCPShooterCharacter.h"
#include "MCPShooterProjectile.h"
#include "GameFramework/PawnMovementComponent.h"

AMCPShooterPlayerController::AMCPShooterPlayerController()
{
	// 毎フレーム更新するように設定
	PrimaryActorTick.bCanEverTick = true;
}

void AMCPShooterPlayerController::BeginPlay()
{
	Super::BeginPlay();
}

void AMCPShooterPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	// 移動の入力バインディングを追加
	InputComponent->BindAxis("MoveForward", this, &AMCPShooterPlayerController::MoveForward);
	InputComponent->BindAxis("MoveRight", this, &AMCPShooterPlayerController::MoveRight);

	// 射撃の入力バインディングを追加
	InputComponent->BindAction("Fire", IE_Pressed, this, &AMCPShooterPlayerController::OnFire);
}

void AMCPShooterPlayerController::MoveForward(float Value)
{
	AMCPShooterCharacter* PlayerShip = Cast<AMCPShooterCharacter>(GetPawn());
	if (PlayerShip && Value != 0.0f)
	{
		// 前方方向ベクトルを取得
		const FVector Direction = PlayerShip->GetActorForwardVector();
		// 移動入力を適用
		PlayerShip->AddMovementInput(Direction, Value);
	}
}

void AMCPShooterPlayerController::MoveRight(float Value)
{
	AMCPShooterCharacter* PlayerShip = Cast<AMCPShooterCharacter>(GetPawn());
	if (PlayerShip && Value != 0.0f)
	{
		// 右方向ベクトルを取得
		const FVector Direction = PlayerShip->GetActorRightVector();
		// 移動入力を適用
		PlayerShip->AddMovementInput(Direction, Value);
	}
}

void AMCPShooterPlayerController::OnFire()
{
	AMCPShooterCharacter* PlayerShip = Cast<AMCPShooterCharacter>(GetPawn());
	if (PlayerShip)
	{
		PlayerShip->Fire();
	}
} 
