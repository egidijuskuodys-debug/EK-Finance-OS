import type {
  FinancialPlanRequest,
  FinancialPlanResponse,
} from "../types/financialPlan"


const API_BASE_URL =
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000"


export async function getFinancialPlan(
  request: FinancialPlanRequest,
): Promise<FinancialPlanResponse> {
  const response = await fetch(
    `${API_BASE_URL}/financial-plan/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  )

  if (!response.ok) {
    const errorText = await response.text()

    throw new Error(
      errorText ||
        "Failed to calculate financial plan.",
    )
  }

  return response.json()
}