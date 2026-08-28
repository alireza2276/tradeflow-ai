import { useEffect, useState } from 'react'

import AttentionTable from '../components/AttentionTable'
import CurrencyCard from '../components/CurrencyCard'
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

  const currencyEntries = Object.entries(
    dashboardData.currency_totals || {}
  )

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
          tone="warning"
        />

        <StatCard
          title="Overdue"
          value={dashboardData.overdue_count}
          subtitle="Cases requiring immediate attention"
          tone="danger"
        />

      </section>

      <section className="currency-section">

        <div className="section-header">
          <div>
            <h2>Currency Exposure</h2>
            <p>
              Purchased, documented, and remaining amounts by currency.
            </p>
          </div>
        </div>

        {currencyEntries.length === 0 ? (
          <div className="empty-state">
            No currency purchase data available.
          </div>
        ) : (
          <div className="currency-grid">
            {currencyEntries.map(([currency, totals]) => (
              <CurrencyCard
                key={currency}
                currency={currency}
                purchasedAmount={totals.purchased_amount}
                documentedAmount={totals.documented_amount}
                remainingAmount={totals.remaining_amount}
              />
            ))}
          </div>
        )}

      </section>

      <section className="attention-section">

        <div className="section-header">
          <div>
            <h2>Cases Requiring Attention</h2>
            <p>
              Purchases that are overdue or approaching their compliance deadline.
            </p>
          </div>
        </div>

        <AttentionTable
          cases={dashboardData.attention_cases}
        />

      </section>

    </div>
  )
}

export default Dashboard