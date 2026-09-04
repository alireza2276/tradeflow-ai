import {
  NavLink,
  useNavigate,
} from 'react-router-dom'

import {
  logout,
} from '../services/api'

import {
  hasPermission,
} from '../utils/permissions'


function DashboardLayout({
  children,
  user,
  onLogout,
}) {
  const navigate = useNavigate()

  async function handleLogout() {
    try {
      await logout()

      onLogout()

      navigate(
        '/login',
        {
          replace: true,
        }
      )
    } catch (logoutError) {
      window.alert(
        logoutError.message ||
        'Logout failed.'
      )
    }
  }

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>TradeFlowAI</h2>
          <span>Trade Finance</span>
        </div>

        <nav className="sidebar-nav">
          {hasPermission(
            user,
            'trade_orders.view_registrationorder'
          ) && hasPermission(
            user,
            'trade_orders.view_currencypurchase'
          ) && (
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              Dashboard
            </NavLink>
          )}

          {hasPermission(
            user,
            'companies.view_company'
          ) && (
            <NavLink
              to="/companies"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              Companies
            </NavLink>
          )}

          {hasPermission(
            user,
            'trade_orders.view_registrationorder'
          ) && (
            <NavLink
              to="/registration-orders"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              Registration Orders
            </NavLink>
          )}

          {hasPermission(
            user,
            'trade_orders.view_currencypurchase'
          ) && (
            <NavLink
              to="/currency-purchases"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              Currency Purchases
            </NavLink>
          )}

          {hasPermission(
            user,
            'trade_orders.view_shipmentpart'
          ) && (
            <NavLink
              to="/shipment-parts"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              Shipment Parts
            </NavLink>
          )}

          {hasPermission(
            user,
            'documents.view_invoice'
          ) && (
            <button type="button">
              Invoices
            </button>
          )}

          {hasPermission(
            user,
            'notifications.view_notificationlog'
          ) && (
            <button type="button">
              Notifications
            </button>
          )}

          <button
            type="button"
            className="sidebar-link logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </nav>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  )
}


export default DashboardLayout