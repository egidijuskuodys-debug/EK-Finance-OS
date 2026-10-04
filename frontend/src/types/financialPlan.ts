export interface FinancialPlanRequest {
  monthly_budget: number
  mortgage_share_percent: number
  expected_etf_return_percent: number
  projection_years: number[]
}


export interface FinancialPlanProjection {
  years: number
  projected_investment_value: number
  additional_invested: number
  estimated_growth: number
}


export interface FinancialPlanAction {
  action: string
  monthly_amount: number
  description: string
}


export interface FinancialPlanResponse {
  base_currency: string

  monthly_budget: number

  monthly_investment_amount: number

  monthly_mortgage_amount: number

  mortgage_share_percent: number

  investment_share_percent: number

  expected_etf_return_percent: number

  current_investment_wealth: number

  annual_investment_amount: number

  projections: FinancialPlanProjection[]

  actions: FinancialPlanAction[]
}