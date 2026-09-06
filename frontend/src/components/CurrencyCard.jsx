import { useTranslation } from 'react-i18next'


function CurrencyCard({
  currency,
  purchasedAmount,
  documentedAmount,
  remainingAmount,
}) {
  const { t } = useTranslation()

  const formatAmount = (value) => {
    return Number(value).toLocaleString('en-US')
  }

  return (
    <div className="currency-card">
      <div className="currency-card-header">
        <div>
          <span className="currency-label">
            {t('currencyCard.currency')}
          </span>

          <h3>
            {currency}
          </h3>
        </div>

        <span className="currency-badge">
          {currency}
        </span>
      </div>

      <div className="currency-card-main">
        <span>
          {t('currencyCard.remainingAmount')}
        </span>

        <strong>
          {formatAmount(remainingAmount)}
        </strong>
      </div>

      <div className="currency-card-details">
        <div>
          <span>
            {t('currencyCard.purchased')}
          </span>

          <strong>
            {formatAmount(purchasedAmount)}
          </strong>
        </div>

        <div>
          <span>
            {t('currencyCard.documented')}
          </span>

          <strong>
            {formatAmount(documentedAmount)}
          </strong>
        </div>
      </div>
    </div>
  )
}


export default CurrencyCard