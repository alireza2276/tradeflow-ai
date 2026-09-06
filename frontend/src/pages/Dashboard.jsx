import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

import AttentionTable from '../components/AttentionTable'
import CurrencyCard from '../components/CurrencyCard'
import StatCard from '../components/StatCard'
import { getDashboardSummary } from '../services/api'


function Dashboard() {
  const { t } = useTranslation()

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
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>
            {t('dashboard.loadingTitle')}
          </h2>

          <p>
            {t('dashboard.loadingDescription')}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="page-state page-state--error">
          <div className="error-icon">
            !
          </div>

          <h2>
            {t('dashboard.loadError')}
          </h2>

          <p>
            {error}
          </p>
        </div>
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
          <h1>
            {t('dashboard.title')}
          </h1>

          <p>
            {t('dashboard.description')}
          </p>
        </div>
      </header>

      <section className="stats-grid">
        <StatCard
          title={t('dashboard.activeOrders')}
          value={dashboardData.active_orders_count}
          subtitle={t(
            'dashboard.activeOrdersSubtitle'
          )}
        />

        <StatCard
          title={t('dashboard.activePurchases')}
          value={dashboardData.active_purchases_count}
          subtitle={t(
            'dashboard.activePurchasesSubtitle'
          )}
        />

        <StatCard
          title={t('dashboard.dueSoon')}
          value={dashboardData.due_soon_count}
          subtitle={t(
            'dashboard.dueSoonSubtitle'
          )}
          tone="warning"
        />

        <StatCard
          title={t('dashboard.overdue')}
          value={dashboardData.overdue_count}
          subtitle={t(
            'dashboard.overdueSubtitle'
          )}
          tone="danger"
        />
      </section>

      <section className="currency-section">
        <div className="section-header">
          <div>
            <h2>
              {t('dashboard.currencyExposure')}
            </h2>

            <p>
              {t(
                'dashboard.currencyExposureDescription'
              )}
            </p>
          </div>
        </div>

        {currencyEntries.length === 0 ? (
          <div className="empty-state">
            {t('dashboard.noCurrencyData')}
          </div>
        ) : (
          <div className="currency-grid">
            {currencyEntries.map(
              ([currency, totals]) => (
                <CurrencyCard
                  key={currency}
                  currency={currency}
                  purchasedAmount={
                    totals.purchased_amount
                  }
                  documentedAmount={
                    totals.documented_amount
                  }
                  remainingAmount={
                    totals.remaining_amount
                  }
                />
              )
            )}
          </div>
        )}
      </section>

      <section className="attention-section">
        <div className="section-header">
          <div>
            <h2>
              {t('dashboard.attentionTitle')}
            </h2>

            <p>
              {t(
                'dashboard.attentionDescription'
              )}
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