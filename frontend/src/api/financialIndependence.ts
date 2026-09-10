import type {
  FinancialIndependence,
} from '../types/financialIndependence'


const API_BASE_URL = (
  'http://localhost:8000'
)


export async function getFinancialIndependence(
  monthlyIncomeTarget: number,
  withdrawalRatePercent: number,
  monthlyContribution: number,
  annualReturnPercent: number,
  annualPropertyGrowth: number,
  currentAge: number,
): Promise<FinancialIndependence> {
  const query = new URLSearchParams({
    monthly_income_target: String(
      monthlyIncomeTarget,
    ),
    withdrawal_rate_percent: String(
      withdrawalRatePercent,
    ),
    monthly_contribution: String(
      monthlyContribution,
    ),
    annual_return_percent: String(
      annualReturnPercent,
    ),
    annual_property_growth: String(
      annualPropertyGrowth,
    ),
    current_age: String(
      currentAge,
    ),
  })

  const response = await fetch(
    (
      `${API_BASE_URL}`
      + '/analytics/financial-independence?'
      + query.toString()
    ),
  )

  if (!response.ok) {
    throw new Error(
      (
        'Failed to load financial '
        + `independence: ${response.status}`
      ),
    )
  }

  const data = await response.json()

  return data as FinancialIndependence
}