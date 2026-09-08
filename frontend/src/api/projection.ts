import type {
  PortfolioProjection,
} from '../types/projection'

const API_BASE_URL = 'http://localhost:8000'


export async function getPortfolioProjection(
  monthlyContribution: number,
  annualReturnPercent: number,
): Promise<PortfolioProjection> {
  const query = new URLSearchParams({
    monthly_contribution: String(monthlyContribution),
    annual_return_percent: String(annualReturnPercent),
  })

  const response = await fetch(
    `${API_BASE_URL}/analytics/projection?${query}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load portfolio projection: ${response.status}`,
    )
  }

  return response.json() as Promise<PortfolioProjection>
}