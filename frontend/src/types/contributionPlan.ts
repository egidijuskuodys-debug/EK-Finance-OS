export interface ContributionAllocation {
  target_key: string
  current_value: number
  target_percentage: number
  suggested_amount: number
  future_value: number
  future_percentage: number
}

export interface ContributionGroup {
  dimension: string
  contribution_amount: number
  allocated_amount: number
  allocations: ContributionAllocation[]
}

export interface ContributionPlan {
  portfolio_value: number
  contribution_amount: number
  future_portfolio_value: number
  base_currency: string
  groups: ContributionGroup[]
}
