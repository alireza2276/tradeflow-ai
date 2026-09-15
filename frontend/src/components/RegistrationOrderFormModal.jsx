import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

import { getCompanies } from '../services/api'


function RegistrationOrderFormModal({
  isOpen,
  order = null,
  onClose,
  onSubmit,
}) {
  const { t } = useTranslation()

  const [companies, setCompanies] = useState([])

  const [formData, setFormData] = useState({
    company: '',
    order_number: '',
    registered_amount: '',
    currency: '',
    activity_type: '',
    shipment_deadline_months: '',
    is_active: true,
  })

  const [loadingCompanies, setLoadingCompanies] =
    useState(false)

  const [submitting, setSubmitting] =
    useState(false)

  const [error, setError] =
    useState('')

  const isEditMode = Boolean(order)


  useEffect(() => {
    if (!isOpen) {
      return
    }

    if (order) {
      setFormData({
        company:
          order.company || '',
        order_number:
          order.order_number || '',
        registered_amount:
          order.registered_amount || '',
        currency:
          order.currency || '',
        activity_type:
          order.activity_type || '',
        shipment_deadline_months:
          order.shipment_deadline_months || '',
        is_active:
          order.is_active ?? true,
      })
    } else {
      setFormData({
        company: '',
        order_number: '',
        registered_amount: '',
        currency: '',
        activity_type: '',
        shipment_deadline_months: '',
        is_active: true,
      })
    }

    setError('')

    async function loadCompanies() {
      try {
        setLoadingCompanies(true)

        const data =
          await getCompanies()

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
      [name]:
        type === 'checkbox'
          ? checked
          : value,
    }))
  }


  async function handleSubmit(event) {
    event.preventDefault()

    const normalizedCurrency =
      formData.currency
        .trim()
        .toUpperCase()

    if (!formData.company) {
      setError(
        t(
          'registrationOrderForm.selectCompanyError'
        )
      )
      return
    }

    if (
      !formData.order_number.trim() ||
      !formData.registered_amount ||
      !normalizedCurrency
    ) {
      setError(
        t(
          'registrationOrderForm.requiredFieldsError'
        )
      )
      return
    }

    const amount =
      Number(
        formData.registered_amount
      )

    if (
      !Number.isFinite(amount) ||
      amount <= 0
    ) {
      setError(
        t(
          'registrationOrderForm.invalidAmountError'
        )
      )
      return
    }

    if (
      !/^[A-Z]{3}$/.test(
        normalizedCurrency
      )
    ) {
      setError(
        t(
          'registrationOrderForm.invalidCurrencyError'
        )
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
        currency:
          normalizedCurrency,
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
              {
                isEditMode
                  ? t(
                      'registrationOrderForm.editTitle'
                    )
                  : t(
                      'registrationOrderForm.addTitle'
                    )
              }
            </h2>

            <p>
              {
                isEditMode
                  ? t(
                      'registrationOrderForm.editDescription'
                    )
                  : t(
                      'registrationOrderForm.addDescription'
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
            <label htmlFor="order-company">
              {t(
                'registrationOrderForm.company'
              )}
            </label>

            <select
              id="order-company"
              name="company"
              value={formData.company}
              onChange={(event) => {
                const companyId =
                  event.target.value

                const selectedCompany =
                  companies.find(
                    (item) =>
                      String(item.id) ===
                      String(companyId)
                  )

                const activityType =
                  selectedCompany?.company_type ||
                  ''

                setFormData(
                  (current) => ({
                    ...current,
                    company:
                      companyId,
                    activity_type:
                      activityType,
                    shipment_deadline_months:
                      activityType ===
                      'PRODUCTION'
                        ? '9'
                        : activityType ===
                          'COMMERCIAL'
                          ? '6'
                          : '',
                  })
                )
              }}
              disabled={
                loadingCompanies ||
                submitting
              }
              required
            >
              <option value="">
                {
                  loadingCompanies
                    ? t(
                        'registrationOrderForm.loadingCompanies'
                      )
                    : t(
                        'registrationOrderForm.selectCompany'
                      )
                }
              </option>

              {companies.map(
                (company) => (
                  <option
                    key={company.id}
                    value={company.id}
                  >
                    {company.name}
                  </option>
                )
              )}
            </select>
          </div>


          <div className="form-group">
            <label htmlFor="order-number">
              {t(
                'registrationOrderForm.orderNumber'
              )}
            </label>

            <input
              id="order-number"
              name="order_number"
              type="text"
              value={
                formData.order_number
              }
              onChange={handleChange}
              placeholder={t(
                'registrationOrderForm.orderNumberPlaceholder'
              )}
              disabled={submitting}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="registered-amount">
              {t(
                'registrationOrderForm.registeredAmount'
              )}
            </label>

            <input
              id="registered-amount"
              name="registered_amount"
              type="number"
              min="0.01"
              step="0.01"
              value={
                formData.registered_amount
              }
              onChange={handleChange}
              placeholder={t(
                'registrationOrderForm.registeredAmountPlaceholder'
              )}
              disabled={submitting}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="order-currency">
              {t(
                'registrationOrderForm.currency'
              )}
            </label>

            <input
              id="order-currency"
              name="currency"
              type="text"
              maxLength="3"
              value={formData.currency}
              onChange={(event) => {
                const value =
                  event.target.value
                    .toUpperCase()

                setFormData(
                  (current) => ({
                    ...current,
                    currency: value,
                  })
                )
              }}
              placeholder={t(
                'registrationOrderForm.currencyPlaceholder'
              )}
              disabled={submitting}
              required
            />
          </div>


          <div className="form-group">
            <label htmlFor="order-activity-type">
              {t(
                'registrationOrderForm.activityType'
              )}
            </label>

            <select
              id="order-activity-type"
              name="activity_type"
              value={
                formData.activity_type
              }
              onChange={handleChange}
              disabled={submitting}
              required
            >
              <option value="">
                {t(
                  'registrationOrderForm.selectActivityType'
                )}
              </option>

              <option value="COMMERCIAL">
                {t(
                  'registrationOrderForm.commercial'
                )}
              </option>

              <option value="PRODUCTION">
                {t(
                  'registrationOrderForm.production'
                )}
              </option>
            </select>
          </div>


          <div className="form-group">
            <label htmlFor="shipment-deadline-months">
              {t(
                'registrationOrderForm.shipmentDeadlineMonths'
              )}
            </label>

            <input
              id="shipment-deadline-months"
              name="shipment_deadline_months"
              type="number"
              min="1"
              max="60"
              value={
                formData.shipment_deadline_months
              }
              onChange={handleChange}
              disabled={submitting}
              required
            />

            <small>
              {t(
                'registrationOrderForm.deadlineRuleHint'
              )}
            </small>
          </div>


          <div className="form-group">
            <label className="form-checkbox">
              <input
                name="is_active"
                type="checkbox"
                checked={
                  formData.is_active
                }
                onChange={handleChange}
                disabled={submitting}
              />

              <span>
                {t(
                  'registrationOrderForm.activeOrder'
                )}
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
              {t('common.cancel')}
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={
                submitting ||
                loadingCompanies
              }
            >
              {
                submitting
                  ? (
                      isEditMode
                        ? t(
                            'registrationOrderForm.saving'
                          )
                        : t(
                            'registrationOrderForm.creating'
                          )
                    )
                  : (
                      isEditMode
                        ? t(
                            'registrationOrderForm.saveChanges'
                          )
                        : t(
                            'registrationOrderForm.createOrder'
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


export default RegistrationOrderFormModal