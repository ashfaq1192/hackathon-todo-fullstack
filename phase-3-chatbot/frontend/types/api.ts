// API error response types

export interface APIError {
  detail: string;                // Human-readable error message
  code?: string;                 // Optional error code
  field?: string;                // Optional field that caused error
}

export interface ValidationError {
  field: string;                 // Field name that failed validation
  message: string;               // Validation error message
}
