import type {
  PortfolioTarget,
  PortfolioTargetInput,
  PortfolioTargetUpdate,
} from '../types/portfolioTarget'

const API_BASE_URL = 'http://localhost:8000'


async function parseError(
  response: Response,
): Promise<string> {
  try {
    const data = await response.json() as {
      detail?: string
    }

    return data.detail
      ?? `Request failed: ${response.status}`
  } catch {
    return `Request failed: ${response.status}`
  }
}


export async function getPortfolioTargets():
Promise<PortfolioTarget[]> {
  const response = await fetch(
    `${API_BASE_URL}/portfolio-targets/`,
  )

  if (!response.ok) {
    throw new Error(
      await parseError(response),
    )
  }

  return response.json() as Promise<PortfolioTarget[]>
}


export async function createPortfolioTarget(
  target: PortfolioTargetInput,
): Promise<PortfolioTarget> {
  const response = await fetch(
    `${API_BASE_URL}/portfolio-targets/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(target),
    },
  )

  if (!response.ok) {
    throw new Error(
      await parseError(response),
    )
  }

  return response.json() as Promise<PortfolioTarget>
}


export async function updatePortfolioTarget(
  targetId: number,
  target: PortfolioTargetUpdate,
): Promise<PortfolioTarget> {
  const response = await fetch(
    `${API_BASE_URL}/portfolio-targets/${targetId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(target),
    },
  )

  if (!response.ok) {
    throw new Error(
      await parseError(response),
    )
  }

  return response.json() as Promise<PortfolioTarget>
}


export async function deletePortfolioTarget(
  targetId: number,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/portfolio-targets/${targetId}`,
    {
      method: 'DELETE',
    },
  )

  if (!response.ok) {
    throw new Error(
      await parseError(response),
    )
  }
}
