export interface ResumenMaletas {
  TotalMesas: number;
  TotalProducidas: number;
  TotalDeueltas: number;
  TotalSobreA: number;
  FaltanProducidas: number;
  FaltanDeueltas: number;
  FaltanSobreA: number;
}

export interface ApiResponse {
  success: boolean;
  message: string;
  data: ResumenMaletas;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  message: string;
}