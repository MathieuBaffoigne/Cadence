mod sidecar;

use std::path::PathBuf;
use std::sync::Mutex;

use sidecar::LocalApiSidecar;
use tauri::Manager;

struct SidecarState(Mutex<LocalApiSidecar>);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      let local_api_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../local-api");
      let mut sidecar = LocalApiSidecar::new(local_api_dir, 8756);

      tauri::async_runtime::block_on(sidecar.start())?;

      app.manage(SidecarState(Mutex::new(sidecar)));

      Ok(())
    })
    .build(tauri::generate_context!())
    .expect("error while building tauri application")
    .run(|app_handle, event| {
      if let tauri::RunEvent::ExitRequested { .. } = event {
        app_handle.state::<SidecarState>().0.lock().unwrap().stop();
      }
    });
}
