import {
  useEffect,
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import {
  hasPermission,
} from '../utils/permissions'

import CurrencyPurchaseFormModal
  from '../components/CurrencyPurchaseFormModal'

import {
  createCurrencyPurchase,
  getCurrencyPurchases,
  updateCurrencyPurchase,
} from '../services/api'


function formatAmount(value) {
  const [integerPart, decimalPart = ''] =
    String(value).split('.')

  const isNegative = integerPart.startsWith('-')

  const digits = isNegative
    ? integerPart.slice(1)
    : integerPart

  const grouped = digits.replace(
    /\B(?=(\d{3})+(?!\d))/g,
    ','
  )

  const trimmedDecimal =
    decimalPart.replace(/0+$/, '')

  return `${isNegative ? '-' : ''}${grouped}${
    trimmedDecimal ? `.${trimmedDecimal}` : ''
  }`
}


function CurrencyPurchases({
  user,
}) {
  const { t } = useTranslation()

  const [purchases, setPurchases] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedPurchase, setSelectedPurchase] = useState(null)


  async function loadPurchases() {
    try {
      setError('')

      const data = await getCurrencyPurchases()
      setPurchases(data)
    } catch (loadError) {
      setError(
        loadError.message ||
        t('currencyPurchases.loadError')
      )
    } finally {
      setIsLoading(false)
    }
  }


  useEffect(() => {
    loadPurchases()
  }, [])


  function handleAddPurchase() {
    setSelectedPurchase(null)
    setIsModalOpen(true)
  }


  function handleEditPurchase(purchase) {
    setSelectedPurchase(purchase)
    setIsModalOpen(true)
  }


  function handleCloseModal() {
    setIsModalOpen(false)
    setSelectedPurchase(null)
  }


  async function handleSubmit(purchaseData) {
    if (selectedPurchase) {
      await updateCurrencyPurchase(
        selectedPurchase.id,
        purchaseData
      )
    } else {
      await createCurrencyPurchase(purchaseData)
    }

    handleCloseModal()
    await loadPurchases()
  }


  if (isLoading) {
    return (
      <div className="page-state">
        {t('currencyPurchases.loading')}
      </div>
    )
  }


  if (error) {
    return (
      <div className="page-state page-state--error">
        {error}
      </div>
    )
  }


  const canEditPurchase = hasPermission(
    user,
    'trade_orders.change_currencypurchase'
  )


  return (
    <div className="purchases-page">
      <div className="purchases-header">
        <div>
          <h1>
            {t('currencyPurchases.title')}
          </h1>

          <p>
            {t('currencyPurchases.description')}
          </p>
        </div>

        {hasPermission(
          user,
          'trade_orders.add_currencypurchase'
        ) && (
          <button
            type="button"
            className="primary-button"
            onClick={handleAddPurchase}
          >
            {t('currencyPurchases.addPurchase')}
          </button>
        )}
      </div>


      <div className="purchases-table-wrapper">
        <table className="purchases-table">
          <thead>
            <tr>
              <th>
                {t('currencyPurchases.company')}
              </th>

              <th>
                {t('currencyPurchases.orderNumber')}
              </th>

              <th>
                {t('currencyPurchases.amount')}
              </th>

              <th>
                {t('currencyPurchases.currency')}
              </th>

              <th>
                {t('currencyPurchases.purchaseDate')}
              </th>

              <th>
                {t('currencyPurchases.deadline')}
              </th>

              {canEditPurchase && (
                <th>
                  {t('currencyPurchases.actions')}
                </th>
              )}
            </tr>
          </thead>

          <tbody>
            {purchases.map((purchase) => (
              <tr key={purchase.id}>
                <td>
                  {purchase.company_name}
                </td>

                <td>
                  {purchase.order_number}
                </td>

                <td>
                  <span className="purchase-amount">
                    {formatAmount(purchase.amount)}
                  </span>
                </td>

                <td>
                  <span className="table-currency">
                    {purchase.currency}
                  </span>
                </td>

                <td>
                  <span className="purchase-date">
                    {purchase.purchase_date_dual}
                  </span>
                </td>

                <td>
                  <span className="purchase-date">
                    {purchase.deadline_dual}
                  </span>
                </td>

                {canEditPurchase && (
                  <td>
                    <div className="table-actions">
                      <button
                        type="button"
                        className="table-action-button"
                        onClick={() =>
                          handleEditPurchase(purchase)
                        }
                      >
                        {t('common.edit')}
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}


            {purchases.length === 0 && (
              <tr>
                <td
                  colSpan={
                    canEditPurchase
                      ? 7
                      : 6
                  }
                >
                  <div className="empty-state">
                    {t('currencyPurchases.empty')}
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>


      <CurrencyPurchaseFormModal
        isOpen={isModalOpen}
        purchase={selectedPurchase}
        onClose={handleCloseModal}
        onSubmit={handleSubmit}
      />
    </div>
  )
}


export default CurrencyPurchases