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
  loan_end_date: string | null

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
  loan_end_date: string | null
}


export type RealEstateUpdate = Partial<
  RealEstateCreate
>


export interface RealEstateProjectionPoint {
  year: number
  projection_date: string

  property_value: number
  loan_balance: number
  equity: number

  principal_paid: number
  interest_paid: number
}


export interface RealEstateProjection {
  property_id: number
  property_name: string
  currency: string

  annual_property_growth: number
  annual_interest_rate: number
  monthly_payment: number

  loan_end_date: string | null
  projection_years: number

  total_principal_paid: number
  total_interest_paid: number

  points: RealEstateProjectionPoint[]
}