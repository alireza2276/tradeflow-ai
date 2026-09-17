import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import {
  getRegistrationOrders,
} from '../services/api'


function CurrencyPurchaseFormModal({
  isOpen,
  purchase = null,
  onClose,
  onSubmit,
}) {
  const { t } = useTranslation()

  const [orders, setOrders] = useState([])

  const [formData, setFormData] = useState({
    registration_order: '',
    amount: '',
    currency: '',
    purchase_date: '',
    remittance_date: '',
    funding_source_code: '',
    reason: '',
  })

  const [loadingOrders, setLoadingOrders] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = Boolean(purchase)


  const selectedOrder = useMemo(
    () => (
      orders.find(
        (order) =>
          String(order.id) ===
          String(formData.registration_order)
      ) || null
    ),
    [
      orders,
      formData.registration_order,
    ]
  )


  useEffect(() => {
    if (!isOpen) {
      return
    }

    if (purchase) {
      setFormData({
        registration_order:
          purchase.registration_order || '',
        amount: purchase.amount || '',
        currency: purchase.currency || '',
        purchase_date:
          purchase.purchase_date || '',
        remittance_date:
          purchase.remittance_date || '',
        funding_source_code: purchase.funding_source_code || '',
        reason: '',
      })
    } else {
      setFormData({
        registration_order: '',
        amount: '',
        currency: '',
        purchase_date: '',
        remittance_date: '',
        funding_source_code: '',
        reason: '',
      })
    }

    setError('')

    async function loadOrders() {
      try {
        setLoadingOrders(true)

        const data =
          await getRegistrationOrders()

        setOrders(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoadingOrders(false)
      }
    }

    loadOrders()
  }, [isOpen, purchase])


  function handleOrderChange(event) {
    const orderId = event.target.value

    const order = orders.find(
      (item) =>
        String(item.id) ===
        String(orderId)
    )

    setFormData((current) => ({
      ...current,
      registration_order: orderId,
      currency: order
        ? order.currency
        : '',
    }))
  }


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
  }


  async function handleSubmit(event) {
    event.preventDefault()

    if (!formData.registration_order) {
      setError(
        t('currencyPurchaseForm.selectOrderError')
      )
      return
    }

    const amount = Number(formData.amount)

    if (!Number.isFinite(amount) || amount <= 0) {
      setError(
        t('currencyPurchaseForm.invalidAmountError')
      )
      return
    }

    if (!formData.purchase_date) {
      setError(
        t('currencyPurchaseForm.purchaseDateError')
      )
      return
    }

    if (!formData.currency) {
      setError(
        t(
          'currencyPurchaseForm.currencyUnavailableError'
        )
      )
      return
    }

    if (
      isEditMode &&
      !formData.reason.trim()
    ) {
      setError(
        t(
          'currencyPurchaseForm.correctionReasonError'
        )
      )
      return
    }

    setSubmitting(true)
    setError('')

    try {
      if (isEditMode) {
        await onSubmit({
          amount: formData.amount,
          purchase_date:
            formData.purchase_date,
          remittance_date: formData.remittance_date || null,
          funding_source_code: formData.funding_source_code.trim(),
          reason: formData.reason.trim(),
        })
      } else {
        await onSubmit({
          registration_order:
            formData.registration_order,
          amount: formData.amount,
          currency: formData.currency,
          purchase_date:
            formData.purchase_date,
          remittance_date: formData.remittance_date || null,
          funding_source_code: formData.funding_source_code.trim(),
        })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }


  if (!isOpen) {
    return null
  }


  return (
    <div className="modal-backdrop">
      <div className="company-modal">
        <div className="modal-header">
          <div>
            <h2>
              {
                isEditMode
                  ? t('currencyPurchaseForm.editTitle')
                  : t('currencyPurchaseForm.addTitle')
              }
            </h2>

            <p>
              {
                isEditMode
                  ? t(
                      'currencyPurchaseForm.editDescription'
                    )
                  : t(
                      'currencyPurchaseForm.addDescription'
                    )
              }
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={submitting}
            aria-label={t('common.close')}
          >
            ×
          </button>
        </div>


        <form
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="form-group">
            <label htmlFor="purchase-order">
              {t(
                'currencyPurchaseForm.registrationOrder'
              )}
            </label>

            <select
              id="purchase-order"
              name="registration_order"
              value={
                formData.registration_order
              }
              onChange={handleOrderChange}
              disabled={
                loadingOrders ||
                submitting ||
                isEditMode
              }
              required
            >
              <option value="">
                {
                  loadingOrders
                    ? t(
                        'currencyPurchaseForm.loadingOrders'
                      )
                    : t(
                        'currencyPurchaseForm.selectOrder'
                      )
                }
              </option>

              {orders.map((order) => (
                <option
                  key={order.id}
                  value={order.id}
                >
                  {order.company_name}
                  {' · '}
                  {order.order_number}
                  {' · '}
                  {order.currency}
                </option>
              ))}
            </select>
          </div>


          <div className="form-group">
            <label htmlFor="purchase-currency">
              {t('currencyPurchaseForm.currency')}
            </label>

            <input
              id="purchase-currency"
              type="text"
              value={
                selectedOrder?.currency ||
                formData.currency
              }
              readOnly
              disabled
            />
          </div>


          <div className="form-group">
            <label htmlFor="purchase-amount">
              {t(
                'currencyPurchaseForm.purchaseAmount'
              )}
            </label>

            <input
              id="purchase-amount"
              name="amount"
              type="number"
              min="0.01"
              step="0.01"
              value={formData.amount}
              onChange={handleChange}
              placeholder={t(
                'currencyPurchaseForm.purchaseAmountPlaceholder'
              )}
              disabled={submitting}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="purchase-date">
              {t(
                'currencyPurchaseForm.purchaseDate'
              )}
            </label>

            <input
              id="purchase-date"
              name="purchase_date"
              type="date"
              value={formData.purchase_date}
              onChange={handleChange}
              disabled={submitting}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="remittance-date">
              {t('currencyPurchaseForm.remittanceDate')}
            </label>
            <input
              id="remittance-date"
              name="remittance_date"
              type="date"
              value={formData.remittance_date}
              onChange={handleChange}
              disabled={submitting}
            />
            <small>{t('currencyPurchaseForm.remittanceDateHint')}</small>
          </div>

          <div className="form-group">
            <label htmlFor="purchase-funding-source-code">
              {t('currencyPurchaseForm.fundingSourceCode', { defaultValue: 'FX funding/source code' })}
            </label>
            <input
              id="purchase-funding-source-code"
              name="funding_source_code"
              type="text"
              value={formData.funding_source_code || ''}
              onChange={handleChange}
              maxLength={80}
              autoComplete="off"
            />
            <small>
              {t('currencyPurchaseForm.fundingSourceHelp', { defaultValue: 'Use only a verified internal code from the regulatory matrix.' })}
            </small>
          </div>

          {isEditMode && (
            <div className="form-group">
              <label htmlFor="purchase-correction-reason">
                {t(
                  'currencyPurchaseForm.correctionReason'
                )}
              </label>

              <textarea
                id="purchase-correction-reason"
                name="reason"
                value={formData.reason}
                onChange={handleChange}
                placeholder={t(
                  'currencyPurchaseForm.correctionReasonPlaceholder'
                )}
                disabled={submitting}
                rows="3"
                required
              />
            </div>
          )}


          {error && (
            <div className="form-error">
              {error}
            </div>
          )}


          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={submitting}
            >
              {t('common.cancel')}
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={
                submitting ||
                loadingOrders
              }
            >
              {
                submitting
                  ? (
                      isEditMode
                        ? t('currencyPurchaseForm.saving')
                        : t('currencyPurchaseForm.creating')
                    )
                  : (
                      isEditMode
                        ? t(
                            'currencyPurchaseForm.saveChanges'
                          )
                        : t(
                            'currencyPurchaseForm.createPurchase'
                          )
                    )
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default CurrencyPurchaseFormModal