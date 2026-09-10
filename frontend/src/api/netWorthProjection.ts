import type {
  NetWorthProjection,
} from '../types/netWorthProjection'


const API_BASE_URL = (
  'http://localhost:8000'
)


export async function getNetWorthProjection(
  monthlyContribution: number,
  annualReturnPercent: number,
  annualPropertyGrowth: number,
): Promise<NetWorthProjection> {
  const query = new URLSearchParams({
    monthly_contribution: String(
      monthlyContribution,
    ),
    annual_return_percent: String(
      annualReturnPercent,
    ),
    annual_property_growth: String(
      annualPropertyGrowth,
    ),
  })

  const response = await fetch(
    (
      `${API_BASE_URL}`
      + '/analytics/net-worth-projection?'
      + query.toString()
    ),
  )

  if (!response.ok) {
    throw new Error(
      (
        'Failed to load net worth '
        + `projection: ${response.status}`
      ),
    )
  }

  const data = await response.json()

  return data as NetWorthProjection
}