import { useEffect, useState } from 'react'

import { getCompanies } from '../services/api'


function RegistrationOrderFormModal({
  isOpen,
  order = null,
  onClose,
  onSubmit,
}) {
  const [companies, setCompanies] = useState([])

  const [formData, setFormData] = useState({
    company: '',
    order_number: '',
    registered_amount: '',
    currency: '',
    is_active: true,
  })

  const [loadingCompanies, setLoadingCompanies] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = Boolean(order)

  useEffect(() => {
    if (!isOpen) {
      return
    }

    if (order) {
      setFormData({
        company: order.company || '',
        order_number: order.order_number || '',
        registered_amount: order.registered_amount || '',
        currency: order.currency || '',
        is_active: order.is_active ?? true,
      })
    } else {
      setFormData({
        company: '',
        order_number: '',
        registered_amount: '',
        currency: '',
        is_active: true,
      })
    }

    setError('')

    async function loadCompanies() {
      try {
        setLoadingCompanies(true)

        const data = await getCompanies()
        setCompanies(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoadingCompanies(false)
      }
    }

    loadCompanies()
  }, [isOpen, order])

  function handleChange(event) {
    const {
      name,
      value,
      type,
      checked,
    } = event.target

    setFormData((current) => ({
      ...current,
      [name]: type === 'checkbox'
        ? checked
        : value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const normalizedCurrency =
      formData.currency.trim().toUpperCase()

    if (!formData.company) {
      setError('Please select a company.')
      return
    }

    if (
      !formData.order_number.trim() ||
      !formData.registered_amount ||
      !normalizedCurrency
    ) {
      setError('Please complete all required fields.')
      return
    }

    const amount = Number(formData.registered_amount)

    if (!Number.isFinite(amount) || amount <= 0) {
      setError(
        'Registered amount must be greater than zero.'
      )
      return
    }

    if (!/^[A-Z]{3}$/.test(normalizedCurrency)) {
      setError(
        'Currency must be a valid 3-letter code.'
      )
      return
    }

    setSubmitting(true)
    setError('')

    try {
      await onSubmit({
        ...formData,
        order_number:
          formData.order_number.trim(),
        currency: normalizedCurrency,
      })
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
              {isEditMode
                ? 'Edit Registration Order'
                : 'Add Registration Order'}
            </h2>

            <p>
              {isEditMode
                ? 'Update registration order information.'
                : 'Create a new registered trade order.'}
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={submitting}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="order-company">
              Company
            </label>

            <select
              id="order-company"
              name="company"
              value={formData.company}
              onChange={handleChange}
              disabled={
                loadingCompanies ||
                submitting
              }
              required
            >
              <option value="">
                {loadingCompanies
                  ? 'Loading companies...'
                  : 'Select a company'}
              </option>

              {companies.map((company) => (
                <option
                  key={company.id}
                  value={company.id}
                >
                  {company.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="order-number">
              Order Number
            </label>

            <input
              id="order-number"
              name="order_number"
              type="text"
              value={formData.order_number}
              onChange={handleChange}
              placeholder="e.g. TF-USD-002"
              disabled={submitting}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="registered-amount">
              Registered Amount
            </label>

            <input
              id="registered-amount"
              name="registered_amount"
              type="number"
              min="0.01"
              step="0.01"
              value={formData.registered_amount}
              onChange={handleChange}
              placeholder="e.g. 50000"
              disabled={submitting}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="order-currency">
              Currency
            </label>

            <input
              id="order-currency"
              name="currency"
              type="text"
              maxLength="3"
              value={formData.currency}
              onChange={(event) => {
                const value =
                  event.target.value.toUpperCase()

                setFormData((current) => ({
                  ...current,
                  currency: value,
                }))
              }}
              placeholder="USD"
              disabled={submitting}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-checkbox">
              <input
                name="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={handleChange}
                disabled={submitting}
              />

              <span>
                Active registration order
              </span>
            </label>
          </div>

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
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={
                submitting ||
                loadingCompanies
              }
            >
              {submitting
                ? (
                    isEditMode
                      ? 'Saving...'
                      : 'Creating...'
                  )
                : (
                    isEditMode
                      ? 'Save Changes'
                      : 'Create Order'
                  )}
            </button>
          </div>

        </form>
      </div>
    </div>
  )
}

export default RegistrationOrderFormModal