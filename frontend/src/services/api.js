const API_BASE_URL = 'http://127.0.0.1:8000/api'


export async function getDashboardSummary() {
  const response = await fetch(
    `${API_BASE_URL}/trade/dashboard/`
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load dashboard data.'
    )
  }

  return response.json()
}


export async function getCompanies() {
  const response = await fetch(
    `${API_BASE_URL}/companies/`
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load companies.'
    )
  }

  return response.json()
}


export async function createCompany(companyData) {
  const response = await fetch(
    `${API_BASE_URL}/companies/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(companyData),
    }
  )

  if (!response.ok) {
    const errorData = await response.json()

    const firstError = Object.values(errorData)
      .flat()
      .find(Boolean)

    throw new Error(
      errorData.detail ||
      firstError ||
      'Failed to create company.'
    )
  }

  return response.json()
}

export async function updateCompany(companyId, companyData) {
  const response = await fetch(
    `${API_BASE_URL}/companies/${companyId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(companyData),
    }
  )

  if (!response.ok) {
    const errorData = await response.json()

    const firstError = Object.values(errorData)
      .flat()
      .find(Boolean)

    throw new Error(
      errorData.detail ||
      firstError ||
      'Failed to update company.'
    )
  }

  return response.json()
}


export async function deleteCompany(companyId) {
  const response = await fetch(
    `${API_BASE_URL}/companies/${companyId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    throw new Error(
      'Failed to delete company.'
    )
  }
}