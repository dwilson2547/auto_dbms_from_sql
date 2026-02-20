import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Entity {
  name: string;
  path: string;
}

@Injectable({ providedIn: 'root' })
export class EntityService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  getEntities(): Observable<Entity[]> {
    return this.http.get<Entity[]>(`${this.baseUrl}/get_all`);
  }

  getAll(entityPath: string): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.baseUrl}${entityPath}/get_all`);
  }

  getOne(entityPath: string, id: number | string): Observable<unknown> {
    return this.http.get<unknown>(`${this.baseUrl}${entityPath}/get/${id}`);
  }

  add(entityPath: string, data: unknown): Observable<unknown> {
    return this.http.post<unknown>(`${this.baseUrl}${entityPath}/add`, data);
  }

  update(entityPath: string, id: number | string, data: unknown): Observable<unknown> {
    return this.http.post<unknown>(`${this.baseUrl}${entityPath}/update/${id}`, data);
  }

  delete(entityPath: string, id: number | string): Observable<unknown> {
    return this.http.delete<unknown>(`${this.baseUrl}${entityPath}/delete/${id}`);
  }

  getFormData(entityPath: string): Observable<unknown> {
    return this.http.get<unknown>(`${this.baseUrl}${entityPath}/form-data`);
  }
}
