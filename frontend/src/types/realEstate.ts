export interface RealEstateProperty {
  id: number

  name: string
  address: string | null
  property_type: string

  purchase_price: number
  current_value: number
  down_payment: number

  loan_original_amount: number
  loan_balance: number
  interest_rate: number | null

  monthly_payment: number
  monthly_rent: number
  monthly_expenses: number

  currency: string
  purchase_date: string | null

  equity: number

  annual_rent: number
  annual_expenses: number
  annual_loan_payments: number

  monthly_cash_flow: number
  annual_cash_flow: number

  gross_rental_yield: number
  net_rental_yield: number
  loan_to_value: number
}


export interface RealEstateSummary {
  properties_count: number

  total_current_value: number
  total_loan_balance: number
  total_equity: number

  total_monthly_rent: number
  total_monthly_expenses: number
  total_monthly_loan_payments: number

  total_monthly_cash_flow: number
  total_annual_cash_flow: number

  currency: string
}


export interface RealEstateCreate {
  name: string
  address: string | null
  property_type: string

  purchase_price: number
  current_value: number
  down_payment: number

  loan_original_amount: number
  loan_balance: number
  interest_rate: number | null

  monthly_payment: number
  monthly_rent: number
  monthly_expenses: number

  currency: string
  purchase_date: string | null
}


export type RealEstateUpdate = Partial<
  RealEstateCreate
>