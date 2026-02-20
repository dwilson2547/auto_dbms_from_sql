import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { EntityService, Entity } from '../../services/entity.service';

@Component({
  selector: 'app-entity-list',
  imports: [RouterLink],
  templateUrl: './entity-list.html',
  styleUrl: './entity-list.scss',
})
export class EntityListComponent implements OnInit {
  private readonly entityService = inject(EntityService);

  readonly entities = signal<Entity[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.entityService.getEntities().subscribe({
      next: (data) => {
        this.entities.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Failed to load entities. Please ensure the API is running.');
        this.loading.set(false);
      },
    });
  }
}
