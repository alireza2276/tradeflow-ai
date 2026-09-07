import {
  useTranslation,
} from 'react-i18next'


function StatCard({
  title,
  value,
  subtitle,
  tone = 'default',
}) {
  const { t } = useTranslation()

  return (
    <div className={`stat-card stat-card--${tone}`}>
      <div className="stat-card-header">
        <span className="stat-card-title">
          {title}
        </span>

        {tone !== 'default' && (
          <span
            className={
              `stat-status stat-status--${tone}`
            }
          >
            {
              tone === 'warning'
                ? t('statCard.attention')
                : t('statCard.critical')
            }
          </span>
        )}
      </div>

      <div className="stat-card-value">
        {value}
      </div>

      {subtitle && (
        <div className="stat-card-subtitle">
          {subtitle}
        </div>
      )}
    </div>
  )
}


export default StatCard