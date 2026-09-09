import type {
  RealEstateCreate,
  RealEstateProperty,
  RealEstateSummary,
  RealEstateUpdate,
} from '../types/realEstate'


const API_BASE_URL = (
  'http://localhost:8000'
)


async function getErrorMessage(
  response: Response,
): Promise<string> {
  try {
    const data = await response.json() as {
      detail?: string
    }

    return (
      data.detail
      ?? `Request failed: ${response.status}`
    )
  } catch {
    return (
      `Request failed: ${response.status}`
    )
  }
}


export async function getRealEstateProperties():
Promise<RealEstateProperty[]> {
  const response = await fetch(
    `${API_BASE_URL}/real-estate/`,
  )

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
      ),
    )
  }

  const data = await response.json()

  return data as RealEstateProperty[]
}


export async function getRealEstateSummary():
Promise<RealEstateSummary> {
  const response = await fetch(
    `${API_BASE_URL}/real-estate/summary`,
  )

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
      ),
    )
  }

  const data = await response.json()

  return data as RealEstateSummary
}


export async function createRealEstateProperty(
  propertyData: RealEstateCreate,
): Promise<RealEstateProperty> {
  const response = await fetch(
    `${API_BASE_URL}/real-estate/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': (
          'application/json'
        ),
      },
      body: JSON.stringify(
        propertyData,
      ),
    },
  )

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
      ),
    )
  }

  const data = await response.json()

  return data as RealEstateProperty
}


export async function updateRealEstateProperty(
  propertyId: number,
  propertyData: RealEstateUpdate,
): Promise<RealEstateProperty> {
  const response = await fetch(
    (
      `${API_BASE_URL}/real-estate/`
      + propertyId
    ),
    {
      method: 'PUT',
      headers: {
        'Content-Type': (
          'application/json'
        ),
      },
      body: JSON.stringify(
        propertyData,
      ),
    },
  )

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
      ),
    )
  }

  const data = await response.json()

  return data as RealEstateProperty
}


export async function deleteRealEstateProperty(
  propertyId: number,
): Promise<void> {
  const response = await fetch(
    (
      `${API_BASE_URL}/real-estate/`
      + propertyId
    ),
    {
      method: 'DELETE',
    },
  )

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
      ),
    )
  }
}