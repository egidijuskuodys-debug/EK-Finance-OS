import type {
  PortfolioRebalancing,
} from '../types/rebalancing'

const API_BASE_URL = 'http://localhost:8000'


export async function getPortfolioRebalancing():
Promise<PortfolioRebalancing> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/rebalancing`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load rebalancing: ${response.status}`,
    )
  }

  return response.json() as Promise<PortfolioRebalancing>
}
