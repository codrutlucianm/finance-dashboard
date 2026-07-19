import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnChanges,
  HostListener,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Transaction } from '../../services/transaction.service';
export type DirectionFilter = 'All' | 'Income' | 'Expenses';

export interface ActiveFilters {
  direction: DirectionFilter;
  categories: string[];
}

@Component({
  selector: 'app-filters',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './filters.component.html',
  styleUrl: './filters.component.scss',
})
export class FiltersComponent implements OnChanges {
  // Raw transactions used to extract available categories
  @Input() transactions: Transaction[] = [];

  // Emits active filters to parent on every change
  @Output() filtersChanged = new EventEmitter<ActiveFilters>();

  // Direction toggle options
  directionOptions: DirectionFilter[] = ['All', 'Income', 'Expenses'];
  selectedDirection: DirectionFilter = 'All';

  // Category dropdown state
  availableCategories: string[] = [];
  selectedCategories: string[] = [];
  isDropdownOpen = false;

  ngOnChanges() {
    const cats = new Set(this.transactions.map((t) => t.category || 'Other'));
    this.availableCategories = Array.from(cats).sort();
    this.selectedCategories = [...this.availableCategories];
    // Defer emit to avoid ExpressionChangedAfterItHasBeenCheckedError
    setTimeout(() => this.emitFilters());
  }

  // Toggle direction filter
  setDirection(direction: DirectionFilter) {
    this.selectedDirection = direction;
    this.emitFilters();
  }

  // Toggle a single category on/off
  toggleCategory(category: string) {
    if (this.selectedCategories.includes(category)) {
      // Prevent deselecting all categories
      if (this.selectedCategories.length === 1) return;
      this.selectedCategories = this.selectedCategories.filter(
        (c) => c !== category,
      );
    } else {
      this.selectedCategories = [...this.selectedCategories, category];
    }
    this.emitFilters();
  }

  // Select all categories
  selectAll() {
    this.selectedCategories = [...this.availableCategories];
    this.emitFilters();
  }

  // Deselect all except first (at least one must be selected)
  clearAll() {
    this.selectedCategories = [this.availableCategories[0]];
    this.emitFilters();
  }

  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  closeDropdown() {
    this.isDropdownOpen = false;
  }

  // Emit current filter state to parent
  private emitFilters() {
    this.filtersChanged.emit({
      direction: this.selectedDirection,
      categories: this.selectedCategories,
    });
  }

  // Label for dropdown button
  get dropdownLabel(): string {
    if (this.selectedCategories.length === this.availableCategories.length) {
      return 'All Categories';
    }
    if (this.selectedCategories.length === 1) {
      return this.selectedCategories[0];
    }
    return `${this.selectedCategories.length} Categories`;
  }

  // Category color for visual indicator in dropdown
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

  // Close dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown')) {
      this.isDropdownOpen = false;
    }
  }
}
