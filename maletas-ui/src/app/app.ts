import { Component } from '@angular/core';
import { DashboardElectoralComponent } from './components/dashboard-electoral/dashboard-electoral';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DashboardElectoralComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {}