import {
  Link,
} from 'react-router-dom'

import {
  hasPermission,
} from '../utils/permissions'


function Forbidden({
  user,
}) {
  const canViewDashboard =
    hasPermission(
      user,
      'trade_orders.view_registrationorder'
    ) &&
    hasPermission(
      user,
      'trade_orders.view_currencypurchase'
    )

  return (
    <div className="forbidden-page">
      <div className="forbidden-card">
        <span className="forbidden-code">
          403
        </span>

        <h1>Access Denied</h1>

        <p>
          You do not have permission to access this page.
        </p>

        {canViewDashboard ? (
          <Link
            to="/"
            className="forbidden-link"
          >
            Back to Dashboard
          </Link>
        ) : (
          <p>
            Please contact your administrator if you need additional access.
          </p>
        )}
      </div>
    </div>
  )
}


export default Forbidden