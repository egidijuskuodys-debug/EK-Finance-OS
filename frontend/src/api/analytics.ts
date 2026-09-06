export type PortfolioHistoryPoint = {
  date: string
  value_eur: number
  positions: number
}

export type RiskAllocationItem = {
  value: number
  percentage: number
  base_currency: string
}

export type RiskBrokerItem = RiskAllocationItem & {
  broker: string
}

export type RiskAssetTypeItem = RiskAllocationItem & {
  asset_type: string
}

export type RiskCurrencyItem = RiskAllocationItem & {
  currency: string
}

export type RiskPosition = {
  investment_id: number
  broker: string
  ticker: string
  asset: string
  asset_type: string
  currency: string
  value: number
  percentage: number
  base_currency: string
}

export type RiskLevel =
  | 'Low'
  | 'Moderate'
  | 'High'

export type RiskAssessment = {
  overall_level: RiskLevel

  position_concentration: {
    level: RiskLevel
    percentage: number
  }

  hhi_concentration: {
    level: RiskLevel
    value: number
  }

  broker_concentration: {
    level: RiskLevel
    percentage: number
    broker: string | null
  }

  currency_concentration: {
    level: RiskLevel
    percentage: number
    currency: string | null
  }
}

export type PortfolioRisk = {
  portfolio_value: number
  base_currency: string
  open_positions: number

  risk_assessment: RiskAssessment

  concentration: {
    top_1_percentage: number
    top_3_percentage: number
    top_5_percentage: number
    hhi: number
  }

  largest_position: RiskPosition | null
  largest_broker: RiskBrokerItem | null
  largest_asset_type: RiskAssetTypeItem | null
  largest_currency: RiskCurrencyItem | null

  top_positions: RiskPosition[]
  by_broker: RiskBrokerItem[]
  by_asset_type: RiskAssetTypeItem[]
  by_currency: RiskCurrencyItem[]
}


export type PerformancePosition = {
  investment_id: number
  broker: string
  ticker: string
  asset: string
  asset_type: string
  status: 'OPEN' | 'CLOSED'
  quantity: number
  currency: string
  open_cost_basis: number
  current_value: number
  unrealized_profit: number
  unrealized_return_percent: number
  realized_profit: number
  dividend_net: number
  total_profit: number
  base_currency: string
}

export type PerformanceSummary = {
  open_cost_basis: number
  current_value: number
  unrealized_profit: number
  unrealized_return_percent: number
  realized_profit: number
  dividend_net: number
  total_profit: number
  positions: number
  open_positions: number
  closed_positions: number
  base_currency: string
}

export type PerformanceBrokerItem = {
  broker: string
  open_cost_basis: number
  current_value: number
  unrealized_profit: number
  realized_profit: number
  dividend_net: number
  total_profit: number
  positions: number
  open_positions: number
  base_currency: string
}

export type PerformanceAssetTypeItem = {
  asset_type: string
  open_cost_basis: number
  current_value: number
  unrealized_profit: number
  realized_profit: number
  dividend_net: number
  total_profit: number
  positions: number
  open_positions: number
  base_currency: string
}

export type PortfolioPerformanceBreakdown = {
  summary: PerformanceSummary
  best_position: PerformancePosition | null
  worst_position: PerformancePosition | null
  positions: PerformancePosition[]
  by_broker: PerformanceBrokerItem[]
  by_asset_type: PerformanceAssetTypeItem[]
}


export type HealthComponent = {
  score: number
  max_score: number
}

export type PortfolioHealth = {
  score: number
  max_score: number
  label: string

  components: {
    position_diversification: HealthComponent
    hhi_diversification: HealthComponent
    broker_diversification: HealthComponent
    currency_diversification: HealthComponent
    asset_type_diversification: HealthComponent
  }

  strengths: string[]
  watch_items: string[]

  base_currency: string
  portfolio_value: number
}


export type InsightPriority =
  | 'High'
  | 'Medium'
  | 'Low'
  | 'Info'

export type PortfolioInsight = {
  category: string
  priority: InsightPriority
  title: string
  message: string
}

export type PortfolioInsightsSummary = {
  health_score: number
  health_label: string
  insights_count: number
  high_priority_count: number
  medium_priority_count: number
}

export type PortfolioInsights = {
  summary: PortfolioInsightsSummary
  insights: PortfolioInsight[]
}


const API_BASE_URL = 'http://localhost:8000'


export async function getPortfolioHistory():
Promise<PortfolioHistoryPoint[]> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/portfolio-history`,
  )

  if (!response.ok) {
    throw new Error(
      `Portfolio history request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<
    PortfolioHistoryPoint[]
  >
}


export async function getPortfolioRisk():
Promise<PortfolioRisk> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/risk`,
  )

  if (!response.ok) {
    throw new Error(
      `Portfolio risk request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<
    PortfolioRisk
  >
}


export async function getPerformanceBreakdown():
Promise<PortfolioPerformanceBreakdown> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/performance-breakdown`,
  )

  if (!response.ok) {
    throw new Error(
      `Performance breakdown request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<
    PortfolioPerformanceBreakdown
  >
}


export async function getPortfolioHealth():
Promise<PortfolioHealth> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/health`,
  )

  if (!response.ok) {
    throw new Error(
      `Portfolio health request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<
    PortfolioHealth
  >
}


export async function getPortfolioInsights():
Promise<PortfolioInsights> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/insights`,
  )

  if (!response.ok) {
    throw new Error(
      `Portfolio insights request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<
    PortfolioInsights
  >
}