import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

import {
  approveApprovalRequest,
  getApprovalRequests,
  rejectApprovalRequest,
} from '../services/api'

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return '-'
  }
  return String(value)
}

function ApprovalRequests() {
  const { t, i18n } = useTranslation()
  const [requests, setRequests] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionId, setActionId] = useState(null)

  async function loadRequests() {
    setIsLoading(true)
    setError('')
    try {
      setRequests(await getApprovalRequests())
    } catch (requestError) {
      setError(requestError.message || t('approvals.loadError'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [])

  function getOperationTitle(operation) {
    const key = {
      CREATE: 'create',
      CORRECT: 'correct',
      VOID: 'void',
    }[operation]
    return key ? t(`approvals.operations.${key}`) : operation
  }

  function getTargetTitle(targetType) {
    if (targetType === 'currency_purchase') {
      return t('approvals.targets.currencyPurchase')
    }
    if (targetType === 'shipment_part') {
      return t('approvals.targets.shipmentPart')
    }
    return targetType
  }

  function renderDetails(items) {
    return (
      <div className="approval-details-grid">
        {items.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{formatValue(value)}</strong>
          </div>
        ))}
      </div>
    )
  }

  function renderComparison(before, proposed, fields) {
    return (
      <div className="approval-comparison">
        <div className="approval-comparison-row approval-comparison-header">
          <span>{t('approvals.fields.field')}</span>
          <span>{t('approvals.fields.current')}</span>
          <span>{t('approvals.fields.proposed')}</span>
        </div>
        {fields.map(([key, label]) => (
          <div className="approval-comparison-row" key={key}>
            <span>{label}</span>
            <span>{formatValue(before?.[key])}</span>
            <span>{formatValue(proposed?.[key])}</span>
          </div>
        ))}
      </div>
    )
  }

  function renderPayload(approvalRequest) {
    const { operation, target_type: targetType, payload = {} } = approvalRequest

    if (targetType === 'currency_purchase') {
      if (operation === 'CREATE') {
        return renderDetails([
          [t('approvals.fields.amount'), payload.amount],
          [t('approvals.fields.currency'), payload.currency],
          [t('approvals.fields.purchaseDate'), payload.purchase_date],
          [t('approvals.fields.registrationOrder'), payload.registration_order_id],
        ])
      }
      if (operation === 'CORRECT') {
        return renderComparison(payload.before, payload.proposed, [
          ['amount', t('approvals.fields.amount')],
          ['currency', t('approvals.fields.currency')],
          ['purchase_date', t('approvals.fields.purchaseDate')],
        ])
      }
      if (operation === 'VOID') {
        const before = payload.before || {}
        return (
          <>
            <div className="approval-void-notice">
              <strong>{t('approvals.voidNoticeTitle')}</strong>
              <p>{t('approvals.voidNoticeDescription')}</p>
            </div>
            {renderDetails([
              [t('approvals.fields.amount'), before.amount],
              [t('approvals.fields.currency'), before.currency],
              [t('approvals.fields.purchaseDate'), before.purchase_date],
              [t('approvals.fields.registrationOrder'), before.registration_order_id],
            ])}
          </>
        )
      }
    }

    if (targetType === 'shipment_part') {
      if (operation === 'CREATE') {
        return renderDetails([
          [t('approvals.fields.amount'), payload.amount],
          [t('approvals.fields.currencyPurchase'), payload.currency_purchase_id],
          [t('approvals.fields.shipmentDate'), payload.shipment_date],
          [t('approvals.fields.receivedDate'), payload.received_date],
          [t('approvals.fields.referenceNumber'), payload.reference_number],
          [t('approvals.fields.notes'), payload.notes],
        ])
      }
      if (operation === 'CORRECT') {
        return renderComparison(payload.before, payload.proposed, [
          ['amount', t('approvals.fields.amount')],
          ['shipment_date', t('approvals.fields.shipmentDate')],
          ['received_date', t('approvals.fields.receivedDate')],
          ['reference_number', t('approvals.fields.referenceNumber')],
          ['notes', t('approvals.fields.notes')],
        ])
      }
      if (operation === 'VOID') {
        const before = payload.before || {}
        return (
          <>
            <div className="approval-void-notice">
              <strong>{t('approvals.shipmentVoidNoticeTitle')}</strong>
              <p>{t('approvals.shipmentVoidNoticeDescription')}</p>
            </div>
            {renderDetails([
              [t('approvals.fields.amount'), before.amount],
              [t('approvals.fields.currencyPurchase'), before.currency_purchase_id],
              [t('approvals.fields.shipmentDate'), before.shipment_date],
              [t('approvals.fields.receivedDate'), before.received_date],
              [t('approvals.fields.referenceNumber'), before.reference_number],
            ])}
          </>
        )
      }
    }

    return null
  }

  async function handleApprove(approvalRequest) {
    const confirmKey = approvalRequest.operation === 'VOID'
      ? 'approvals.confirmVoidApprove'
      : 'approvals.confirmApprove'
    if (!window.confirm(t(confirmKey))) return

    setActionId(approvalRequest.id)
    setError('')
    try {
      await approveApprovalRequest(approvalRequest.id)
      await loadRequests()
    } catch (requestError) {
      setError(requestError.message || t('approvals.approveError'))
    } finally {
      setActionId(null)
    }
  }

  async function handleReject(approvalRequest) {
    const reason = window.prompt(t('approvals.rejectReasonPrompt'))
    if (reason === null) return
    const trimmedReason = reason.trim()
    if (!trimmedReason) {
      setError(t('approvals.rejectReasonRequired'))
      return
    }

    setActionId(approvalRequest.id)
    setError('')
    try {
      await rejectApprovalRequest(approvalRequest.id, trimmedReason)
      await loadRequests()
    } catch (requestError) {
      setError(requestError.message || t('approvals.rejectError'))
    } finally {
      setActionId(null)
    }
  }

  if (isLoading) {
    return <div className="page-loading">{t('approvals.loading')}</div>
  }

  return (
    <div className="approval-page">
      <div className="page-header">
        <div>
          <h1>{t('approvals.title')}</h1>
          <p>{t('approvals.subtitle')}</p>
        </div>
      </div>

      {error && <div className="form-error">{error}</div>}

      {requests.length === 0 ? (
        <div className="empty-state">{t('approvals.empty')}</div>
      ) : (
        <div className="approval-list">
          {requests.map((approvalRequest) => (
            <div
              key={approvalRequest.id}
              className={approvalRequest.operation === 'VOID'
                ? 'approval-card approval-card--void'
                : 'approval-card'}
            >
              <div className="approval-card-header">
                <div>
                  <strong>{getOperationTitle(approvalRequest.operation)}</strong>
                  <span>{' · '}{getTargetTitle(approvalRequest.target_type)}</span>
                </div>
                <span className="approval-status">{t('approvals.status.pending')}</span>
              </div>

              <div className="approval-meta">
                <span>{t('approvals.maker')}: {approvalRequest.maker_username}</span>
                <span>
                  {t('approvals.createdAt')}: {' '}
                  {new Date(approvalRequest.created_at).toLocaleString(
                    i18n.language === 'fa' ? 'fa-IR' : 'en-US'
                  )}
                </span>
              </div>

              {approvalRequest.reason && (
                <div className="approval-reason">
                  <strong>{t('approvals.reason')}</strong>
                  <p>{approvalRequest.reason}</p>
                </div>
              )}

              {renderPayload(approvalRequest)}

              <div className="approval-actions">
                <button
                  type="button"
                  className="approval-button approval-button--approve"
                  disabled={actionId === approvalRequest.id}
                  onClick={() => handleApprove(approvalRequest)}
                >
                  {approvalRequest.operation === 'VOID'
                    ? t('approvals.approveVoid')
                    : t('approvals.approve')}
                </button>
                <button
                  type="button"
                  className="approval-button approval-button--reject"
                  disabled={actionId === approvalRequest.id}
                  onClick={() => handleReject(approvalRequest)}
                >
                  {t('approvals.reject')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ApprovalRequests
