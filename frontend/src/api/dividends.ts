import type { Dividend } from '../types/dividend'

const API_BASE_URL = window.location.origin.replace(':5173', ':8000')

export async function getDividends(): Promise<Dividend[]> {
  const response = await fetch(
    `${API_BASE_URL}/dividends`,
  )

  if (!response.ok) {
    throw new Error(
      `Dividends request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<Dividend[]>
}