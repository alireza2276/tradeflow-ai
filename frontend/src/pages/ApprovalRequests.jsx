import {
  useEffect,
  useState,
} from 'react'

import {
  useTranslation,
} from 'react-i18next'

import {
  approveApprovalRequest,
  getApprovalRequests,
  rejectApprovalRequest,
} from '../services/api'


function formatValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return '-'
  }

  return String(value)
}


function ApprovalRequests() {
  const { t } = useTranslation()

  const [requests, setRequests] =
    useState([])

  const [isLoading, setIsLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [actionId, setActionId] =
    useState(null)


  async function loadRequests() {
    setIsLoading(true)
    setError('')

    try {
      const data =
        await getApprovalRequests()

      setRequests(data)
    } catch (requestError) {
      setError(
        requestError.message ||
        t('approvals.loadError')
      )
    } finally {
      setIsLoading(false)
    }
  }


  useEffect(() => {
    loadRequests()
  }, [])


  function getOperationTitle(
    operation
  ) {
    if (operation === 'CREATE') {
      return t(
        'approvals.operations.create'
      )
    }

    if (operation === 'CORRECT') {
      return t(
        'approvals.operations.correct'
      )
    }

    if (operation === 'VOID') {
      return t(
        'approvals.operations.void'
      )
    }

    return operation
  }


  function getTargetTitle(
    targetType
  ) {
    if (
      targetType ===
      'currency_purchase'
    ) {
      return t(
        'approvals.targets.currencyPurchase'
      )
    }

    return targetType
  }


  function renderCreatePayload(
    payload
  ) {
    return (
      <div className="approval-details-grid">
        <div>
          <span>
            {t('approvals.fields.amount')}
          </span>

          <strong>
            {formatValue(payload.amount)}
          </strong>
        </div>

        <div>
          <span>
            {t('approvals.fields.currency')}
          </span>

          <strong>
            {formatValue(payload.currency)}
          </strong>
        </div>

        <div>
          <span>
            {t(
              'approvals.fields.purchaseDate'
            )}
          </span>

          <strong>
            {formatValue(
              payload.purchase_date
            )}
          </strong>
        </div>

        <div>
          <span>
            {t(
              'approvals.fields.registrationOrder'
            )}
          </span>

          <strong>
            {formatValue(
              payload.registration_order_id
            )}
          </strong>
        </div>
      </div>
    )
  }


  function renderCorrectionPayload(
    payload
  ) {
    const before =
      payload.before || {}

    const proposed =
      payload.proposed || {}

    return (
      <div className="approval-comparison">
        <div
          className={
            'approval-comparison-row ' +
            'approval-comparison-header'
          }
        >
          <span>
            {t('approvals.fields.field')}
          </span>

          <span>
            {t('approvals.fields.current')}
          </span>

          <span>
            {t('approvals.fields.proposed')}
          </span>
        </div>

        <div className="approval-comparison-row">
          <span>
            {t('approvals.fields.amount')}
          </span>

          <span>
            {formatValue(before.amount)}
          </span>

          <span>
            {formatValue(proposed.amount)}
          </span>
        </div>

        <div className="approval-comparison-row">
          <span>
            {t('approvals.fields.currency')}
          </span>

          <span>
            {formatValue(before.currency)}
          </span>

          <span>
            {formatValue(proposed.currency)}
          </span>
        </div>

        <div className="approval-comparison-row">
          <span>
            {t(
              'approvals.fields.purchaseDate'
            )}
          </span>

          <span>
            {formatValue(
              before.purchase_date
            )}
          </span>

          <span>
            {formatValue(
              proposed.purchase_date
            )}
          </span>
        </div>
      </div>
    )
  }


  function renderVoidPayload(
    payload
  ) {
    const before =
      payload.before || {}

    return (
      <>
        <div className="approval-void-notice">
          <strong>
            {t(
              'approvals.voidNoticeTitle'
            )}
          </strong>

          <p>
            {t(
              'approvals.voidNoticeDescription'
            )}
          </p>
        </div>

        <div className="approval-details-grid">
          <div>
            <span>
              {t('approvals.fields.amount')}
            </span>

            <strong>
              {formatValue(before.amount)}
            </strong>
          </div>

          <div>
            <span>
              {t('approvals.fields.currency')}
            </span>

            <strong>
              {formatValue(before.currency)}
            </strong>
          </div>

          <div>
            <span>
              {t(
                'approvals.fields.purchaseDate'
              )}
            </span>

            <strong>
              {formatValue(
                before.purchase_date
              )}
            </strong>
          </div>

          <div>
            <span>
              {t(
                'approvals.fields.registrationOrder'
              )}
            </span>

            <strong>
              {formatValue(
                before.registration_order_id
              )}
            </strong>
          </div>
        </div>
      </>
    )
  }


  function renderPayload(
    approvalRequest
  ) {
    if (
      approvalRequest.operation ===
      'CREATE'
    ) {
      return renderCreatePayload(
        approvalRequest.payload
      )
    }

    if (
      approvalRequest.operation ===
      'CORRECT'
    ) {
      return renderCorrectionPayload(
        approvalRequest.payload
      )
    }

    if (
      approvalRequest.operation ===
      'VOID'
    ) {
      return renderVoidPayload(
        approvalRequest.payload
      )
    }

    return null
  }


  async function handleApprove(
    approvalRequest
  ) {
    const confirmed =
      window.confirm(
        approvalRequest.operation ===
          'VOID'
          ? t(
              'approvals.confirmVoidApprove'
            )
          : t(
              'approvals.confirmApprove'
            )
      )

    if (!confirmed) {
      return
    }

    setActionId(
      approvalRequest.id
    )

    setError('')

    try {
      await approveApprovalRequest(
        approvalRequest.id
      )

      await loadRequests()
    } catch (requestError) {
      setError(
        requestError.message ||
        t('approvals.approveError')
      )
    } finally {
      setActionId(null)
    }
  }


  async function handleReject(
    approvalRequest
  ) {
    const reason =
      window.prompt(
        t(
          'approvals.rejectReasonPrompt'
        )
      )

    if (reason === null) {
      return
    }

    const trimmedReason =
      reason.trim()

    if (!trimmedReason) {
      setError(
        t(
          'approvals.rejectReasonRequired'
        )
      )

      return
    }

    setActionId(
      approvalRequest.id
    )

    setError('')

    try {
      await rejectApprovalRequest(
        approvalRequest.id,
        trimmedReason
      )

      await loadRequests()
    } catch (requestError) {
      setError(
        requestError.message ||
        t('approvals.rejectError')
      )
    } finally {
      setActionId(null)
    }
  }


  if (isLoading) {
    return (
      <div className="page-loading">
        {t('approvals.loading')}
      </div>
    )
  }


  return (
    <div className="approval-page">
      <div className="page-header">
        <div>
          <h1>
            {t('approvals.title')}
          </h1>

          <p>
            {t('approvals.subtitle')}
          </p>
        </div>
      </div>


      {error && (
        <div className="form-error">
          {error}
        </div>
      )}


      {requests.length === 0 ? (
        <div className="empty-state">
          {t('approvals.empty')}
        </div>
      ) : (
        <div className="approval-list">
          {requests.map(
            (approvalRequest) => (
              <div
                key={approvalRequest.id}
                className={
                  approvalRequest.operation ===
                  'VOID'
                    ? 'approval-card approval-card--void'
                    : 'approval-card'
                }
              >
                <div className="approval-card-header">
                  <div>
                    <strong>
                      {
                        getOperationTitle(
                          approvalRequest.operation
                        )
                      }
                    </strong>

                    <span>
                      {' · '}
                      {
                        getTargetTitle(
                          approvalRequest
                            .target_type
                        )
                      }
                    </span>
                  </div>

                  <span className="approval-status">
                    {t(
                      'approvals.status.pending'
                    )}
                  </span>
                </div>


                <div className="approval-meta">
                  <span>
                    {t('approvals.maker')}
                    {': '}
                    {
                      approvalRequest
                        .maker_username
                    }
                  </span>

                  <span>
                    {t('approvals.createdAt')}
                    {': '}
                    {
                      new Date(
                        approvalRequest
                          .created_at
                      ).toLocaleString(
                        'fa-IR'
                      )
                    }
                  </span>
                </div>


                {approvalRequest.reason && (
                  <div className="approval-reason">
                    <strong>
                      {t('approvals.reason')}
                    </strong>

                    <p>
                      {
                        approvalRequest
                          .reason
                      }
                    </p>
                  </div>
                )}


                {renderPayload(
                  approvalRequest
                )}


                <div className="approval-actions">
                  <button
                    type="button"
                    className={
                      'approval-button ' +
                      'approval-button--approve'
                    }
                    disabled={
                      actionId ===
                      approvalRequest.id
                    }
                    onClick={() =>
                      handleApprove(
                        approvalRequest
                      )
                    }
                  >
                    {
                      approvalRequest.operation ===
                      'VOID'
                        ? t(
                            'approvals.approveVoid'
                          )
                        : t(
                            'approvals.approve'
                          )
                    }
                  </button>

                  <button
                    type="button"
                    className={
                      'approval-button ' +
                      'approval-button--reject'
                    }
                    disabled={
                      actionId ===
                      approvalRequest.id
                    }
                    onClick={() =>
                      handleReject(
                        approvalRequest
                      )
                    }
                  >
                    {t('approvals.reject')}
                  </button>
                </div>
              </div>
            )
          )}
        </div>
      )}
    </div>
  )
}


export default ApprovalRequests