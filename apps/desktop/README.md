# Desktop shell (Electron)

Packages the Angular frontend into an installable, offline-capable desktop app.

On startup, spawns the local FastAPI sidecar (`../local-api`, via `uv run uvicorn`) as a child process, waits for it to be healthy, then opens the main window loading the built Angular app (`../frontend/dist/frontend/browser`).

TypeScript, strict mode. `LocalApiSidecar` owns the sidecar process lifecycle; `CadenceApplication` owns the Electron window lifecycle.

## Run

Build the frontend first (`../frontend`: `npx ng build`), then:

```
npm run build
npm start
```

## Test

```
npm test
```

Vitest, `node:child_process` and `node:http` mocked (see `src/local-api-sidecar.spec.ts`) — no real process spawned, no real network call.
