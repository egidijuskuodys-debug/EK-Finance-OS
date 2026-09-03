export type PortfolioHistoryPoint = {
  date: string
  value_eur: number
  positions: number
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