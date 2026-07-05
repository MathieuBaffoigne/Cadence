use std::path::PathBuf;
use std::process::{Child, Command};
use std::time::Duration;

use tokio::time::{sleep, Instant};

#[derive(Debug)]
pub struct SidecarError(String);

impl std::fmt::Display for SidecarError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl std::error::Error for SidecarError {}

/// Owns the local-api FastAPI process spawned as a sidecar to the Tauri shell:
/// start, readiness poll, shutdown. Rust equivalent of the former Electron
/// `LocalApiSidecar` class.
pub struct LocalApiSidecar {
    cwd: PathBuf,
    port: u16,
    ready_timeout: Duration,
    child: Option<Child>,
}

impl LocalApiSidecar {
    pub fn new(cwd: PathBuf, port: u16) -> Self {
        Self {
            cwd,
            port,
            ready_timeout: Duration::from_secs(10),
            child: None,
        }
    }

    pub fn base_url(&self) -> String {
        format!("http://127.0.0.1:{}", self.port)
    }

    pub async fn start(&mut self) -> Result<(), SidecarError> {
        let child = Command::new("uv")
            .args(["run", "uvicorn", "main:app", "--port", &self.port.to_string()])
            .current_dir(&self.cwd)
            .spawn()
            .map_err(|e| SidecarError(format!("failed to spawn local-api: {e}")))?;

        self.child = Some(child);
        wait_until_healthy(&self.base_url(), self.ready_timeout).await
    }

    pub fn stop(&mut self) {
        if let Some(mut child) = self.child.take() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

impl Drop for LocalApiSidecar {
    fn drop(&mut self) {
        self.stop();
    }
}

pub(crate) async fn wait_until_healthy(base_url: &str, timeout: Duration) -> Result<(), SidecarError> {
    let health_url = format!("{base_url}/health");
    let deadline = Instant::now() + timeout;

    while Instant::now() < deadline {
        if is_healthy(&health_url).await {
            return Ok(());
        }
        sleep(Duration::from_millis(300)).await;
    }

    Err(SidecarError(format!(
        "local-api did not become ready within {timeout:?}"
    )))
}

async fn is_healthy(url: &str) -> bool {
    reqwest::get(url)
        .await
        .map(|response| response.status().is_success())
        .unwrap_or(false)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::thread;

    #[test]
    fn base_url_uses_loopback_and_configured_port() {
        let sidecar = LocalApiSidecar::new(PathBuf::from("."), 8756);
        assert_eq!(sidecar.base_url(), "http://127.0.0.1:8756");
    }

    /// Binds a bare HTTP responder only after `delay` has elapsed, so requests
    /// made before that get a real connection refusal (nothing is listening
    /// yet) — exercising the retry loop in `wait_until_healthy` for real,
    /// instead of mocking the HTTP client.
    fn start_delayed_health_server(port: u16, delay: Duration) {
        thread::spawn(move || {
            thread::sleep(delay);
            let listener = TcpListener::bind(("127.0.0.1", port)).expect("bind test port");
            for stream in listener.incoming() {
                let mut stream = match stream {
                    Ok(s) => s,
                    Err(_) => continue,
                };
                let mut buf = [0u8; 512];
                let _ = stream.read(&mut buf);
                let _ = stream.write_all(b"HTTP/1.1 200 OK\r\ncontent-length: 0\r\n\r\n");
            }
        });
    }

    #[tokio::test]
    async fn retries_until_the_server_answers() {
        let port = 18831;
        start_delayed_health_server(port, Duration::from_millis(400));

        let result = wait_until_healthy(&format!("http://127.0.0.1:{port}"), Duration::from_secs(2)).await;

        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn times_out_if_never_healthy() {
        // Port 18832: nothing listens here for the whole test, every attempt fails.
        let result = wait_until_healthy("http://127.0.0.1:18832", Duration::from_millis(200)).await;

        assert!(result.is_err());
    }
}
