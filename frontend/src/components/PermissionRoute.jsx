import {
  Navigate,
  Outlet,
} from 'react-router-dom'

import {
  hasPermission,
} from '../utils/permissions'


function PermissionRoute({
  user,
  permission,
  permissions = [],
}) {
  const requiredPermissions = permission
    ? [permission]
    : permissions

  const hasAccess = requiredPermissions.every(
    (requiredPermission) =>
      hasPermission(
        user,
        requiredPermission
      )
  )

    if (!hasAccess) {
      return (
        <Navigate
          to="/forbidden"
          replace
        />
      )
    }

  return <Outlet />
}


export default PermissionRoute