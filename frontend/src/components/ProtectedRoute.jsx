import {
  Navigate,
  Outlet,
} from 'react-router-dom'

import {
  useTranslation,
} from 'react-i18next'


function ProtectedRoute({
  isAuthenticated,
  isLoading,
}) {
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="auth-loading">
        {t('auth.checkingSession')}
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    )
  }

  return <Outlet />
}


export default ProtectedRoute