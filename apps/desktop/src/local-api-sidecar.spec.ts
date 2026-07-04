import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EventEmitter } from 'node:events';
import type { ChildProcess } from 'node:child_process';
import { LocalApiSidecar } from './local-api-sidecar';

const spawnMock = vi.fn();
const getMock = vi.fn();

vi.mock('node:child_process', () => ({
  spawn: (...args: unknown[]) => spawnMock(...args),
}));

vi.mock('node:http', () => ({
  get: (...args: unknown[]) => getMock(...args),
}));

interface FakeResponse {
  statusCode: number;
  resume: () => void;
}

function respondHealthy(): void {
  getMock.mockImplementation(
    (_url: string, callback: (response: FakeResponse) => void) => {
      callback({ statusCode: 200, resume: () => {} });
      return { on: vi.fn() };
    },
  );
}

function respondUnreachable(): void {
  getMock.mockImplementation(() => ({
    on: (event: string, handler: (error: Error) => void) => {
      if (event === 'error') {
        handler(new Error('ECONNREFUSED'));
      }
    },
  }));
}

function createFakeChildProcess(): ChildProcess {
  const emitter = new EventEmitter() as unknown as ChildProcess;
  emitter.kill = vi.fn();
  return emitter;
}

describe('LocalApiSidecar', () => {
  let fakeProcess: ChildProcess;

  beforeEach(() => {
    spawnMock.mockReset();
    getMock.mockReset();
    fakeProcess = createFakeChildProcess();
    spawnMock.mockReturnValue(fakeProcess);
  });

  it('spawns uv run uvicorn with the configured port and cwd', async () => {
    respondHealthy();
    const sidecar = new LocalApiSidecar({ cwd: '/path/to/local-api', port: 8756 });

    await sidecar.start();

    expect(spawnMock).toHaveBeenCalledWith(
      'uv',
      ['run', 'uvicorn', 'main:app', '--port', '8756'],
      { cwd: '/path/to/local-api', stdio: 'inherit' },
    );
  });

  it('retries the health check until the API responds', async () => {
    let callCount = 0;
    getMock.mockImplementation(
      (_url: string, callback: (response: FakeResponse) => void) => {
        callCount += 1;
        if (callCount < 3) {
          return {
            on: (event: string, handler: (error: Error) => void) => {
              if (event === 'error') {
                handler(new Error('ECONNREFUSED'));
              }
            },
          };
        }
        callback({ statusCode: 200, resume: () => {} });
        return { on: vi.fn() };
      },
    );

    const sidecar = new LocalApiSidecar({ cwd: '/x', port: 8756 });
    await sidecar.start();

    expect(callCount).toBe(3);
  });

  it('kills the underlying process on stop', async () => {
    respondHealthy();
    const sidecar = new LocalApiSidecar({ cwd: '/x', port: 8756 });
    await sidecar.start();

    sidecar.stop();

    expect(fakeProcess.kill).toHaveBeenCalled();
  });

  it('throws if the API never becomes healthy within the timeout', async () => {
    respondUnreachable();
    const sidecar = new LocalApiSidecar({ cwd: '/x', port: 8756, readyTimeoutMs: 50 });

    await expect(sidecar.start()).rejects.toThrow(/did not become ready/);
  });
});
