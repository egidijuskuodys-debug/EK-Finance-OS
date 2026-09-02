export interface Dividend {
  id: number

  investment_id: number

  payment_date: string

  gross_amount: number
  tax_amount: number
  net_amount: number

  currency: string

  notes: string | null
}