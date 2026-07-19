import {
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
  ElementRef,
  ViewChild,
  AfterViewInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Transaction } from '../../services/transaction.service';
import { Chart, registerables } from 'chart.js';

// Register all Chart.js components
Chart.register(...registerables);

type AggregationLevel = 'Daily' | 'Weekly' | 'Monthly';

@Component({
  selector: 'app-charts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './charts.component.html',
  styleUrl: './charts.component.scss',
})
export class ChartsComponent implements OnChanges, AfterViewInit {
  @Input() transactions: Transaction[] = [];
  @ViewChild('pieCanvas') pieCanvas!: ElementRef;
  @ViewChild('barCanvas') barCanvas!: ElementRef;

  private pieChart: Chart | null = null;
  private barChart: Chart | null = null;
  private viewInitialized = false;

  // Aggregation toggle state
  aggregationLevels: AggregationLevel[] = ['Daily', 'Weekly', 'Monthly'];
  selectedLevel: AggregationLevel = 'Monthly';

  // Category colors matching transaction-table component
  private categoryColors: Record<string, string> = {
    'Food & Groceries': '#FF9F43',
    Transport: '#54A0FF',
    Entertainment: '#A29BFE',
    Utilities: '#00CEC9',
    Healthcare: '#FF7675',
    Shopping: '#FD79A8',
    Income: '#00D68F',
    Savings: '#6C63FF',
    Mortgage: '#E17055',
    Other: '#636E72',
  };

  ngAfterViewInit() {
    this.viewInitialized = true;
  }

  private lastTransactionCount = -1;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['transactions']) {
      const current = this.transactions.length;
      // Only re-render if transaction count actually changed
      if (current !== this.lastTransactionCount && current > 0) {
        this.lastTransactionCount = current;
        setTimeout(() => {
          if (this.viewInitialized) {
            this.renderCharts();
          }
        }, 100);
      }
    }
  }

  // Called when user clicks a toggle button
  setAggregationLevel(level: AggregationLevel) {
    this.selectedLevel = level;
    this.renderBarChart();
  }

  private renderCharts() {
    this.renderPieChart();
    this.renderBarChart();
  }

  private renderPieChart() {
    // Group expenses by category (exclude income)
    const expensesByCategory: Record<string, number> = {};
    this.transactions
      .filter((t) => t.amount < 0)
      .forEach((t) => {
        const cat = t.category || 'Other';
        expensesByCategory[cat] =
          (expensesByCategory[cat] || 0) + Math.abs(t.amount);
      });

    const labels = Object.keys(expensesByCategory);
    const data = Object.values(expensesByCategory);
    const colors = labels.map((l) => this.categoryColors[l] || '#636E72');

    if (this.pieChart) this.pieChart.destroy();

    this.pieChart = new Chart(this.pieCanvas.nativeElement, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{ data, backgroundColor: colors, borderWidth: 0 }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#8B8FA8',
              font: { family: 'Inter', size: 12 },
              padding: 16,
            },
          },
        },
      },
    });
  }

  private renderBarChart() {
    // Group transactions based on selected aggregation level
    const grouped: Record<string, { income: number; expenses: number }> = {};

    this.transactions.forEach((t) => {
      const key = this.getGroupKey(t.date, this.selectedLevel);
      if (!grouped[key]) grouped[key] = { income: 0, expenses: 0 };
      if (t.amount > 0) grouped[key].income += t.amount;
      else grouped[key].expenses += Math.abs(t.amount);
    });

    const labels = Object.keys(grouped).sort();
    const income = labels.map((m) => grouped[m].income);
    const expenses = labels.map((m) => grouped[m].expenses);

    if (this.barChart) this.barChart.destroy();

    this.barChart = new Chart(this.barCanvas.nativeElement, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Income',
            data: income,
            backgroundColor: '#00D68F',
            borderRadius: 6,
          },
          {
            label: 'Expenses',
            data: expenses,
            backgroundColor: '#FF4D6D',
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: { color: '#8B8FA8', font: { family: 'Inter', size: 12 } },
          },
        },
        scales: {
          x: { ticks: { color: '#8B8FA8' }, grid: { color: '#2A2D3E' } },
          y: { ticks: { color: '#8B8FA8' }, grid: { color: '#2A2D3E' } },
        },
      },
    });
  }

  // Auto-detects date format: DD.MM.YYYY (PDF) or YYYY-MM-DD (CSV)
  private parseDate(date: string): Date {
    if (date.includes('.')) {
      const parts = date.split('.');
      return new Date(
        parseInt(parts[2]),
        parseInt(parts[1]) - 1,
        parseInt(parts[0]),
      );
    }
    return new Date(date);
  }

  // Returns a group key based on aggregation level
  private getGroupKey(date: string, level: AggregationLevel): string {
    const d = this.parseDate(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();

    if (level === 'Daily') {
      return `${day}.${month}.${year}`;
    } else if (level === 'Weekly') {
      const monday = new Date(d);
      monday.setDate(d.getDate() - d.getDay() + 1);
      return `W${this.getWeekNumber(monday)} ${year}`;
    } else {
      return `${month}.${year}`;
    }
  }

  // Returns ISO week number for a given date
  private getWeekNumber(d: Date): number {
    const onejan = new Date(d.getFullYear(), 0, 1);
    return Math.ceil(
      ((d.getTime() - onejan.getTime()) / 86400000 + onejan.getDay() + 1) / 7,
    );
  }
}
