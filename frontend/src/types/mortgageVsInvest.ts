export interface MortgageVsInvestRequest {
  monthly_extra_amount: number
  hybrid_mortgage_percentage: number
  annual_investment_returns: number[]
}


export interface MortgageBaseline {
  loan_balance: number
  annual_interest_rate: number
  monthly_payment: number
  remaining_months: number
  loan_end_date: string | null
  total_interest: number
  total_paid: number
}


export interface MortgageStrategyOutcome {
  strategy: string
  description: string

  mortgage_monthly_amount: number
  investment_monthly_amount: number

  payoff_months: number
  payoff_date: string

  interest_paid: number
  interest_saved: number

  investment_value_at_horizon: number
  advantage_vs_invest_only: number
}


export interface MortgageReturnComparison {
  annual_investment_return: number

  invest_only: MortgageStrategyOutcome
  repay_first: MortgageStrategyOutcome
  hybrid: MortgageStrategyOutcome

  winner: string
  winner_value: number
  difference_to_second: number
}


export interface MortgageVsInvestResponse {
  property_id: number
  property_name: string
  currency: string

  monthly_extra_amount: number
  hybrid_mortgage_percentage: number

  calculation_date: string
  comparison_end_date: string
  break_even_annual_return: number | null

  baseline: MortgageBaseline

  comparisons: MortgageReturnComparison[]

  assumptions: string[]
}
