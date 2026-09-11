export interface MonthlyInvestNowItem {
  target: string
  amount: number
  currency: string
  current_percentage: number
  future_percentage: number
  target_percentage: number
  priority: string
  reason: string
}


export interface MonthlyBrokerRoutingItem {
  broker: string
  amount: number
  currency: string
  current_percentage: number
  future_percentage: number
  target_percentage: number
  reason: string
}


export interface MonthlyPauseItem {
  dimension: string
  target: string
  action: string
  current_percentage: number
  target_percentage: number
  amount_over_target: number
  currency: string
  reason: string
}


export interface MonthlyReviewItem {
  category: string
  priority: string
  action: string
  title: string
  message: string
  reason: string
}


export interface MonthlyPlanSummary {
  invest_now_count: number
  broker_routes_count: number
  pause_count: number
  review_count: number
}


export interface MonthlyPlanGuidance {
  asset_and_broker_note: string
  sell_note: string
}


export interface MonthlyInvestmentPlan {
  generated_date: string
  currency: string
  portfolio_value: number
  monthly_amount: number
  allocated_amount: number
  unallocated_amount: number
  summary: MonthlyPlanSummary
  invest_now: MonthlyInvestNowItem[]
  broker_routing: MonthlyBrokerRoutingItem[]
  pause_new_contributions: MonthlyPauseItem[]
  review_items: MonthlyReviewItem[]
  guidance: MonthlyPlanGuidance
}