import type { Transaction } from '../types/transaction'

const API_BASE_URL = 'http://localhost:8000'

export async function getTransactions(): Promise<Transaction[]> {
  const response = await fetch(
    `${API_BASE_URL}/transactions`,
  )

  if (!response.ok) {
    throw new Error(
      `Transactions request failed: ${response.status}`,
    )
  }

  return response.json() as Promise<Transaction[]>
}