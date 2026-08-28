function AttentionTable({ cases }) {
  if (!cases || cases.length === 0) {
    return (
      <div className="empty-state">
        No cases currently require attention.
      </div>
    )
  }

  const formatAmount = (value) => {
    return Number(value).toLocaleString('en-US')
  }

  return (
    <div className="attention-table-wrapper">
      <table className="attention-table">
        <thead>
          <tr>
            <th>Company</th>
            <th>Order</th>
            <th>Currency</th>
            <th>Remaining</th>
            <th>Deadline</th>
            <th>Days</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {cases.map((item) => (
            <tr key={item.purchase_id}>
              <td>{item.company_name}</td>

              <td>{item.order_number}</td>

              <td>
                <span className="table-currency">
                  {item.currency}
                </span>
              </td>

              <td>
                {formatAmount(item.remaining_amount)}
              </td>

              <td>{item.deadline}</td>

              <td>
                {item.days_remaining}
              </td>

              <td>
                <span
                  className={
                    item.status === 'OVERDUE'
                      ? 'status-badge status-badge--danger'
                      : 'status-badge status-badge--warning'
                  }
                >
                  {item.status === 'OVERDUE'
                    ? 'Overdue'
                    : 'Due Soon'}
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