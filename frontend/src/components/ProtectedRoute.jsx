import {
  Navigate,
  Outlet,
} from 'react-router-dom'


function ProtectedRoute({
  isAuthenticated,
  isLoading,
}) {
  if (isLoading) {
    return (
      <div className="auth-loading">
        Checking your session...
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
