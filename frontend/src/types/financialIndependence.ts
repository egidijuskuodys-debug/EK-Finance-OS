export interface FinancialIndependencePoint {
  year: number

  investment_value: number
  real_estate_equity: number
  net_worth: number

  investment_monthly_passive_income: number
  rental_monthly_cash_flow: number
  monthly_passive_income: number

  target_reached: boolean
}


export interface FinancialIndependence {
  currency: string

  monthly_income_target: number
  annual_income_target: number
  withdrawal_rate_percent: number

  investment_income_target: number
  required_capital: number

  current_fi_capital: number
  current_net_worth: number
  current_real_estate_equity: number

  investment_monthly_passive_income: number
  rental_monthly_cash_flow: number
  current_monthly_passive_income: number

  remaining_gap: number
  progress_percent: number

  years_to_goal: number | null
  current_age: number
  projected_age_at_goal: number | null

  monthly_contribution: number
  annual_return_percent: number
  annual_property_growth: number

  yearly_projection: (
    FinancialIndependencePoint[]
  )
}