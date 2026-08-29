import { NavLink } from 'react-router-dom'


function DashboardLayout({ children }) {
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
              isActive ? 'sidebar-link active' : 'sidebar-link'
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/companies"
            className={({ isActive }) =>
              isActive ? 'sidebar-link active' : 'sidebar-link'
            }
          >
            Companies
          </NavLink>

          <NavLink
            to="/registration-orders"
            className={({ isActive }) =>
              isActive ? 'sidebar-link active' : 'sidebar-link'
            }
          >
            Registration Orders
          </NavLink>

          <button type="button">
            Currency Purchases
          </button>

          <button type="button">
            Shipments
          </button>

          <button type="button">
            Invoices
          </button>

          <button type="button">
            Notifications
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