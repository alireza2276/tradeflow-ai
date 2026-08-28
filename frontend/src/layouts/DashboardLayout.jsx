function DashboardLayout({ children }) {
  return (
    <div className="dashboard-layout">

      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>TradeFlowAI</h2>
          <span>Trade Finance</span>
        </div>

        <nav className="sidebar-nav">
          <button type="button">Dashboard</button>
          <button type="button">Companies</button>
          <button type="button">Registration Orders</button>
          <button type="button">Currency Purchases</button>
          <button type="button">Shipments</button>
          <button type="button">Invoices</button>
          <button type="button">Notifications</button>
        </nav>
      </aside>

      <main className="main-content">
        {children}
      </main>

    </div>
  )
}

export default DashboardLayout