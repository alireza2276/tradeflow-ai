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
    let errorMessage = 'Failed to delete company.'

    try {
      const errorData = await response.json()

      if (errorData.detail) {
        errorMessage = errorData.detail
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(errorMessage)
  }
}

export async function getRegistrationOrders() {
  const response = await fetch(
    `${API_BASE_URL}/trade/registration-orders/`
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load registration orders.'
    )
  }

  return response.json()
}

export async function createRegistrationOrder(orderData) {
  const response = await fetch(
    `${API_BASE_URL}/trade/registration-orders/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
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
      'Failed to create registration order.'
    )
  }

  return response.json()
}

export async function updateRegistrationOrder(orderId, orderData) {
  const response = await fetch(
    `${API_BASE_URL}/trade/registration-orders/${orderId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
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
      'Failed to update registration order.'
    )
  }

  return response.json()
}

export async function deleteRegistrationOrder(orderId) {
  const response = await fetch(
    `${API_BASE_URL}/trade/registration-orders/${orderId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    let errorMessage =
      'Failed to delete registration order.'

    try {
      const errorData = await response.json()

      errorMessage =
        errorData.detail ||
        errorMessage
    } catch {
      // Keep the default message
    }

    throw new Error(errorMessage)
  }
}