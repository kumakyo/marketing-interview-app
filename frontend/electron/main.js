const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let backendProcess;

function createWindow() {
  // メインウィンドウを作成
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 1000,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    titleBarStyle: 'default',
    show: false,
    backgroundColor: '#f9fafb'
  });

  // ウィンドウが準備できたら表示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // 開発モードではlocalhost:3000、本番モードでは静的ファイルを読み込み
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../out/index.html'));
  }

  // 外部リンクをデフォルトブラウザで開く
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // ウィンドウが閉じられた時
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startBackend() {
  console.log('Starting Python backend...');
  
  // Pythonバックエンドを起動
  const backendPath = path.join(__dirname, '../../backend');
  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
  
  backendProcess = spawn(pythonExecutable, ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: backendPath,
    stdio: 'pipe',
    env: {
      ...process.env,
      PYTHONPATH: backendPath
    }
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.log(`Backend stderr: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });

  backendProcess.on('error', (error) => {
    console.error('Failed to start backend:', error);
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log('Stopping Python backend...');
    backendProcess.kill();
    backendProcess = null;
  }
}

// アプリケーションの準備ができた時
app.whenReady().then(() => {
  // バックエンドを起動
  if (!isDev) {
    startBackend();
    
    // バックエンドの起動を少し待ってからウィンドウを作成
    setTimeout(createWindow, 3000);
  } else {
    createWindow();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// すべてのウィンドウが閉じられた時
app.on('window-all-closed', () => {
  stopBackend();
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// アプリケーションが終了する前
app.on('before-quit', () => {
  stopBackend();
});

// セキュリティ: 新しいウィンドウの作成を防ぐ
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});

// セキュリティ: ナビゲーションを制限
app.on('web-contents-created', (event, contents) => {
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    
    if (parsedUrl.origin !== 'http://localhost:3000' && parsedUrl.origin !== 'http://127.0.0.1:3000') {
      event.preventDefault();
    }
  });
});
