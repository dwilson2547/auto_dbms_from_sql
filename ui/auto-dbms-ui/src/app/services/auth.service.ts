import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private _isLoggedIn = signal(false);

  readonly isLoggedIn = this._isLoggedIn.asReadonly();

  login(): void {
    // TODO: implement real authentication
    this._isLoggedIn.set(true);
  }

  logout(): void {
    // TODO: implement real authentication
    this._isLoggedIn.set(false);
  }
}
