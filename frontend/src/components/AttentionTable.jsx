import { useTranslation } from 'react-i18next'


function AttentionTable({ cases }) {
  const { t } = useTranslation()

  if (!cases || cases.length === 0) {
    return (
      <div className="empty-state">
        {t('attentionTable.empty')}
      </div>
    )
  }

  const formatAmount = (value) => {
    return Number(value).toLocaleString('en-US')
  }

  function getDeadlineText(item) {
    if (item.days_remaining < 0) {
      return t(
        'attentionTable.daysOverdue',
        {
          count: Math.abs(
            item.days_remaining
          ),
        }
      )
    }

    if (item.days_remaining === 0) {
      return t(
        'attentionTable.dueToday'
      )
    }

    return t(
      'attentionTable.daysLeft',
      {
        count: item.days_remaining,
      }
    )
  }

  return (
    <div className="attention-table-wrapper">
      <table className="attention-table">
        <thead>
          <tr>
            <th>
              {t('attentionTable.company')}
            </th>

            <th>
              {t('attentionTable.order')}
            </th>

            <th>
              {t('attentionTable.currency')}
            </th>

            <th>
              {t('attentionTable.remaining')}
            </th>

            <th>
              {t('attentionTable.deadline')}
            </th>

            <th>
              {t('attentionTable.status')}
            </th>
          </tr>
        </thead>

        <tbody>
          {cases.map((item) => (
            <tr key={item.purchase_id}>
              <td>
                {item.company_name}
              </td>

              <td>
                {item.order_number}
              </td>

              <td>
                <span className="table-currency">
                  {item.currency}
                </span>
              </td>

              <td>
                {formatAmount(
                  item.remaining_amount
                )}
              </td>

              <td>
                <div className="deadline-cell">
                  <strong>
                    {item.deadline_dual}
                  </strong>

                  <span
                    className={
                      item.status === 'OVERDUE'
                        ? 'deadline-text deadline-text--danger'
                        : 'deadline-text deadline-text--warning'
                    }
                  >
                    {getDeadlineText(item)}
                  </span>
                </div>
              </td>

              <td>
                <span
                  className={
                    item.status === 'OVERDUE'
                      ? 'status-badge status-badge--danger'
                      : 'status-badge status-badge--warning'
                  }
                >
                  {
                    item.status === 'OVERDUE'
                      ? t(
                          'attentionTable.overdue'
                        )
                      : t(
                          'attentionTable.dueSoon'
                        )
                  }
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


export default AttentionTable