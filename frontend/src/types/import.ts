export interface ImportValidationResult {
  ready: boolean
  already_imported: boolean
  message: string
  uploaded_file_name?: string
}

export interface ImportResult {
  success: boolean
  already_imported: boolean
  message: string

  import_history_id?: number
  file_name?: string
  uploaded_file_name?: string

  investments?: {
    created: number
    existing: number
  }

  transactions?: {
    imported: number
    skipped: number
  }

  dividends?: {
    imported: number
    skipped: number
  }

  cash_movements?: {
    imported: number
    skipped: number
  }

  positions_in_statement?: number
}