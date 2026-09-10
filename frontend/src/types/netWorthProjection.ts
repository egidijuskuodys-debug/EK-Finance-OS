export interface NetWorthProjectionPoint {
  year: number

  investment_value: number

  real_estate_value: number
  real_estate_loan_balance: number
  real_estate_equity: number

  net_worth: number
}


export interface NetWorthProjection {
  currency: string

  monthly_contribution: number
  annual_return_percent: number
  annual_property_growth: number

  projection_years: number

  starting_investment_value: number
  starting_real_estate_equity: number
  starting_net_worth: number

  final_investment_value: number
  final_real_estate_equity: number
  final_net_worth: number

  yearly_projection: (
    NetWorthProjectionPoint[]
  )
}