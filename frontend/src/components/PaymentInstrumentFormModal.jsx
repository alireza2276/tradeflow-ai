import {
  useState,
} from 'react'


function PaymentInstrumentFormModal({
  mode,
  paymentInstrument,
  registrationOrders,
  onClose,
  onSubmit,
}) {
  const [formData, setFormData] = useState(
    () => ({
      registration_order:
        paymentInstrument?.registration_order || '',
      instrument_number:
        paymentInstrument?.instrument_number || '',
    })
  )

  const [error, setError] =
    useState('')

  const [saving, setSaving] =
    useState(false)

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setSaving(true)

    try {
      const payload =
        mode === 'create'
          ? {
              registration_order:
                formData.registration_order,
              instrument_number:
                formData.instrument_number.trim(),
            }
          : {
              instrument_number:
                formData.instrument_number.trim(),
            }

      await onSubmit(payload)
    } catch (submitError) {
      setError(
        submitError.message ||
        'Failed to save payment instrument.'
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div>
            <h2>
              {mode === 'create'
                ? 'Add Payment Instrument'
                : 'Edit Payment Instrument'}
            </h2>

            <p>
              {mode === 'create'
                ? 'Link a payment instrument to a registration order.'
                : 'Update the payment instrument number.'}
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={saving}
          >
            ×
          </button>
        </div>

        <form
          onSubmit={handleSubmit}
          className="modal-form"
        >
          {mode === 'create' && (
            <div className="form-group">
              <label htmlFor="registration_order">
                Registration Order
              </label>

              <select
                id="registration_order"
                name="registration_order"
                value={formData.registration_order}
                onChange={handleChange}
                required
                disabled={saving}
              >
                <option value="">
                  Select registration order
                </option>

                {registrationOrders.map(
                  (order) => (
                    <option
                      key={order.id}
                      value={order.id}
                    >
                      {order.company_name}
                      {' | '}
                      {order.order_number}
                      {' | '}
                      {order.currency}
                    </option>
                  )
                )}
              </select>
            </div>
          )}

          {mode === 'edit' && (
            <div className="form-group">
              <label>
                Registration Order
              </label>

              <input
                type="text"
                value={
                  `${paymentInstrument.company_name} | ` +
                  `${paymentInstrument.order_number}`
                }
                disabled
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="instrument_number">
              Instrument Number
            </label>

            <input
              id="instrument_number"
              name="instrument_number"
              type="text"
              value={formData.instrument_number}
              onChange={handleChange}
              placeholder="Example: PI-2026-0001"
              maxLength={100}
              required
              disabled={saving}
              autoComplete="off"
            />
          </div>

          {error && (
            <div className="modal-error-message">
              {error}
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={saving}
            >
              {saving
                ? 'Saving...'
                : mode === 'create'
                  ? 'Create'
                  : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PaymentInstrumentFormModal