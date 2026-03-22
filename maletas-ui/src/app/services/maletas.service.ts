import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ApiResponse, ErrorResponse } from '../models/maletas.model';
import { ApiResponse as ResumenGeneralApiResponse } from '../models/resumen-general.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MaletasService {
  // private apiUrl = 'http://localhost:3009/api/';
  private apiUrl = `${environment.apiUrl+'api/'}`;

  constructor(private http: HttpClient) { }

  getResumenMaletas(): Observable<ApiResponse> {
    return this.http.get<ApiResponse>(`${this.apiUrl}resumen-maletas`)
      .pipe(
        // retry() eliminado: el backend consulta APIs externas y un reintento
        // puede llegar mientras la primera petición aún procesa, acumulando
        // datos incorrectos (p.ej. cantidadNotificacion sumada dos veces).
        catchError(this.handleError)
      );
  }

  getResumenGeneral(): Observable<ResumenGeneralApiResponse> {
    return this.http.get<ResumenGeneralApiResponse>(`${this.apiUrl}resumen-general`)
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Error desconocido';

    if (error.error instanceof ErrorEvent) {
      errorMessage = `Error: ${error.error.message}`;
    } else {
      if (error.error && error.error.message) {
        errorMessage = error.error.message;
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }

    console.error('Error en MaletasService:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}