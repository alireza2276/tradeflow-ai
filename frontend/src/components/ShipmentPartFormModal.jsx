import {
  useEffect,
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'


function getEmptyFormData() {
  return {
    currency_purchase: '',
    amount: '',
    shipment_date: '',
    received_date: '',
    reference_number: '',
    notes: '',
    reason: '',
  }
}


function ShipmentPartFormModal({
  isOpen,
  mode,
  shipmentPart,
  currencyPurchases,
  onClose,
  onSubmit,
}) {
  const { t } = useTranslation()

  const [formData, setFormData] = useState(
    getEmptyFormData()
  )

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [submitError, setSubmitError] =
    useState('')

  const isEditMode =
    mode === 'edit'


  useEffect(() => {
    if (!isOpen) {
      return
    }

    if (
      isEditMode &&
      shipmentPart
    ) {
      setFormData({
        currency_purchase:
          shipmentPart.currency_purchase || '',
        amount:
          shipmentPart.amount || '',
        shipment_date:
          shipmentPart.shipment_date || '',
        received_date:
          shipmentPart.received_date || '',
        reference_number:
          shipmentPart.reference_number || '',
        notes:
          shipmentPart.notes || '',
        reason: '',
      })
    } else {
      setFormData(
        getEmptyFormData()
      )
    }

    setSubmitError('')
    setIsSubmitting(false)
  }, [
    isOpen,
    isEditMode,
    shipmentPart,
  ])


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setFormData(
      (currentFormData) => ({
        ...currentFormData,
        [name]: value,
      })
    )

    if (submitError) {
      setSubmitError('')
    }
  }


  async function handleSubmit(event) {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    if (
      !isEditMode &&
      !formData.currency_purchase
    ) {
      setSubmitError(
        t(
          'shipmentPartForm.selectPurchaseError'
        )
      )
      return
    }

    const amount =
      Number(formData.amount)

    if (
      !Number.isFinite(amount) ||
      amount <= 0
    ) {
      setSubmitError(
        t(
          'shipmentPartForm.invalidAmountError'
        )
      )
      return
    }

    if (
      isEditMode &&
      !formData.reason.trim()
    ) {
      setSubmitError(
        t(
          'shipmentPartForm.correctionReasonError'
        )
      )
      return
    }

    setIsSubmitting(true)
    setSubmitError('')

    try {
      const payload = {
        amount:
          formData.amount,

        shipment_date:
          formData.shipment_date || null,

        received_date:
          formData.received_date || null,

        reference_number:
          formData.reference_number.trim(),

        notes:
          formData.notes.trim(),
      }

      if (isEditMode) {
        payload.reason =
          formData.reason.trim()
      } else {
        payload.currency_purchase =
          formData.currency_purchase
      }

      await onSubmit(payload)
    } catch (error) {
      setSubmitError(
        error.message ||
        t(
          'shipmentPartForm.saveError'
        )
      )
    } finally {
      setIsSubmitting(false)
    }
  }


  if (!isOpen) {
    return null
  }


  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div>
            <h2>
              {
                isEditMode
                  ? t(
                      'shipmentPartForm.editTitle'
                    )
                  : t(
                      'shipmentPartForm.addTitle'
                    )
              }
            </h2>

            <p>
              {
                isEditMode
                  ? t(
                      'shipmentPartForm.editDescription'
                    )
                  : t(
                      'shipmentPartForm.addDescription'
                    )
              }
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={isSubmitting}
            aria-label={t('common.close')}
          >
            ×
          </button>
        </div>


        <form
          onSubmit={handleSubmit}
          className="modal-form"
          noValidate
        >
          <div className="form-group">
            <label htmlFor="currency_purchase">
              {t(
                'shipmentPartForm.currencyPurchase'
              )}
            </label>

            <select
              id="currency_purchase"
              name="currency_purchase"
              value={
                formData.currency_purchase
              }
              onChange={handleChange}
              disabled={
                isEditMode ||
                isSubmitting
              }
              required={!isEditMode}
            >
              <option value="">
                {t(
                  'shipmentPartForm.selectCurrencyPurchase'
                )}
              </option>

              {currencyPurchases.map(
                (purchase) => (
                  <option
                    key={purchase.id}
                    value={purchase.id}
                  >
                    {purchase.company_name}
                    {' | '}
                    {purchase.order_number}
                    {' | '}
                    {purchase.amount}
                    {' '}
                    {purchase.currency}
                  </option>
                )
              )}
            </select>
          </div>


          <div className="form-group">
            <label htmlFor="amount">
              {t(
                'shipmentPartForm.amount'
              )}
            </label>

            <input
              id="amount"
              name="amount"
              type="number"
              step="0.01"
              min="0.01"
              value={formData.amount}
              onChange={handleChange}
              disabled={isSubmitting}
              required
            />
          </div>


          <div className="form-row">
            <div className="form-group">
              <label htmlFor="shipment_date">
                {t(
                  'shipmentPartForm.shipmentDate'
                )}
              </label>

              <input
                id="shipment_date"
                name="shipment_date"
                type="date"
                value={
                  formData.shipment_date
                }
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="received_date">
                {t(
                  'shipmentPartForm.receivedDate'
                )}
              </label>

              <input
                id="received_date"
                name="received_date"
                type="date"
                value={
                  formData.received_date
                }
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </div>
          </div>


          <div className="form-group">
            <label htmlFor="reference_number">
              {t(
                'shipmentPartForm.referenceNumber'
              )}
            </label>

            <input
              id="reference_number"
              name="reference_number"
              type="text"
              value={
                formData.reference_number
              }
              onChange={handleChange}
              disabled={isSubmitting}
            />
          </div>


          <div className="form-group">
            <label htmlFor="notes">
              {t(
                'shipmentPartForm.notes'
              )}
            </label>

            <textarea
              id="notes"
              name="notes"
              rows="4"
              value={formData.notes}
              onChange={handleChange}
              disabled={isSubmitting}
            />
          </div>


          {isEditMode && (
            <div className="form-group">
              <label htmlFor="shipment-correction-reason">
                {t(
                  'shipmentPartForm.correctionReason'
                )}
              </label>

              <textarea
                id="shipment-correction-reason"
                name="reason"
                rows="3"
                value={formData.reason}
                onChange={handleChange}
                placeholder={t(
                  'shipmentPartForm.correctionReasonPlaceholder'
                )}
                disabled={isSubmitting}
                required
              />
            </div>
          )}


          {submitError && (
            <div className="modal-error-message">
              {submitError}
            </div>
          )}


          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={isSubmitting}
            >
              {t('common.cancel')}
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={isSubmitting}
            >
              {
                isSubmitting
                  ? (
                      isEditMode
                        ? t(
                            'shipmentPartForm.submittingCorrection'
                          )
                        : t(
                            'shipmentPartForm.submittingCreate'
                          )
                    )
                  : (
                      isEditMode
                        ? t(
                            'shipmentPartForm.submitCorrection'
                          )
                        : t(
                            'shipmentPartForm.submitCreate'
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


export default ShipmentPartFormModal