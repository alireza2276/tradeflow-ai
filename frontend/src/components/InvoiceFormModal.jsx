import {
  useState,
} from 'react'


function InvoiceFormModal({
  mode,
  invoice,
  shipmentParts,
  onClose,
  onSubmit,
}) {
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
    } catch (submitErrorValue) {
      setSubmitError(
        submitErrorValue.message ||
        'Failed to save invoice.'
      )
    } finally {
      setSubmitting(false)
    }
  }

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
              {mode === 'create'
                ? 'Add Invoice'
                : 'Edit Invoice'}
            </h2>

            <p>
              {mode === 'create'
                ? 'Create an invoice for a shipment part.'
                : 'Update invoice financial details.'}
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={submitting}
            aria-label="Close invoice form"
          >
            ×
          </button>
        </div>

        <form
          className="modal-form"
          onSubmit={handleSubmit}
        >
          <label>
            Shipment Part

            {mode === 'create' ? (
              <select
                name="shipment_part"
                value={formData.shipment_part}
                onChange={handleChange}
                required
                disabled={submitting}
              >
                <option value="">
                  Select shipment part
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
                      {shipmentPart.reference_number ||
                        'No reference'}
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
            FOB Amount

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
            Freight Amount

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
            Submission Date

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
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting
                ? 'Saving...'
                : mode === 'create'
                  ? 'Create Invoice'
                  : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default InvoiceFormModal
