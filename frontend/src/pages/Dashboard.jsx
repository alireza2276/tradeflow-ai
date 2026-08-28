import { useEffect, useState } from 'react'

import StatCard from '../components/StatCard'
import { getDashboardSummary } from '../services/api'


function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await getDashboardSummary()
        setDashboardData(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [])

  if (loading) {
    return (
      <div className="dashboard-page">
        <p>Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="dashboard-page">

      <header className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Monitor trade finance operations and compliance deadlines.
          </p>
        </div>
      </header>

      <section className="stats-grid">
        <StatCard
          title="Active Orders"
          value={dashboardData.active_orders_count}
          subtitle="Registration orders currently active"
        />

        <StatCard
          title="Active Purchases"
          value={dashboardData.active_purchases_count}
          subtitle="Currency purchases under monitoring"
        />

        <StatCard
          title="Due Soon"
          value={dashboardData.due_soon_count}
          subtitle="Deadlines within the next 30 days"
        />

        <StatCard
          title="Overdue"
          value={dashboardData.overdue_count}
          subtitle="Cases requiring immediate attention"
        />
      </section>

    </div>
  )
}

export default Dashboard