export interface DashboardAllocationItem {
  name: string
  value: number
  percentage: number
}

export interface DashboardPositionItem {
  ticker: string
  asset_type: string
  current_value: number
  profit_loss: number
  profit_loss_percent: number
}

export interface DashboardData {
  total_positions: number
  total_quantity: number

  portfolio_value: number
  total_invested: number

  securities_value: number
  cash_balance: number
  total_wealth: number

  total_deposits: number
  total_withdrawals: number
  net_contributions: number

  investment_gain: number
  investment_gain_percent: number

  unrealized_profit: number
  unrealized_profit_percent: number

  realized_profit: number

  dividend_net: number

  total_profit: number
  total_return_percent: number

  xirr: number | null

  best_position: string | null
  worst_position: string | null

  base_currency: string

  asset_allocation: DashboardAllocationItem[]

  top_positions: DashboardPositionItem[]
}