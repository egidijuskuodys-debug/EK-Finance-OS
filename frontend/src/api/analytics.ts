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

export type PortfolioRisk = {
  portfolio_value: number
  base_currency: string
  open_positions: number
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