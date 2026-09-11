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
  voidCurrencyPurchase,
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

  const [voidPurchase, setVoidPurchase] = useState(null)
  const [voidReason, setVoidReason] = useState('')
  const [voidSubmitting, setVoidSubmitting] = useState(false)
  const [voidError, setVoidError] = useState('')


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
      await createCurrencyPurchase(
        purchaseData
      )
    }

    handleCloseModal()

    await loadPurchases()
  }


  function handleOpenVoid(purchase) {
    setVoidPurchase(purchase)
    setVoidReason('')
    setVoidError('')
  }


  function handleCloseVoid() {
    if (voidSubmitting) {
      return
    }

    setVoidPurchase(null)
    setVoidReason('')
    setVoidError('')
  }


  async function handleSubmitVoid(event) {
    event.preventDefault()

    const trimmedReason =
      voidReason.trim()

    if (!trimmedReason) {
      setVoidError(
        t(
          'currencyPurchases.voidReasonRequired'
        )
      )

      return
    }

    if (!voidPurchase) {
      return
    }

    setVoidSubmitting(true)
    setVoidError('')

    try {
      await voidCurrencyPurchase(
        voidPurchase.id,
        trimmedReason
      )

      setVoidPurchase(null)
      setVoidReason('')
      setVoidError('')

      await loadPurchases()
    } catch (err) {
      setVoidError(
        err.message ||
        t('currencyPurchases.voidError')
      )
    } finally {
      setVoidSubmitting(false)
    }
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

  const canVoidPurchase = hasPermission(
    user,
    'trade_orders.void_currencypurchase'
  )

  const hasPurchaseActions =
    canEditPurchase ||
    canVoidPurchase


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
            {t(
              'currencyPurchases.addPurchase'
            )}
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
                {t(
                  'currencyPurchases.orderNumber'
                )}
              </th>

              <th>
                {t('currencyPurchases.amount')}
              </th>

              <th>
                {t('currencyPurchases.currency')}
              </th>

              <th>
                {t(
                  'currencyPurchases.purchaseDate'
                )}
              </th>

              <th>
                {t(
                  'currencyPurchases.deadline'
                )}
              </th>

              {hasPurchaseActions && (
                <th>
                  {t(
                    'currencyPurchases.actions'
                  )}
                </th>
              )}
            </tr>
          </thead>


          <tbody>
            {purchases.map(
              (purchase) => (
                <tr key={purchase.id}>
                  <td>
                    {purchase.company_name}
                  </td>

                  <td>
                    {purchase.order_number}
                  </td>

                  <td>
                    <span className="purchase-amount">
                      {formatAmount(
                        purchase.amount
                      )}
                    </span>
                  </td>

                  <td>
                    <span className="table-currency">
                      {purchase.currency}
                    </span>
                  </td>

                  <td>
                    <span className="purchase-date">
                      {
                        purchase
                          .purchase_date_dual
                      }
                    </span>
                  </td>

                  <td>
                    <span className="purchase-date">
                      {
                        purchase
                          .deadline_dual
                      }
                    </span>
                  </td>

                  {hasPurchaseActions && (
                    <td>
                      <div className="table-actions">
                        {canEditPurchase && !purchase.is_void && (
                          <button
                            type="button"
                            className="table-action-button"
                            onClick={() =>
                              handleEditPurchase(purchase)
                            }
                          >
                            {t('common.edit')}
                          </button>
                        )}

                        {canVoidPurchase && !purchase.is_void && (
                          <button
                            type="button"
                            className={
                              'table-action-button ' +
                              'table-action-button--danger'
                            }
                            onClick={() =>
                              handleOpenVoid(purchase)
                            }
                          >
                            {t(
                              'currencyPurchases.requestVoid'
                            )}
                          </button>
                        )}

                        {purchase.is_void && (
                          <span className="purchase-void-badge">
                            {t('currencyPurchases.voided')}
                          </span>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              )
            )}


            {purchases.length === 0 && (
              <tr>
                <td
                  colSpan={
                    hasPurchaseActions
                      ? 7
                      : 6
                  }
                >
                  <div className="empty-state">
                    {t(
                      'currencyPurchases.empty'
                    )}
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


      {voidPurchase && (
        <div className="modal-backdrop">
          <div className="company-modal">
            <div className="modal-header">
              <div>
                <h2>
                  {t(
                    'currencyPurchases.voidTitle'
                  )}
                </h2>

                <p>
                  {t(
                    'currencyPurchases.voidDescription'
                  )}
                </p>
              </div>

              <button
                type="button"
                className="modal-close-button"
                onClick={handleCloseVoid}
                disabled={voidSubmitting}
                aria-label={t('common.close')}
              >
                ×
              </button>
            </div>


            <form
              onSubmit={handleSubmitVoid}
              noValidate
            >
              <div className="form-group">
                <label htmlFor="void-reason">
                  {t(
                    'currencyPurchases.voidReason'
                  )}
                </label>

                <textarea
                  id="void-reason"
                  value={voidReason}
                  onChange={(event) =>
                    setVoidReason(
                      event.target.value
                    )
                  }
                  rows="4"
                  disabled={voidSubmitting}
                  required
                />
              </div>


              {voidError && (
                <div className="form-error">
                  {voidError}
                </div>
              )}


              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleCloseVoid}
                  disabled={voidSubmitting}
                >
                  {t('common.cancel')}
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={voidSubmitting}
                >
                  {
                    voidSubmitting
                      ? t(
                          'currencyPurchases.voidSubmitting'
                        )
                      : t(
                          'currencyPurchases.submitVoid'
                        )
                  }
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}


export default CurrencyPurchases