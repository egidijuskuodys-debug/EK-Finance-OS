import type { Investment } from '../types/investment'

const API_BASE_URL = window.location.origin.replace(':5173', ':8000')

export async function getInvestments(): Promise<Investment[]> {
  const response = await fetch(
    `${API_BASE_URL}/investments`,
  )

  if (!response.ok) {
    throw new Error(
      `Investments request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<Investment[]>
}