import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  TransactionService,
  UploadResponse,
} from '../../services/transaction.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.scss',
})
export class UploadComponent {
  // Emits the parsed response to the parent component after successful upload
  @Output() uploadComplete = new EventEmitter<UploadResponse>();

  // UI state flags
  isDragging = false;
  isLoading = false;
  error: string | null = null;

  constructor(private transactionService: TransactionService) {}

  // Triggered when user drags a file over the drop zone
  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
  }

  // Triggered when user drags a file out of the drop zone
  onDragLeave() {
    this.isDragging = false;
  }

  // Triggered when a user drops a file onto the drop zone
  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    const file = event.dataTransfer?.files[0];
    if (file) this.processFile(file);
  }

  // Triggered when the user selects a file via the file input
  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) this.processFile(file);
  }

  // Validates file type and sends it to the backend via TransactionService
  processFile(file: File) {
    const allowed = ['application/pdf', 'text/csv'];
    if (!allowed.includes(file.type) && !file.name.endsWith('.csv')) {
      this.error = 'Only CSV or PDF files are accepted.';
      return;
    }

    this.isLoading = true;
    this.error = null;

    this.transactionService.uploadFile(file).subscribe({
      next: (response) => {
        this.isLoading = false;
        // Emit the response to the dashboard (parent) component
        this.uploadComplete.emit(response);
      },
      error: (err) => {
        this.isLoading = false;
        this.error = err.error?.detail || 'Upload failed. Please try again.';
      },
    });
  }
}
