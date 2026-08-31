import {
  useEffect,
  useState,
} from 'react'

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

function CurrencyPurchases() {
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
        'Failed to load currency purchases.'
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
        Loading currency purchases...
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

  return (
    <div className="purchases-page">
      <div className="purchases-header">
        <div>
          <h1>Currency Purchases</h1>

          <p>
            Manage currency purchases and their deadlines.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={handleAddPurchase}
        >
          Add Currency Purchase
        </button>
      </div>

      <div className="purchases-table-wrapper">
        <table className="purchases-table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Order Number</th>
              <th>Amount</th>
              <th>Currency</th>
              <th>Purchase Date</th>
              <th>Deadline</th>
              <th>Actions</th>
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

                <td>
                  <div className="table-actions">
                    <button
                      type="button"
                      className="table-action-button"
                      onClick={() =>
                        handleEditPurchase(purchase)
                      }
                    >
                      Edit
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {purchases.length === 0 && (
              <tr>
                <td colSpan="7">
                  <div className="empty-state">
                    No currency purchases found.
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
