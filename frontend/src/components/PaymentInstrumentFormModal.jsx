import {
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'


function PaymentInstrumentFormModal({
  mode,
  paymentInstrument,
  registrationOrders,
  onClose,
  onSubmit,
}) {
  const { t } = useTranslation()

  const [formData, setFormData] = useState(
    () => ({
      registration_order:
        paymentInstrument?.registration_order || '',
      instrument_number:
        paymentInstrument?.instrument_number || '',
      operation_type:
        paymentInstrument?.operation_type || 'REMITTANCE',
      issue_date:
        paymentInstrument?.issue_date || '',
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

    if (saving) {
      return
    }

    if (
      mode === 'create' &&
      !formData.registration_order
    ) {
      setError(
        t(
          'paymentInstrumentForm.selectOrderError'
        )
      )
      return
    }

    if (!formData.instrument_number.trim()) {
      setError(
        t(
          'paymentInstrumentForm.instrumentNumberError'
        )
      )
      return
    }

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
              operation_type: formData.operation_type,
              issue_date: formData.issue_date || null,
            }
          : {
              instrument_number:
                formData.instrument_number.trim(),
              operation_type: formData.operation_type,
              issue_date: formData.issue_date || null,
            }

      await onSubmit(payload)
    } catch (submitError) {
      setError(
        submitError.message ||
        t('paymentInstrumentForm.saveError')
      )
    } finally {
      setSaving(false)
    }
  }


  const isCreateMode =
    mode === 'create'


  return (
    <div className="modal-backdrop">
      <div
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="payment-instrument-modal-title"
      >
        <div className="modal-header">
          <div>
            <h2 id="payment-instrument-modal-title">
              {
                isCreateMode
                  ? t(
                      'paymentInstrumentForm.addTitle'
                    )
                  : t(
                      'paymentInstrumentForm.editTitle'
                    )
              }
            </h2>

            <p>
              {
                isCreateMode
                  ? t(
                      'paymentInstrumentForm.addDescription'
                    )
                  : t(
                      'paymentInstrumentForm.editDescription'
                    )
              }
            </p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            disabled={saving}
            aria-label={t(
              'paymentInstrumentForm.close'
            )}
          >
            ×
          </button>
        </div>


        <form
          onSubmit={handleSubmit}
          className="modal-form"
          noValidate
        >
          {isCreateMode && (
            <div className="form-group">
              <label htmlFor="registration_order">
                {t(
                  'paymentInstrumentForm.registrationOrder'
                )}
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
                  {t(
                    'paymentInstrumentForm.selectRegistrationOrder'
                  )}
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


          {!isCreateMode && (
            <div className="form-group">
              <label>
                {t(
                  'paymentInstrumentForm.registrationOrder'
                )}
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
              {t(
                'paymentInstrumentForm.instrumentNumber'
              )}
            </label>

            <input
              id="instrument_number"
              name="instrument_number"
              type="text"
              value={formData.instrument_number}
              onChange={handleChange}
              placeholder={t(
                'paymentInstrumentForm.instrumentNumberPlaceholder'
              )}
              maxLength={100}
              required
              disabled={saving}
              autoComplete="off"
            />
          </div>


          <div className="form-group">
            <label htmlFor="operation_type">
              {t('paymentInstrumentForm.operationType', { defaultValue: 'نوع عملیات ارزی' })}
            </label>
            <select id="operation_type" name="operation_type" value={formData.operation_type} onChange={handleChange} disabled={saving} required>
              <option value="REMITTANCE">{t('paymentInstrumentForm.remittance', { defaultValue: 'حواله ارزی' })}</option>
              <option value="DOCUMENTARY_COLLECTION">{t('paymentInstrumentForm.documentaryCollection', { defaultValue: 'برات / وصولی اسنادی' })}</option>
              <option value="LETTER_OF_CREDIT">{t('paymentInstrumentForm.letterOfCredit', { defaultValue: 'اعتبار اسنادی' })}</option>
              <option value="OTHER">{t('paymentInstrumentForm.otherOperation', { defaultValue: 'سایر' })}</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="issue_date">
              {t('paymentInstrumentForm.issueDate', { defaultValue: 'تاریخ صدور / گشایش ابزار' })}
            </label>
            <input id="issue_date" name="issue_date" type="date" value={formData.issue_date} onChange={handleChange} disabled={saving} />
          </div>

          {error && (
            <div
              className="modal-error-message"
              role="alert"
            >
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
              {t('common.cancel')}
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={saving}
            >
              {
                saving
                  ? t(
                      'paymentInstrumentForm.saving'
                    )
                  : (
                      isCreateMode
                        ? t(
                            'paymentInstrumentForm.create'
                          )
                        : t(
                            'paymentInstrumentForm.saveChanges'
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


export default PaymentInstrumentFormModal