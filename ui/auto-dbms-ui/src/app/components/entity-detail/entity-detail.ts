import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { EntityService, Entity } from '../../services/entity.service';
import { CrudPanelComponent, CrudPanelConfig } from '../crud-panel/crud-panel';

@Component({
  selector: 'app-entity-detail',
  imports: [RouterLink, CrudPanelComponent],
  templateUrl: './entity-detail.html',
  styleUrl: './entity-detail.scss',
})
export class EntityDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly entityService = inject(EntityService);

  readonly entityName = signal('');
  readonly entityPath = signal('');
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly panels: CrudPanelConfig[] = [
    { operation: 'get-all', label: 'Get All', description: 'Retrieve all records' },
    { operation: 'get-one', label: 'Get One', description: 'Retrieve a single record by ID' },
    { operation: 'add', label: 'Add', description: 'Create a new record' },
    { operation: 'update', label: 'Update', description: 'Update an existing record by ID' },
    { operation: 'delete', label: 'Delete', description: 'Delete a record by ID' },
  ];

  ngOnInit(): void {
    const name = this.route.snapshot.paramMap.get('name') ?? '';
    this.entityName.set(name);

    this.entityService.getEntities().subscribe({
      next: (entities: Entity[]) => {
        const match = entities.find((e) => e.name === name);
        if (match) {
          this.entityPath.set(match.path);
        } else {
          this.error.set(`Entity "${name}" not found.`);
        }
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Failed to load entity information.');
        this.loading.set(false);
      },
    });
  }

  execute(panel: CrudPanelComponent): void {
    const op = panel.config().operation;
    const path = this.entityPath();
    const id = panel.idInput();
    let body: unknown;

    if (panel.requiresBody) {
      try {
        body = JSON.parse(panel.jsonInput());
      } catch {
        panel.errorMsg.set('Invalid JSON in request body.');
        return;
      }
    }

    panel.result.set(null);
    panel.errorMsg.set(null);
    panel.loading.set(true);

    let operation$;
    switch (op) {
      case 'get-all':
        operation$ = this.entityService.getAll(path);
        break;
      case 'get-one':
        operation$ = this.entityService.getOne(path, id);
        break;
      case 'add':
        operation$ = this.entityService.add(path, body);
        break;
      case 'update':
        operation$ = this.entityService.update(path, id, body);
        break;
      case 'delete':
        operation$ = this.entityService.delete(path, id);
        break;
      default:
        panel.errorMsg.set('Unknown operation.');
        panel.loading.set(false);
        return;
    }

    operation$.subscribe({
      next: (res) => {
        panel.result.set(res);
        panel.loading.set(false);
      },
      error: (err) => {
        panel.errorMsg.set(err?.message ?? 'Request failed.');
        panel.loading.set(false);
      },
    });
  }
}
