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