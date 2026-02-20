import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

interface LoginResponse {
  access_token: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenKey = 'auth_token';

  private _isLoggedIn = signal(!!localStorage.getItem(this.tokenKey));
  readonly isLoggedIn = this._isLoggedIn.asReadonly();

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>('/api/auth/login', { username, password }).pipe(
      tap((res) => {
        localStorage.setItem(this.tokenKey, res.access_token);
        this._isLoggedIn.set(true);
      })
    );
  }

  logout(): Observable<unknown> {
    return this.http.post<unknown>('/api/auth/logout', {}).pipe(
      tap(() => {
        localStorage.removeItem(this.tokenKey);
        this._isLoggedIn.set(false);
      })
    );
  }
}
