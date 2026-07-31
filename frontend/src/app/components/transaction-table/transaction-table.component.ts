import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Transaction } from '../../services/transaction.service';

@Component({
  selector: 'app-transaction-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './transaction-table.component.html',
  styleUrl: './transaction-table.component.scss',
})
export class TransactionTableComponent {
  // Transactions received from parent component
  @Input() transactions: Transaction[] = [];

  // Category badge color mapping
  getCategoryColor(category: string): string {
    const colors: Record<string, string> = {
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
    return colors[category] || '#636E72';
  }
}
