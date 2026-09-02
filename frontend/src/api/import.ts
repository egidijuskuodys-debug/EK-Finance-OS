import type {
  ImportResult,
  ImportValidationResult,
} from '../types/import'

const API_BASE_URL = 'http://localhost:8000'


function buildFormData(
  broker: string,
  file: File,
) {
  const formData = new FormData()

  formData.append(
    'broker',
    broker,
  )

  formData.append(
    'file',
    file,
  )

  return formData
}


export async function validateImportFile(
  broker: string,
  file: File,
): Promise<ImportValidationResult> {
  const response = await fetch(
    `${API_BASE_URL}/import/upload-validate`,
    {
      method: 'POST',
      body: buildFormData(
        broker,
        file,
      ),
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.detail
      ?? `Import validation failed: ${response.status}`,
    )
  }

  return data as ImportValidationResult
}


export async function executeImportFile(
  broker: string,
  file: File,
): Promise<ImportResult> {
  const response = await fetch(
    `${API_BASE_URL}/import/upload-import`,
    {
      method: 'POST',
      body: buildFormData(
        broker,
        file,
      ),
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.detail
      ?? `Import failed: ${response.status}`,
    )
  }

  return data as ImportResult
}