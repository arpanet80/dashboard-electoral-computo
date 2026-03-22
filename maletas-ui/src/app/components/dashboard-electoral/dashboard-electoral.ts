import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { MaletasService } from '../../services/maletas.service';
import { Subscription, switchMap, timer } from 'rxjs';
import { ResumenGeneral } from '../../models/resumen-general.model';

@Component({
  selector: 'app-dashboard-electoral',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-electoral.html',
  styleUrl: './dashboard-electoral.css',
})
export class DashboardElectoralComponent implements OnInit, OnDestroy {
  resumen: ResumenGeneral | null = null;
  loading = false;
  error: string | null = null;
  lastUpdate: Date | null = null;
  isRefreshing = false;
  isDark = true;

  // Toogle de tema oscuro y claro
  toggleTheme() {
    this.isDark = !this.isDark;
  }

  
  private refreshSubscription: Subscription | null = null;

  // Circunferencia del donut: 2π * r = 2π * 52 ≈ 326.73
  private readonly CIRCUMFERENCE = 2 * Math.PI * 52;

  constructor(private maletasService: MaletasService) {}

  ngOnInit() {
    this.loadData();

    // Actualización automática cada 2 minutos
    this.refreshSubscription = timer(120000, 120000)
      .pipe(
        switchMap(() => {
          this.isRefreshing = true;
          return this.maletasService.getResumenGeneral();
        })
      )
      .subscribe({
        next: (response) => {
          const scrollY = window.scrollY;
          this.resumen = response.data;
          this.lastUpdate = new Date();
          this.isRefreshing = false;
          this.error = null;
          setTimeout(() => window.scrollTo({ top: scrollY, behavior: 'instant' }), 0);
        },
        error: (err) => {
          this.error = err.message;
          this.isRefreshing = false;
        },
      });
  }

  loadData() {
    // Guardar posición del scroll antes de actualizar
    const scrollY = window.scrollY;

    this.loading = true;
    this.error = null;

    this.maletasService.getResumenGeneral().subscribe({
      next: (response) => {
        this.resumen = response.data;
        this.lastUpdate = new Date();
        this.loading = false;
        // Restaurar posición del scroll después de que Angular actualice la vista
        setTimeout(() => window.scrollTo({ top: scrollY, behavior: 'instant' }), 0);
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      },
    });
  }

  ngOnDestroy() {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  // ─── Helpers numéricos ───────────────────────────────────────────────────────

  formatNumber(value: number | undefined | null): string {
    if (value == null) return '0';
    return value.toLocaleString('es-BO');
  }

  getPercentage(completed: number | undefined, total: number | undefined): number {
    if (!completed || !total || total === 0) return 0;
    return Math.min(100, Math.round((completed / total) * 100));
  }

  // ─── Donuts de MONITOREO ─────────────────────────────────────────────────────

  /**
   * Calcula el stroke-dasharray para el arco relleno del donut.
   * Usa la circunferencia de r=52.
   */
  getDonutDasharray(completed: number | undefined, total: number | undefined): string {
    const pct = this.getPercentage(completed, total);
    const filled = (pct / 100) * this.CIRCUMFERENCE;
    const gap = this.CIRCUMFERENCE - filled;
    return `${filled.toFixed(2)} ${gap.toFixed(2)}`;
  }

  /**
   * Color del arco según porcentaje de avance.
   */
  getDonutColor(pct: number): string {
    if (pct >= 90) return '#10b981'; // verde esmeralda
    if (pct >= 60) return '#3b82f6'; // azul
    if (pct >= 30) return '#f59e0b'; // ámbar
    return '#ef4444';                // rojo
  }

  // ─── Datos de MALETAS (nombres internos corregidos) ──────────────────────────

  get totalMesas(): number {
    return this.resumen?.maletas?.TotalMesas ?? 0;
  }

  /** TotalProducidas — alias legible: "Entregadas" */
  get totalEntregadas(): number {
    return this.resumen?.maletas?.TotalProducidas ?? 0;
  }

  /** TotalDeueltas — alias legible: "Devueltas" */
  get totalDevueltas(): number {
    return this.resumen?.maletas?.TotalDeueltas ?? 0;
  }

  get totalSobreA(): number {
    return this.resumen?.maletas?.TotalSobreA ?? 0;
  }

  /** FaltanProducidas — alias legible: "Faltan Entregadas" */
  get faltanEntregadas(): number {
    return this.resumen?.maletas?.FaltanProducidas ?? 0;
  }

  /** FaltanDeueltas — alias legible: "Faltan Devueltas" */
  get faltanDevueltas(): number {
    return this.resumen?.maletas?.FaltanDeueltas ?? 0;
  }

  get faltanSobreA(): number {
    return this.resumen?.maletas?.FaltanSobreA ?? 0;
  }

  // ─── Datos de MONITOREO ──────────────────────────────────────────────────────

  get aperturaMesa(): number {
    return this.resumen?.monitoreo?.aperturaMesa ?? 0;
  }

  get cierreMesa(): number {
    return this.resumen?.monitoreo?.cierreMesa ?? 0;
  }

  get recepcionSobreA(): number {
    return this.resumen?.monitoreo?.recepcionSobreAPorNotario ?? 0;
  }

  get totalMesasMonitoreo(): number {
    return this.resumen?.monitoreo?.totalMesas ?? 0;
  }

  // ─── Barra de progreso para maletas ─────────────────────────────────────────

  getBarWidth(completed: number, total: number): string {
    if (!total) return '0%';
    return `${Math.min(100, Math.round((completed / total) * 100))}%`;
  }

  getBarColor(completed: number, total: number): string {
    const pct = this.getPercentage(completed, total);
    if (pct >= 90) return '#10b981';
    if (pct >= 60) return '#3b82f6';
    if (pct >= 30) return '#f59e0b';
    return '#ef4444';
  }

  // ─── KPIs adicionales de monitoreo ───────────────────────────────────────────

  get kpisMonitoreo() {
    const m = this.resumen?.monitoreo;
    if (!m) return [];
    return [
      { label: 'Jurados Notificados',       value: m.cantidadNotificacion,           icon: '📢' },
      { label: 'Jurados Capacitados',       value: m.cantidadCapacitacion,           icon: '📚' },
      { label: 'Estipendio Entregado',        value: m.cantidadEstipendio,             icon: '💰' },
      { label: 'Rec. Maleta CDL',   value: m.recepcionMaletaCdl,             icon: '📦' },
      { label: 'Maletas Resguardadas en Recinto Seguro', value: m.resguardoMaletaRecintoElectoral,icon: '🏛️' },
      { label: 'Entrega Maleta a Jurado',  value: m.entregaMaletaJuradoElectoral,   icon: '🤝' },
      { label: 'Mesas Abiertas',    value: m.aperturaMesa,                   icon: '✅' },
      { label: 'Mesas Cerradas',    value: m.cierreMesa,                     icon: '🔒' },
      { label: 'No Apertura',       value: m.noAperturaMesa,                 icon: '❌' },
      { label: 'Entrega Sobres A Notario',  value: m.recepcionSobreAPorNotario,      icon: '📜' },
    ];
  }

  get tablaJurados() {
    const m = this.resumen?.monitoreo;
    if (!m) return [];
    return [
      { concepto: 'Jurados Sorteados',    valor: m.juradoSorteado,         color: '#3b82f6' },
      { concepto: 'Jurados Excusados',    valor: m.juradoExcusado,         color: '#f59e0b' },
      { concepto: 'Jurados de la Fila',   valor: m.juradoDeLaFila,         color: '#8b5cf6' },
      { concepto: 'Total Estados Jurado', valor: m.totalEstadosJurados,    color: '#64748b' },
      { concepto: 'Total Jurados Sorteados', valor: m.totalEtapaJuradoElegidos, color: '#10b981' },
    ];
  }

  hasMaletasData(): boolean {
    return !!this.resumen?.maletas && !this.resumen.maletas.error && this.totalMesas > 0;
  }

  hasMonitoreoData(): boolean {
    return !!this.resumen?.monitoreo && !this.resumen.monitoreo.error && this.totalMesasMonitoreo > 0;
  }
}
