import { Component, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface HealthResponse {
  status: string;
  db: string;
  ping_count: number;
}

@Component({
  selector: 'app-root',
  imports: [],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('Cadence');
  protected readonly health = signal<HealthResponse | null>(null);
  protected readonly error = signal<string | null>(null);

  constructor(private readonly http: HttpClient) {
    this.http.get<HealthResponse>('http://127.0.0.1:8756/health').subscribe({
      next: (res) => this.health.set(res),
      error: () => this.error.set('Local API unreachable on 127.0.0.1:8756'),
    });
  }
}
