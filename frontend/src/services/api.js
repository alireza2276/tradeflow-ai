const API_BASE_URL = 'http://localhost:8000/api'

function getCookie(name) {
  const cookies = document.cookie
    ? document.cookie.split(';')
    : []

  for (const cookie of cookies) {
    const [cookieName, ...cookieValueParts] = cookie
      .trim()
      .split('=')

    if (cookieName === name) {
      return decodeURIComponent(
        cookieValueParts.join('=')
      )
    }
  }

  return null
}


async function parseErrorResponse(
  response,
  fallbackMessage
) {
  try {
    const errorData = await response.json()

    const firstError = Object.values(errorData)
      .flat()
      .find(Boolean)

    return (
      errorData.detail ||
      firstError ||
      fallbackMessage
    )
  } catch {
    return fallbackMessage
  }
}


async function apiFetch(
  path,
  options = {}
) {
  const method = (
    options.method || 'GET'
  ).toUpperCase()

  const headers = {
    ...(options.headers || {}),
  }

  const unsafeMethods = [
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
  ]

  if (unsafeMethods.includes(method)) {
    const csrfToken = getCookie('csrftoken')

    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }

  return fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
      credentials: 'include',
    }
  )
}


export async function ensureCsrfCookie() {
  const response = await apiFetch(
    '/auth/csrf/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to initialize CSRF protection.'
    )
  }

  return response.json()
}


export async function login(
  username,
  password
) {
  await ensureCsrfCookie()

  const csrfToken = getCookie('csrftoken')

  if (!csrfToken) {
    throw new Error(
      'CSRF token is unavailable.'
    )
  }

  const response = await fetch(
    `${API_BASE_URL}/auth/login/`,
    {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        username,
        password,
      }),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Login failed.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function getCurrentUser() {
  const response = await apiFetch(
    '/auth/me/'
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Authentication required.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function logout() {
  /*
   * Django rotates the CSRF token after login,
   * so always read the current cookie here.
   */
  const csrfToken = getCookie('csrftoken')

  if (!csrfToken) {
    throw new Error(
      'CSRF token is unavailable.'
    )
  }

  const response = await fetch(
    `${API_BASE_URL}/auth/logout/`,
    {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRFToken': csrfToken,
      },
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Logout failed.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function getDashboardSummary() {
  const response = await apiFetch(
    '/trade/dashboard/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load dashboard data.'
    )
  }

  return response.json()
}


export async function getCompanies() {
  const response = await apiFetch(
    '/companies/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load companies.'
    )
  }

  return response.json()
}


export async function createCompany(companyData) {
  const response = await apiFetch(
    '/companies/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(companyData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to create company.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function updateCompany(
  companyId,
  companyData
) {
  const response = await apiFetch(
    `/companies/${companyId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(companyData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to update company.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function deleteCompany(companyId) {
  const response = await apiFetch(
    `/companies/${companyId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to delete company.'
    )

    throw new Error(errorMessage)
  }
}


export async function getRegistrationOrders() {
  const response = await apiFetch(
    '/trade/registration-orders/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load registration orders.'
    )
  }

  return response.json()
}


export async function createRegistrationOrder(
  orderData
) {
  const response = await apiFetch(
    '/trade/registration-orders/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to create registration order.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function updateRegistrationOrder(
  orderId,
  orderData
) {
  const response = await apiFetch(
    `/trade/registration-orders/${orderId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to update registration order.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function deleteRegistrationOrder(
  orderId
) {
  const response = await apiFetch(
    `/trade/registration-orders/${orderId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to delete registration order.'
    )

    throw new Error(errorMessage)
  }
}

export async function getCurrencyPurchases() {
  const response = await apiFetch(
    '/trade/currency-purchases/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load currency purchases.'
    )
  }

  return response.json()
}


export async function createCurrencyPurchase(
  purchaseData
) {
  const response = await apiFetch(
    '/trade/currency-purchases/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(purchaseData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to create currency purchase.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function updateCurrencyPurchase(
  purchaseId,
  purchaseData
) {
  const response = await apiFetch(
    `/trade/currency-purchases/${purchaseId}/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(purchaseData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to update currency purchase.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}

export async function getShipmentParts() {
  const response = await apiFetch(
    '/trade/shipment-parts/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load shipment parts.'
    )
  }

  return response.json()
}


export async function createShipmentPart(
  shipmentData
) {
  const response = await apiFetch(
    '/trade/shipment-parts/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(shipmentData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to create shipment part.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function updateShipmentPart(
  shipmentId,
  shipmentData
) {
  const response = await apiFetch(
    `/trade/shipment-parts/${shipmentId}/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(shipmentData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to update shipment part.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}

export async function getInvoices() {
  const response = await apiFetch(
    '/documents/invoices/'
  )

  if (!response.ok) {
    throw new Error(
      'Failed to load invoices.'
    )
  }

  return response.json()
}


export async function createInvoice(
  invoiceData
) {
  const response = await apiFetch(
    '/documents/invoices/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(invoiceData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to create invoice.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}


export async function updateInvoice(
  invoiceId,
  invoiceData
) {
  const response = await apiFetch(
    `/documents/invoices/${invoiceId}/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(invoiceData),
    }
  )

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(
      response,
      'Failed to update invoice.'
    )

    throw new Error(errorMessage)
  }

  return response.json()
}
