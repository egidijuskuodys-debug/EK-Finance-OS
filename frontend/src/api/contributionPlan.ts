import type {
  ContributionPlan,
} from '../types/contributionPlan'

const API_BASE_URL = 'http://localhost:8000'


export async function getContributionPlan(
  amount: number,
): Promise<ContributionPlan> {
  const query = new URLSearchParams({
    amount: String(amount),
  })

  const response = await fetch(
    `${API_BASE_URL}/analytics/contribution-plan?${query}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load contribution plan: ${response.status}`,
    )
  }

  return response.json() as Promise<ContributionPlan>
}
