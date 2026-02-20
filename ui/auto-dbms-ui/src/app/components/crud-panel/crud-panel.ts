import { Component, input, signal } from '@angular/core';

export type CrudOperation = 'get-all' | 'get-one' | 'add' | 'update' | 'delete';

export interface CrudPanelConfig {
  operation: CrudOperation;
  label: string;
  description: string;
}

@Component({
  selector: 'app-crud-panel',
  templateUrl: './crud-panel.html',
  styleUrl: './crud-panel.scss',
})
export class CrudPanelComponent {
  readonly config = input.required<CrudPanelConfig>();
  readonly entityPath = input.required<string>();

  readonly expanded = signal(false);
  readonly result = signal<unknown>(null);
  readonly loading = signal(false);
  readonly errorMsg = signal<string | null>(null);

  readonly idInput = signal('');
  readonly jsonInput = signal('{}');

  toggle(): void {
    this.expanded.update((v) => !v);
  }

  get requiresId(): boolean {
    return ['get-one', 'update', 'delete'].includes(this.config().operation);
  }

  get requiresBody(): boolean {
    return ['add', 'update'].includes(this.config().operation);
  }

  get resultJson(): string {
    const r = this.result();
    return r !== null ? JSON.stringify(r, null, 2) : '';
  }

  onIdChange(event: Event): void {
    this.idInput.set((event.target as HTMLInputElement).value);
  }

  onJsonChange(event: Event): void {
    this.jsonInput.set((event.target as HTMLTextAreaElement).value);
  }
}
