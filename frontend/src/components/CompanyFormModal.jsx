import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'


function CompanyFormModal({
  company = null,
  onClose,
  onSubmit,
}) {
  const { t } = useTranslation()

  const [formData, setFormData] = useState({
    name: '',
    national_id: '',
    company_type: 'COMMERCIAL',
  })

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = Boolean(company)


  useEffect(() => {
    if (company) {
      setFormData({
        name: company.name || '',
        national_id: company.national_id || '',
        company_type:
          company.company_type || 'COMMERCIAL',
      })
    }
  }, [company])


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
            <h2>
              {
                isEditMode
                  ? t('companyForm.editTitle')
                  : t('companyForm.addTitle')
              }
            </h2>

            <p>
              {
                isEditMode
                  ? t('companyForm.editDescription')
                  : t('companyForm.addDescription')
              }
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            aria-label={t('common.close')}
          >
            ×
          </button>
        </div>


        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="company-name">
              {t('companyForm.companyName')}
            </label>

            <input
              id="company-name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder={t(
                'companyForm.companyNamePlaceholder'
              )}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="national-id">
              {t('companyForm.nationalId')}
            </label>

            <input
              id="national-id"
              name="national_id"
              type="text"
              value={formData.national_id}
              onChange={handleChange}
              placeholder={t(
                'companyForm.nationalIdPlaceholder'
              )}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="company-type">
              {t('companyForm.companyType')}
            </label>

            <select
              id="company-type"
              name="company_type"
              value={formData.company_type}
              onChange={handleChange}
            >
              <option value="COMMERCIAL">
                {t('companyForm.commercial')}
              </option>

              <option value="PRODUCTION">
                {t('companyForm.production')}
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
              {t('common.cancel')}
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {
                submitting
                  ? (
                      isEditMode
                        ? t('companyForm.saving')
                        : t('companyForm.creating')
                    )
                  : (
                      isEditMode
                        ? t('companyForm.saveChanges')
                        : t('companyForm.createCompany')
                    )
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


export default CompanyFormModal