import type { DashboardData } from '../types/dashboard'

const API_BASE_URL = 'http://localhost:8000'

export async function getDashboard(): Promise<DashboardData> {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/`,
  )

  if (!response.ok) {
    throw new Error(
      `Dashboard request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<DashboardData>
}