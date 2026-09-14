import {
  NavLink,
  useNavigate,
} from 'react-router-dom'

import {
  useTranslation,
} from 'react-i18next'

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
  const { t, i18n } = useTranslation()

  const currentLanguage =
    i18n.resolvedLanguage || i18n.language

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
        t('common.logoutFailed')
      )
    }
  }

  async function handleLanguageChange(language) {
    await i18n.changeLanguage(language)

    document.documentElement.lang = language
    document.documentElement.dir =
      language === 'fa'
        ? 'rtl'
        : 'ltr'
  }

  const displayName =
    user?.full_name?.trim() ||
    [user?.first_name, user?.last_name]
      .filter(Boolean)
      .join(' ')
      .trim() ||
    user?.username ||
    t('userIdentity.unknownUser')

  const roleNames = Array.isArray(user?.roles)
    ? user.roles
    : []

  const displayRoles =
    roleNames.length > 0
      ? roleNames
          .map((role) =>
            t(`userIdentity.roles.${role}`, {
              defaultValue: role,
            })
          )
          .join(' • ')
      : t('userIdentity.noRole')

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>
            {t('common.appName')}
          </h2>

          <span>
            {t('common.tradeFinance')}
          </span>
        </div>

        <section
          className="signed-in-user"
          aria-label={t('userIdentity.signedInAs')}
        >
          <div
            className="signed-in-user-avatar"
            aria-hidden="true"
          >
            {displayName.charAt(0).toLocaleUpperCase()}
          </div>

          <div className="signed-in-user-details">
            <span className="signed-in-user-label">
              {t('userIdentity.signedInAs')}
            </span>

            <strong
              className="signed-in-user-name"
              title={displayName}
            >
              {displayName}
            </strong>

            <span
              className="signed-in-user-role"
              title={displayRoles}
            >
              {displayRoles}
            </span>
          </div>
        </section>

        <div className="language-switcher">
          <button
            type="button"
            className={
              currentLanguage === 'fa'
                ? 'language-button active'
                : 'language-button'
            }
            onClick={() =>
              handleLanguageChange('fa')
            }
          >
            {t('common.persian')}
          </button>

          <button
            type="button"
            className={
              currentLanguage === 'en'
                ? 'language-button active'
                : 'language-button'
            }
            onClick={() =>
              handleLanguageChange('en')
            }
          >
            {t('common.english')}
          </button>
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
              {t('navigation.dashboard')}
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
              {t('navigation.companies')}
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
              {t(
                'navigation.registrationOrders'
              )}
            </NavLink>
          )}

          {hasPermission(
            user,
            'trade_orders.view_paymentinstrument'
          ) && (
            <NavLink
              to="/payment-instruments"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              {t(
                'navigation.paymentInstruments'
              )}
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
              {t(
                'navigation.currencyPurchases'
              )}
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
              {t(
                'navigation.shipmentParts'
              )}
            </NavLink>
          )}

          {hasPermission(
            user,
            'documents.view_invoice'
          ) && (
            <NavLink
              to="/invoices"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              {t('navigation.invoices')}
            </NavLink>
          )}

          {hasPermission(
            user,
            'notifications.view_notificationlog'
          ) && (
            <NavLink
              to="/notifications"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              {t(
                'navigation.notifications'
              )}
            </NavLink>
          )}

          {hasPermission(
            user,
            'workflows.review_approvalrequest'
          ) && (
            <NavLink
              to="/approvals"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              {t('navigation.approvals')}
            </NavLink>
          )}

          {hasPermission(
            user,
            'audit.view_sensitive_audit'
          ) && (
            <NavLink
              to="/audit-trail"
              className={({ isActive }) =>
                isActive
                  ? 'sidebar-link active'
                  : 'sidebar-link'
              }
            >
              {t('navigation.auditTrail')}
            </NavLink>
          )}

          <button
            type="button"
            className="sidebar-link logout-button"
            onClick={handleLogout}
          >
            {t('common.logout')}
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
