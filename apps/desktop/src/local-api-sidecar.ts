import { ChildProcess, spawn } from 'node:child_process';
import { get } from 'node:http';

export interface LocalApiSidecarOptions {
  readonly cwd: string;
  readonly port: number;
  readonly readyTimeoutMs?: number;
}

/**
 * Manages the local FastAPI process (started via `uv run uvicorn`) as a
 * sidecar to the Electron shell. Owns the process lifecycle: start, readiness
 * check, and shutdown.
 */
export class LocalApiSidecar {
  private readonly cwd: string;
  private readonly port: number;
  private readonly readyTimeoutMs: number;
  private process: ChildProcess | null = null;

  constructor(options: LocalApiSidecarOptions) {
    this.cwd = options.cwd;
    this.port = options.port;
    this.readyTimeoutMs = options.readyTimeoutMs ?? 10_000;
  }

  get baseUrl(): string {
    return `http://127.0.0.1:${this.port}`;
  }

  async start(): Promise<void> {
    this.process = spawn(
      'uv',
      ['run', 'uvicorn', 'main:app', '--port', String(this.port)],
      { cwd: this.cwd, stdio: 'inherit' },
    );
    await this.waitUntilReady();
  }

  stop(): void {
    this.process?.kill();
    this.process = null;
  }

  private async waitUntilReady(): Promise<void> {
    const deadline = Date.now() + this.readyTimeoutMs;
    while (Date.now() < deadline) {
      if (await this.isHealthy()) {
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 300));
    }
    throw new Error(`Local API did not become ready within ${this.readyTimeoutMs}ms`);
  }

  private isHealthy(): Promise<boolean> {
    return new Promise((resolve) => {
      const request = get(`${this.baseUrl}/health`, (response) => {
        resolve(response.statusCode === 200);
        response.resume();
      });
      request.on('error', () => resolve(false));
    });
  }
}
