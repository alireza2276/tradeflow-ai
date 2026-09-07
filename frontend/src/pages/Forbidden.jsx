import {
  Link,
} from 'react-router-dom'

import {
  useTranslation,
} from 'react-i18next'

import {
  hasPermission,
} from '../utils/permissions'


function Forbidden({
  user,
}) {
  const { t } = useTranslation()

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

        <h1>
          {t('forbidden.title')}
        </h1>

        <p>
          {t('forbidden.message')}
        </p>

        {canViewDashboard ? (
          <Link
            to="/"
            className="forbidden-link"
          >
            {t('forbidden.backToDashboard')}
          </Link>
        ) : (
          <p>
            {t('forbidden.contactAdministrator')}
          </p>
        )}
      </div>
    </div>
  )
}


export default Forbidden