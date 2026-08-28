function StatCard({
  title,
  value,
  subtitle,
  tone = 'default',
}) {
  return (
    <div className={`stat-card stat-card--${tone}`}>
      <div className="stat-card-header">
        <span className="stat-card-title">
          {title}
        </span>

        {tone !== 'default' && (
          <span className={`stat-status stat-status--${tone}`}>
            {tone === 'warning' ? 'Attention' : 'Critical'}
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