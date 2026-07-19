import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadComponent } from '../upload/upload.component';
import { TransactionTableComponent } from '../transaction-table/transaction-table.component';
import { ChartsComponent } from '../charts/charts.component';
import { FiltersComponent, ActiveFilters } from '../filters/filters.component';
import {
  UploadResponse,
  Transaction,
} from '../../services/transaction.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    UploadComponent,
    TransactionTableComponent,
    ChartsComponent,
    FiltersComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
  // Raw transactions from upload
  transactions: Transaction[] = [];
  uploadInfo: { filename: string; bank: string; rows: number } | null = null;
  isDarkTheme = true;

  // Active filters state
  activeFilters: ActiveFilters = { direction: 'All', categories: [] };

  // Called when upload component emits a successful response
  onUploadComplete(response: UploadResponse) {
    this.transactions = response.transactions;
    this.uploadInfo = {
      filename: response.filename,
      bank: response.bank,
      rows: response.rows,
    };
  }

  // Called when filters component emits new filter state
  onFiltersChanged(filters: ActiveFilters) {
    this.activeFilters = filters;
  }

  // Returns transactions filtered by direction and categories
  get filteredTransactions(): Transaction[] {
    return this.transactions.filter((t) => {
      // Direction filter
      if (this.activeFilters.direction === 'Income' && t.amount <= 0)
        return false;
      if (this.activeFilters.direction === 'Expenses' && t.amount >= 0)
        return false;

      // Category filter
      const cat = t.category || 'Other';
      if (!this.activeFilters.categories.includes(cat)) return false;

      return true;
    });
  }

  // Toggle dark/light theme
  toggleTheme() {
    this.isDarkTheme = !this.isDarkTheme;
    document.documentElement.setAttribute(
      'data-theme',
      this.isDarkTheme ? 'dark' : 'light',
    );
  }

  // Summary stats based on filtered transactions
  get totalIncome(): number {
    return this.filteredTransactions
      .filter((t) => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
  }

  get totalExpenses(): number {
    return this.filteredTransactions
      .filter((t) => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
  }

  get netBalance(): number {
    return this.totalIncome - this.totalExpenses;
  }
}
