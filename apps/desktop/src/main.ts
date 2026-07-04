import { app, BrowserWindow } from 'electron';
import * as path from 'node:path';
import { LocalApiSidecar } from './local-api-sidecar';

/**
 * Owns the Electron app lifecycle: the local API sidecar and the main window
 * that loads the built Angular frontend.
 */
class CadenceApplication {
  private readonly sidecar: LocalApiSidecar;
  private window: BrowserWindow | null = null;

  constructor(sidecar: LocalApiSidecar) {
    this.sidecar = sidecar;
  }

  async start(): Promise<void> {
    await this.sidecar.start();
    this.window = this.createMainWindow();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.window = this.createMainWindow();
      }
    });
  }

  stop(): void {
    this.sidecar.stop();
  }

  private createMainWindow(): BrowserWindow {
    const window = new BrowserWindow({
      width: 1200,
      height: 800,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration: false,
      },
    });

    const indexHtml = path.join(
      __dirname,
      '..',
      '..',
      'frontend',
      'dist',
      'frontend',
      'browser',
      'index.html',
    );
    void window.loadFile(indexHtml);

    return window;
  }
}

const sidecar = new LocalApiSidecar({
  cwd: path.join(__dirname, '..', '..', 'local-api'),
  port: 8756,
});
const application = new CadenceApplication(sidecar);

app.whenReady().then(() => void application.start());

app.on('window-all-closed', () => {
  application.stop();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => application.stop());
