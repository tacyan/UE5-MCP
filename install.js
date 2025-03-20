#!/usr/bin/env node

/**
 * MCP (Model Context Protocol) インストールスクリプト
 * 
 * このスクリプトは、MCPをインストールし、必要な依存関係をセットアップします。
 * WindowsとMacの両方で動作します。
 * 
 * @author MCP Team
 */

const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');
const os = require('os');

// 色のエスケープシーケンス
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m'
};

/**
 * ログメッセージを出力する
 * 
 * @param {string} message - 出力するメッセージ
 * @param {string} type - メッセージタイプ (info, success, warn, error)
 */
function log(message, type = 'info') {
  const date = new Date().toISOString().replace('T', ' ').substr(0, 19);
  
  switch (type) {
    case 'success':
      console.log(`${colors.bright}${colors.green}[${date}] ✓ ${message}${colors.reset}`);
      break;
    case 'warn':
      console.log(`${colors.bright}${colors.yellow}[${date}] ⚠ ${message}${colors.reset}`);
      break;
    case 'error':
      console.log(`${colors.bright}${colors.red}[${date}] ✗ ${message}${colors.reset}`);
      break;
    default:
      console.log(`${colors.bright}${colors.blue}[${date}] ℹ ${message}${colors.reset}`);
  }
}

/**
 * システム情報を取得する
 * 
 * @returns {Object} システム情報
 */
function getSystemInfo() {
  const platform = os.platform();
  const isWindows = platform === 'win32';
  const isMac = platform === 'darwin';
  const isLinux = platform === 'linux';
  
  const pythonCommand = isWindows ? 'python' : 'python3';
  const pipCommand = isWindows ? 'pip' : 'pip3';
  
  return {
    platform,
    isWindows,
    isMac,
    isLinux,
    pythonCommand,
    pipCommand
  };
}

/**
 * Pythonがインストールされているか確認する
 * 
 * @param {string} pythonCommand - Pythonコマンド
 * @returns {boolean} インストールされているかどうか
 */
function checkPython(pythonCommand) {
  try {
    const version = execSync(`${pythonCommand} --version`).toString();
    log(`Python検出: ${version.trim()}`, 'success');
    return true;
  } catch (error) {
    log('Pythonが見つかりません。インストールしてください。', 'error');
    return false;
  }
}

/**
 * 依存関係をインストールする
 * 
 * @param {string} pipCommand - pipコマンド
 */
function installDependencies(pipCommand) {
  log('必要なPythonパッケージをインストールしています...');
  
  const pip = spawn(pipCommand, ['install', '-r', 'requirements.txt']);
  
  pip.stdout.on('data', (data) => {
    console.log(data.toString());
  });
  
  pip.stderr.on('data', (data) => {
    console.error(data.toString());
  });
  
  pip.on('close', (code) => {
    if (code === 0) {
      log('パッケージが正常にインストールされました', 'success');
      createConfig();
    } else {
      log(`依存関係のインストールに失敗しました。終了コード: ${code}`, 'error');
    }
  });
}

/**
 * 設定ファイルを作成する
 */
function createConfig() {
  // .env.exampleが存在するか確認
  if (fs.existsSync('.env.example')) {
    // .envファイルが存在しない場合のみコピー
    if (!fs.existsSync('.env')) {
      fs.copyFileSync('.env.example', '.env');
      log('.envファイルを作成しました', 'success');
    } else {
      log('.envファイルは既に存在します', 'info');
    }
  }
  
  // mcp_settings.jsonファイルを作成
  const mcpSettings = {
    server: {
      host: '127.0.0.1',
      port: 5000,
      autoStart: true
    },
    modules: {
      blender: {
        enabled: true,
        port: 5001
      },
      unreal: {
        enabled: true,
        port: 5002
      }
    },
    ai: {
      provider: 'mock',
      model: 'gpt-4'
    },
    paths: {
      blender: '',
      unreal: '',
      exports: './exports'
    },
    logging: {
      level: 'info',
      file: 'mcp.log'
    },
    version: '1.0.0'
  };
  
  fs.writeFileSync('mcp_settings.json', JSON.stringify(mcpSettings, null, 2));
  log('mcp_settings.jsonファイルを作成しました', 'success');
  
  // 実行権限を設定
  try {
    fs.chmodSync('run_mcp.py', 0o755);
    log('run_mcp.pyに実行権限を設定しました', 'success');
  } catch (error) {
    log('run_mcp.pyの権限設定に失敗しました: ' + error.message, 'warn');
  }
  
  log('インストールが完了しました! 以下のコマンドでMCPサーバーを起動できます:', 'success');
  log('  python run_mcp.py all', 'info');
  log('設定を変更するには、mcp_settings.jsonファイルを編集してください。', 'info');
}

// メイン実行部分
(function main() {
  log('MCP (Model Context Protocol) インストーラー', 'info');
  log('------------------------------------', 'info');
  
  const sysInfo = getSystemInfo();
  log(`実行環境: ${sysInfo.platform}`, 'info');
  
  if (checkPython(sysInfo.pythonCommand)) {
    installDependencies(sysInfo.pipCommand);
  }
})(); 
