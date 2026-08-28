function CurrencyCard({
  currency,
  purchasedAmount,
  documentedAmount,
  remainingAmount,
}) {
  const formatAmount = (value) => {
    return Number(value).toLocaleString('en-US')
  }

  return (
    <div className="currency-card">

      <div className="currency-card-header">
        <div>
          <span className="currency-label">
            Currency
          </span>

          <h3>{currency}</h3>
        </div>

        <span className="currency-badge">
          {currency}
        </span>
      </div>

      <div className="currency-card-main">
        <span>Remaining Amount</span>

        <strong>
          {formatAmount(remainingAmount)}
        </strong>
      </div>

      <div className="currency-card-details">

        <div>
          <span>Purchased</span>
          <strong>
            {formatAmount(purchasedAmount)}
          </strong>
        </div>

        <div>
          <span>Documented</span>
          <strong>
            {formatAmount(documentedAmount)}
          </strong>
        </div>

      </div>

    </div>
  )
}

export default CurrencyCard