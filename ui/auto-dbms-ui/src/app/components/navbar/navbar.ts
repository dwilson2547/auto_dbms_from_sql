import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, FormsModule],
  templateUrl: './navbar.html',
  styleUrl: './navbar.scss',
})
export class NavbarComponent {
  readonly auth = inject(AuthService);
  readonly showLoginForm = signal(false);
  readonly username = signal('');
  readonly password = signal('');
  readonly loginError = signal<string | null>(null);

  toggleLogin(): void {
    this.showLoginForm.update((v) => !v);
    this.loginError.set(null);
    this.username.set('');
    this.password.set('');
  }

  submitLogin(): void {
    this.auth.login(this.username(), this.password()).subscribe({
      next: () => {
        this.showLoginForm.set(false);
        this.loginError.set(null);
        this.username.set('');
        this.password.set('');
      },
      error: () => {
        this.loginError.set('Invalid credentials. Please try again.');
      },
    });
  }

  doLogout(): void {
    this.auth.logout().subscribe();
  }
}
