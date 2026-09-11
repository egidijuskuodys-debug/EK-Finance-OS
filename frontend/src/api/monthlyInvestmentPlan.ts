import type {
  MonthlyInvestmentPlan,
} from '../types/monthlyInvestmentPlan'


const API_BASE_URL = (
  'http://localhost:8000'
)


export async function getMonthlyInvestmentPlan(
  monthlyAmount: number,
): Promise<MonthlyInvestmentPlan> {
  const query = new URLSearchParams({
    monthly_amount: String(
      monthlyAmount,
    ),
  })

  const response = await fetch(
    `${API_BASE_URL}/analytics/monthly-investment-plan?${query}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load monthly investment plan: ${response.status}`,
    )
  }

  return response.json() as Promise<
    MonthlyInvestmentPlan
  >
}