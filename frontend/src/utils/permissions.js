export function hasPermission(user, permission) {
  if (!user) {
    return false
  }

  if (!Array.isArray(user.permissions)) {
    return false
  }

  return user.permissions.includes(permission)
}


export function hasAnyPermission(user, permissions) {
  if (!user) {
    return false
  }

  if (!Array.isArray(user.permissions)) {
    return false
  }

  return permissions.some((permission) =>
    user.permissions.includes(permission)
  )
}


export function hasRole(user, role) {
  if (!user) {
    return false
  }

  if (!Array.isArray(user.roles)) {
    return false
  }

  return user.roles.includes(role)
}