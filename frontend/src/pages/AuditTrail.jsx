import {
  Fragment,
  useEffect,
  useState,
} from 'react'

import {
  useTranslation,
} from 'react-i18next'

import {
  getAuditEvents,
} from '../services/api'


function AuditTrail() {
  const { t, i18n } = useTranslation()
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedEventId, setExpandedEventId] = useState(null)

  useEffect(() => {
    let isMounted = true

    async function loadAuditEvents() {
      try {
        const data = await getAuditEvents()

        if (isMounted) {
          setEvents(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError.message ||
            t('auditTrail.loadError')
          )
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadAuditEvents()

    return () => {
      isMounted = false
    }
  }, [t])

  function formatDateTime(value) {
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
        second: '2-digit',
      }
    ).format(new Date(value))
  }

  function formatAction(action) {
    const key = `auditTrail.actions.${action}`
    const translated = t(key)

    return translated === key
      ? action
      : translated
  }

  function formatTargetType(targetType) {
    const key = `auditTrail.targets.${targetType}`
    const translated = t(key)

    return translated === key
      ? targetType
      : translated
  }

  if (loading) {
    return (
      <div className="loading-state">
        {t('auditTrail.loading')}
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
    <div className="audit-page">
      <div className="page-header">
        <div>
          <h1>{t('auditTrail.title')}</h1>
          <p>{t('auditTrail.description')}</p>
        </div>
      </div>

      {events.length === 0 ? (
        <div className="empty-state">
          {t('auditTrail.empty')}
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>{t('auditTrail.time')}</th>
                <th>{t('auditTrail.actor')}</th>
                <th>{t('auditTrail.action')}</th>
                <th>{t('auditTrail.target')}</th>
                <th>{t('auditTrail.targetId')}</th>
                <th>{t('auditTrail.reason')}</th>
                <th>{t('auditTrail.details')}</th>
              </tr>
            </thead>

            <tbody>
              {events.map((event) => (
                <Fragment key={event.id}>
                  <tr>
                    <td>{formatDateTime(event.created_at)}</td>
                    <td>{event.actor_username || t('auditTrail.system')}</td>
                    <td>{formatAction(event.action)}</td>
                    <td>{formatTargetType(event.target_type)}</td>
                    <td>{event.target_id || '-'}</td>
                    <td>{event.reason || '-'}</td>
                    <td>
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          setExpandedEventId(
                            expandedEventId === event.id
                              ? null
                              : event.id
                          )
                        }
                      >
                        {expandedEventId === event.id
                          ? t('auditTrail.hideDetails')
                          : t('auditTrail.showDetails')}
                      </button>
                    </td>
                  </tr>

                  {expandedEventId === event.id && (
                    <tr key={`${event.id}-details`}>
                      <td colSpan="7">
                        <div className="audit-details-grid">
                          <div>
                            <strong>{t('auditTrail.before')}</strong>
                            <pre>{JSON.stringify(event.before_state, null, 2)}</pre>
                          </div>

                          <div>
                            <strong>{t('auditTrail.after')}</strong>
                            <pre>{JSON.stringify(event.after_state, null, 2)}</pre>
                          </div>

                          <div>
                            <strong>{t('auditTrail.metadata')}</strong>
                            <pre>{JSON.stringify(event.metadata, null, 2)}</pre>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


export default AuditTrail
