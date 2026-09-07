export interface BrokerAllocation {
  broker: string
  value: number
  percentage: number
  currency: string
}

export interface AssetTypeAllocation {
  asset_type: string
  value: number
  percentage: number
  currency: string
}

export interface PortfolioAllocation {
  portfolio_value: number
  base_currency: string
  by_broker: BrokerAllocation[]
  by_asset_type: AssetTypeAllocation[]
}


const API_BASE_URL = 'http://localhost:8000'


export async function getPortfolioAllocation():
Promise<PortfolioAllocation> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/allocation`,
  )

  if (!response.ok) {
    throw new Error(
      `Portfolio allocation request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<PortfolioAllocation>
}
