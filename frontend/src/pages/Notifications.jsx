import {
  useEffect,
  useState,
} from 'react'

import {
  getNotificationLogs,
} from '../services/api'


function Notifications() {
  const [
    notifications,
    setNotifications,
  ] = useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  useEffect(() => {
    let isMounted = true

    async function fetchNotifications() {
      try {
        const data =
          await getNotificationLogs()

        if (!isMounted) {
          return
        }

        setNotifications(data)
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError.message ||
            'Failed to load notifications.'
          )
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchNotifications()

    return () => {
      isMounted = false
    }
  }, [])

  function formatNotificationType(type) {
    return type
      .replaceAll('_', ' ')
      .toLowerCase()
      .replace(/\b\w/g, (character) =>
        character.toUpperCase()
      )
  }

  function formatSentAt(value) {
    if (!value) {
      return '-'
    }

    return new Intl.DateTimeFormat(
      'en-GB',
      {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      }
    ).format(new Date(value))
  }

  if (loading) {
    return (
      <div className="loading-state">
        Loading notifications...
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        {error}
      </div>
    )
  }

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <div>
          <h1>Notifications</h1>

          <p>
            Review deadline alerts generated
            for currency purchases.
          </p>
        </div>
      </div>

      {notifications.length === 0 ? (
        <div className="empty-state">
          No notifications found.
        </div>
      ) : (
        <div className="notifications-table-wrapper">
          <table className="notifications-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Order</th>
                <th>Purchase</th>
                <th>Purchase Date</th>
                <th>Deadline</th>
                <th>Alert</th>
                <th>Generated At</th>
              </tr>
            </thead>

            <tbody>
              {notifications.map(
                (notification) => (
                  <tr key={notification.id}>
                    <td>
                      <div className="notification-company">
                        <strong>
                          {notification.company_name}
                        </strong>

                        <span>
                          {notification.company_national_id}
                        </span>
                      </div>
                    </td>

                    <td>
                      {notification.order_number}
                    </td>

                    <td>
                      <span className="notification-amount">
                        {notification.purchase_amount}
                      </span>{' '}
                      {notification.currency}
                    </td>

                    <td>
                      {notification.purchase_date_dual}
                    </td>

                    <td>
                      {notification.deadline_dual}
                    </td>

                    <td>
                      <span
                        className={`notification-badge notification-badge-${notification.notification_type.toLowerCase()}`}
                      >
                        {formatNotificationType(
                          notification.notification_type
                        )}
                      </span>
                    </td>

                    <td>
                      {formatSentAt(
                        notification.sent_at
                      )}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Notifications