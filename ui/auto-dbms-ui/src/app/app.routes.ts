import { Routes } from '@angular/router';
import { EntityListComponent } from './components/entity-list/entity-list';
import { EntityDetailComponent } from './components/entity-detail/entity-detail';

export const routes: Routes = [
  { path: '', component: EntityListComponent },
  { path: 'entity/:name', component: EntityDetailComponent },
];
