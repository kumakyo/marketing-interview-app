const { contextBridge, ipcRenderer } = require('electron');

// セキュアなAPIをレンダラープロセスに公開
contextBridge.exposeInMainWorld('electronAPI', {
  // アプリケーション情報
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // ウィンドウ操作
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),
  
  // ファイル操作
  saveReport: (data) => ipcRenderer.invoke('save-report', data),
  openReportFolder: () => ipcRenderer.invoke('open-report-folder'),
  
  // 設定
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  
  // システム情報
  platform: process.platform,
  
  // イベントリスナー
  onBackendStatus: (callback) => {
    const unsubscribe = (event, status) => callback(status);
    ipcRenderer.on('backend-status', unsubscribe);
    return () => ipcRenderer.removeListener('backend-status', unsubscribe);
  }
});
