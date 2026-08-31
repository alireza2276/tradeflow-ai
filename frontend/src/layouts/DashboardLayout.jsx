import {
  NavLink,
  useNavigate,
} from 'react-router-dom'

import {
  logout,
} from '../services/api'


function DashboardLayout({
  children,
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

          <button type="button">
            Shipments
          </button>

          <button type="button">
            Invoices
          </button>

          <button type="button">
            Notifications
          </button>

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
