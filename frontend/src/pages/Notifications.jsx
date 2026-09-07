import {
  useEffect,
  useState,
} from 'react'

import {
  useTranslation,
} from 'react-i18next'

import {
  getNotificationLogs,
} from '../services/api'


function Notifications() {
  const {
    t,
    i18n,
  } = useTranslation()

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
            t('notifications.loadError')
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
  }, [t])


  function formatNotificationType(type) {
    if (!type) {
      return '-'
    }

    const translationKey =
      `notifications.types.${type}`

    const translated =
      t(translationKey)

    if (translated !== translationKey) {
      return translated
    }

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

    const locale =
      i18n.resolvedLanguage === 'fa'
        ? 'fa-IR'
        : 'en-GB'

    return new Intl.DateTimeFormat(
      locale,
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
        {t('notifications.loading')}
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
          <h1>
            {t('notifications.title')}
          </h1>

          <p>
            {t('notifications.description')}
          </p>
        </div>
      </div>


      {notifications.length === 0 ? (
        <div className="empty-state">
          {t('notifications.empty')}
        </div>
      ) : (
        <div className="notifications-table-wrapper">
          <table className="notifications-table">
            <thead>
              <tr>
                <th>
                  {t('notifications.company')}
                </th>

                <th>
                  {t('notifications.order')}
                </th>

                <th>
                  {t('notifications.purchase')}
                </th>

                <th>
                  {t('notifications.purchaseDate')}
                </th>

                <th>
                  {t('notifications.deadline')}
                </th>

                <th>
                  {t('notifications.alert')}
                </th>

                <th>
                  {t('notifications.generatedAt')}
                </th>
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
                          {
                            notification.company_national_id
                          }
                        </span>
                      </div>
                    </td>

                    <td>
                      {notification.order_number}
                    </td>

                    <td>
                      <span className="notification-amount">
                        {notification.purchase_amount}
                      </span>
                      {' '}
                      {notification.currency}
                    </td>

                    <td>
                      {
                        notification.purchase_date_dual ||
                        '-'
                      }
                    </td>

                    <td>
                      {
                        notification.deadline_dual ||
                        '-'
                      }
                    </td>

                    <td>
                      <span
                        className={
                          `notification-badge ` +
                          `notification-badge-${
                            notification.notification_type
                              ?.toLowerCase() || 'unknown'
                          }`
                        }
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