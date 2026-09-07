export type RebalancingAction = 'Add' | 'Reduce' | 'Hold'

export interface RebalancingItem {
  dimension: string
  target_key: string
  current_value: number
  current_percentage: number
  target_value: number
  target_percentage: number
  difference: number
  deviation_percentage_points: number
  action: RebalancingAction
  currency: string
}

export interface PortfolioRebalancing {
  portfolio_value: number
  base_currency: string
  targets_count: number
  items: RebalancingItem[]
}
