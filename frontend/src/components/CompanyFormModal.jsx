import { useState } from 'react'


function CompanyFormModal({
  onClose,
  onSubmit,
}) {
  const [formData, setFormData] = useState({
    name: '',
    national_id: '',
    company_type: 'COMMERCIAL',
  })

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setSubmitting(true)
    setError('')

    try {
      await onSubmit(formData)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="company-modal">

        <div className="modal-header">
          <div>
            <h2>Add Company</h2>
            <p>
              Register a new company in TradeFlowAI.
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="company-name">
              Company Name
            </label>

            <input
              id="company-name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter company name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="national-id">
              National ID
            </label>

            <input
              id="national-id"
              name="national_id"
              type="text"
              value={formData.national_id}
              onChange={handleChange}
              placeholder="Enter national ID"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="company-type">
              Company Type
            </label>

            <select
              id="company-type"
              name="company_type"
              value={formData.company_type}
              onChange={handleChange}
            >
              <option value="COMMERCIAL">
                Commercial
              </option>

              <option value="PRODUCTION">
                Production
              </option>
            </select>
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
              disabled={submitting}
            >
              {submitting
                ? 'Creating...'
                : 'Create Company'}
            </button>
          </div>

        </form>
      </div>
    </div>
  )
}

export default CompanyFormModal