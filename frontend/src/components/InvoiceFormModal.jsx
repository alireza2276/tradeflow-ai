import {
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'


function InvoiceFormModal({
  mode,
  invoice,
  shipmentParts,
  onClose,
  onSubmit,
}) {
  const { t } = useTranslation()

  const [formData, setFormData] = useState(() => {
    if (
      mode === 'edit' &&
      invoice
    ) {
      return {
        shipment_part:
          invoice.shipment_part || '',
        fob_amount:
          invoice.fob_amount || '',
        freight_amount:
          invoice.freight_amount || '',
        submission_date:
          invoice.submission_date || '',
      }
    }

    return {
      shipment_part: '',
      fob_amount: '',
      freight_amount: '0',
      submission_date: '',
    }
  })

  const [submitting, setSubmitting] =
    useState(false)

  const [submitError, setSubmitError] =
    useState('')


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

    if (submitting) {
      return
    }

    if (
      mode === 'create' &&
      !formData.shipment_part
    ) {
      setSubmitError(
        t('invoiceForm.selectShipmentError')
      )
      return
    }

    const fobAmount =
      Number(formData.fob_amount)

    if (
      !Number.isFinite(fobAmount) ||
      fobAmount < 0
    ) {
      setSubmitError(
        t('invoiceForm.invalidFobError')
      )
      return
    }

    const freightAmount =
      Number(formData.freight_amount)

    if (
      !Number.isFinite(freightAmount) ||
      freightAmount < 0
    ) {
      setSubmitError(
        t('invoiceForm.invalidFreightError')
      )
      return
    }

    if (!formData.submission_date) {
      setSubmitError(
        t('invoiceForm.submissionDateError')
      )
      return
    }

    setSubmitting(true)
    setSubmitError('')

    const payload = {
      fob_amount:
        formData.fob_amount,
      freight_amount:
        formData.freight_amount,
      submission_date:
        formData.submission_date,
    }

    if (mode === 'create') {
      payload.shipment_part =
        formData.shipment_part
    }

    try {
      await onSubmit(payload)
    } catch (error) {
      setSubmitError(
        error.message ||
        t('invoiceForm.saveError')
      )
    } finally {
      setSubmitting(false)
    }
  }


  const isCreateMode =
    mode === 'create'


  return (
    <div
      className="modal-backdrop"
      role="presentation"
    >
      <div
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="invoice-modal-title"
      >
        <div className="modal-header">
          <div>
            <h2 id="invoice-modal-title">
              {
                isCreateMode
                  ? t('invoiceForm.addTitle')
                  : t('invoiceForm.editTitle')
              }
            </h2>

            <p>
              {
                isCreateMode
                  ? t(
                      'invoiceForm.addDescription'
                    )
                  : t(
                      'invoiceForm.editDescription'
                    )
              }
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={submitting}
            aria-label={t('invoiceForm.close')}
          >
            ×
          </button>
        </div>


        <form
          className="modal-form"
          onSubmit={handleSubmit}
          noValidate
        >
          <label>
            {t('invoiceForm.shipmentPart')}

            {isCreateMode ? (
              <select
                name="shipment_part"
                value={formData.shipment_part}
                onChange={handleChange}
                required
                disabled={submitting}
              >
                <option value="">
                  {t(
                    'invoiceForm.selectShipmentPart'
                  )}
                </option>

                {shipmentParts.map(
                  (shipmentPart) => (
                    <option
                      key={shipmentPart.id}
                      value={shipmentPart.id}
                    >
                      {shipmentPart.company_name}
                      {' | '}
                      {shipmentPart.order_number}
                      {' | '}
                      {
                        shipmentPart.reference_number ||
                        t('invoiceForm.noReference')
                      }
                      {' | '}
                      {shipmentPart.amount}
                      {' '}
                      {shipmentPart.purchase_currency}
                    </option>
                  )
                )}
              </select>
            ) : (
              <input
                type="text"
                value={[
                  invoice?.company_name,
                  invoice?.order_number,
                ]
                  .filter(Boolean)
                  .join(' | ')}
                disabled
              />
            )}
          </label>


          <label>
            {t('invoiceForm.fobAmount')}

            <input
              type="number"
              name="fob_amount"
              value={formData.fob_amount}
              onChange={handleChange}
              min="0"
              step="0.0001"
              required
              disabled={submitting}
            />
          </label>


          <label>
            {t('invoiceForm.freightAmount')}

            <input
              type="number"
              name="freight_amount"
              value={formData.freight_amount}
              onChange={handleChange}
              min="0"
              step="0.0001"
              required
              disabled={submitting}
            />
          </label>


          <label>
            {t('invoiceForm.submissionDate')}

            <input
              type="date"
              name="submission_date"
              value={formData.submission_date}
              onChange={handleChange}
              required
              disabled={submitting}
            />
          </label>


          {submitError && (
            <div
              className="modal-error-message"
              role="alert"
            >
              {submitError}
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
              disabled={submitting}
            >
              {
                submitting
                  ? t('invoiceForm.saving')
                  : (
                      isCreateMode
                        ? t(
                            'invoiceForm.createInvoice'
                          )
                        : t(
                            'invoiceForm.saveChanges'
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


export default InvoiceFormModal