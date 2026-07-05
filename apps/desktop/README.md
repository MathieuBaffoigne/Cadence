# Desktop shell (Tauri)

Packages the Angular frontend into an installable, offline-capable desktop app.

On startup, spawns the local FastAPI sidecar (`../local-api`, via `uv run uvicorn`) as a child process, waits for it to be healthy, then opens the main window loading the built Angular app (`../frontend/dist/frontend/browser`).

Rust. `LocalApiSidecar` (`src-tauri/src/sidecar.rs`) owns the sidecar process lifecycle; wired into the Tauri app lifecycle in `src-tauri/src/lib.rs` (`setup` starts it, `ExitRequested` stops it).

## Run

```
cargo tauri dev
```

This runs `beforeDevCommand`/`beforeBuildCommand` from `src-tauri/tauri.conf.json` automatically (starts the Angular dev server), builds the Rust binary, spawns the `local-api` sidecar, and opens the window.

## Build

```
cargo tauri build
```

## Test

```
cd src-tauri
cargo test
```

Sidecar readiness/retry logic is tested against a real (but bare-bones, in-test) TCP server — no mocking of the process or HTTP layer, see `src-tauri/src/sidecar.rs`.
