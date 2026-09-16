import type {
  MortgageVsInvestRequest,
  MortgageVsInvestResponse,
} from '../types/mortgageVsInvest'


const API_BASE_URL = (
  window.location.origin.replace(
    ':5173',
    ':8000',
  )
)


export async function compareMortgageVsInvest(
  propertyId: number,
  request: MortgageVsInvestRequest,
): Promise<MortgageVsInvestResponse> {
  const response = await fetch(
    (
      `${API_BASE_URL}`
      + `/real-estate/${propertyId}`
      + '/mortgage-vs-invest'
    ),
    {
      method: 'POST',
      headers: {
        'Content-Type': (
          'application/json'
        ),
      },
      body: JSON.stringify(
        request,
      ),
    },
  )

  if (!response.ok) {
    let message = (
      'Failed to calculate '
      + 'mortgage comparison.'
    )

    try {
      const errorData = await response.json()

      if (
        typeof errorData.detail
        === 'string'
      ) {
        message = errorData.detail
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message)
  }

  return response.json()
}