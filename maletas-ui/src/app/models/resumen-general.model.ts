export interface ResumenGeneral {
  maletas: ResumenMaletas;
  monitoreo: ReporteMonitoreo;
  metadata: Metadata;
}

export interface ResumenMaletas {
  TotalMesas: number;
  TotalProducidas: number;
  TotalDeueltas: number;
  TotalSobreA: number;
  FaltanProducidas: number;
  FaltanDeueltas: number;
  FaltanSobreA: number;
  error?: string; // Opcional, solo en caso de error
}

export interface ReporteMonitoreo {
  agrupacion: string;
  idPaisAgrupado: number;
  cantidadNotificacion: number;
  cantidadCapacitacion: number;
  cantidadEstipendio: number;
  recepcionMaletaCdl: number;
  resguardoMaletaRecintoElectoral: number;
  entregaMaletaJuradoElectoral: number;
  aperturaMesa: number;
  cierreMesa: number;
  noAperturaMesa: number;
  recepcionSobreAPorNotario: number;
  juradoSorteado: number;
  juradoExcusado: number;
  juradoDeLaFila: number;
  totalEstadosJurados: number;
  totalMaletas: number;
  totalEtapaJuradoElegidos: number;
  totalMesas: number;
  usuarioRegistro: string;
  error?: string; // Opcional, solo en caso de error
}

export interface Metadata {
  timestamp: string;
  departamento: number;
  fuentes: Fuentes;
}

export interface Fuentes {
  maletas: boolean;
  monitoreo: boolean;
}

export interface ApiResponse {
  success: boolean;
  message: string;
  data: ResumenGeneral;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  message: string;
}