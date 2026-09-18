import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { hasPermission } from '../utils/permissions'
import CurrencyPurchaseFormModal from '../components/CurrencyPurchaseFormModal'
import {
  createCurrencyPurchase,
  exportCurrencyPurchasesXlsx,
  getCurrencyPurchases,
  updateCurrencyPurchase,
  voidCurrencyPurchase,
  settleCurrencyPurchaseObligation,
  reopenCurrencyPurchaseObligation,
  applyDeadlineExtension,
  getDeadlineExtensions,
} from '../services/api'

function formatAmount(value) {
  if (value === null || value === undefined || value === '') return '-'
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 4 })
}

const emptyFilters = {
  company: '', national_id: '', order_number: '', instrument_number: '',
  currency: '', purchase_date_from: '', purchase_date_to: '',
  deadline_from: '', deadline_to: '', amount_min: '', amount_max: '',
  status: '',
}

function CurrencyPurchases({ user }) {
  const { t } = useTranslation()
  const [purchases, setPurchases] = useState([])
  const [filters, setFilters] = useState(emptyFilters)
  const [appliedFilters, setAppliedFilters] = useState(emptyFilters)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedPurchase, setSelectedPurchase] = useState(null)
  const [voidPurchase, setVoidPurchase] = useState(null)
  const [voidReason, setVoidReason] = useState('')
  const [voidSubmitting, setVoidSubmitting] = useState(false)
  const [voidError, setVoidError] = useState('')
  const [compliancePurchase, setCompliancePurchase] = useState(null)
  const [complianceMode, setComplianceMode] = useState('')
  const [complianceReason, setComplianceReason] = useState('')
  const [complianceReference, setComplianceReference] = useState('')
  const [extensionDate, setExtensionDate] = useState('')
  const [deadlineKind, setDeadlineKind] = useState('IMPORT_CLEARANCE')
  const [complianceError, setComplianceError] = useState('')
  const [complianceSubmitting, setComplianceSubmitting] = useState(false)
  const [historyPurchase, setHistoryPurchase] = useState(null)
  const [deadlineHistory, setDeadlineHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')

  async function loadPurchases(activeFilters = appliedFilters) {
    try {
      setError('')
      setPurchases(await getCurrencyPurchases(activeFilters))
    } catch (err) {
      setError(err.message || t('currencyPurchases.loadError'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { loadPurchases(emptyFilters) }, [])

  function changeFilter(event) {
    const { name, value } = event.target
    setFilters((current) => ({ ...current, [name]: value }))
  }

  async function applyFilters(event) {
    event.preventDefault()
    setAppliedFilters(filters)
    setIsLoading(true)
    await loadPurchases(filters)
  }

  async function resetFilters() {
    setFilters(emptyFilters)
    setAppliedFilters(emptyFilters)
    setIsLoading(true)
    await loadPurchases(emptyFilters)
  }

  async function handleSubmit(data) {
    if (selectedPurchase) await updateCurrencyPurchase(selectedPurchase.id, data)
    else await createCurrencyPurchase(data)
    setIsModalOpen(false)
    setSelectedPurchase(null)
    await loadPurchases()
  }

  async function handleSubmitVoid(event) {
    event.preventDefault()
    if (!voidReason.trim()) {
      setVoidError(t('currencyPurchases.voidReasonRequired'))
      return
    }
    setVoidSubmitting(true)
    try {
      await voidCurrencyPurchase(voidPurchase.id, voidReason.trim())
      setVoidPurchase(null); setVoidReason(''); setVoidError('')
      await loadPurchases()
    } catch (err) {
      setVoidError(err.message || t('currencyPurchases.voidError'))
    } finally { setVoidSubmitting(false) }
  }

  function openCompliance(purchase, mode) {
    setCompliancePurchase(purchase)
    setComplianceMode(mode)
    setComplianceReason('')
    setComplianceReference('')
    setExtensionDate('')
    setDeadlineKind('IMPORT_CLEARANCE')
    setComplianceError('')
  }

  async function submitCompliance(event) {
    event.preventDefault()
    if (!complianceReason.trim()) {
      setComplianceError(t('compliance.reasonRequired'))
      return
    }
    setComplianceSubmitting(true)
    setComplianceError('')
    try {
      if (complianceMode === 'settle') {
        await settleCurrencyPurchaseObligation(compliancePurchase.id, { reason: complianceReason.trim(), reference: complianceReference.trim() })
      } else if (complianceMode === 'reopen') {
        await reopenCurrencyPurchaseObligation(compliancePurchase.id, { reason: complianceReason.trim(), reference: complianceReference.trim() })
      } else {
        if (!extensionDate) throw new Error(t('compliance.newDeadlineRequired'))
        await applyDeadlineExtension({
          currency_purchase: compliancePurchase.id,
          new_deadline: extensionDate,
          reason: complianceReason.trim(),
          reference: complianceReference.trim(),
          deadline_kind: deadlineKind,
        })
      }
      setCompliancePurchase(null)
      await loadPurchases()
    } catch (err) {
      setComplianceError(err.message || t('compliance.actionError'))
    } finally {
      setComplianceSubmitting(false)
    }
  }

  async function openDeadlineHistory(purchase) {
    setHistoryPurchase(purchase)
    setDeadlineHistory([])
    setHistoryError('')
    setHistoryLoading(true)
    try {
      setDeadlineHistory(await getDeadlineExtensions(purchase.id))
    } catch (err) {
      setHistoryError(err.message || t('compliance.historyLoadError'))
    } finally {
      setHistoryLoading(false)
    }
  }

  const canEdit = hasPermission(user, 'trade_orders.change_currencypurchase')
  const canVoid = hasPermission(user, 'trade_orders.void_currencypurchase')
  const canAdd = hasPermission(user, 'trade_orders.add_currencypurchase')
  const canSettle = hasPermission(user, 'trade_orders.settle_currencypurchase_obligation')
  const canExtend = hasPermission(user, 'trade_orders.extend_currencypurchase_deadline')

  return (
    <div className="purchases-page">
      <div className="purchases-header">
        <div><h1>{t('currencyPurchases.title')}</h1><p>{t('currencyPurchases.description')}</p></div>
        <div className="table-actions">
          <button type="button" className="secondary-button" onClick={() => exportCurrencyPurchasesXlsx(appliedFilters)}>
            {t('currencyPurchases.exportExcel')}
          </button>
          {canAdd && <button type="button" className="primary-button" onClick={() => { setSelectedPurchase(null); setIsModalOpen(true) }}>{t('currencyPurchases.addPurchase')}</button>}
        </div>
      </div>

      <form className="advanced-search-panel" onSubmit={applyFilters}>
        <h3>{t('currencyPurchases.advancedSearch')}</h3>
        <div className="advanced-search-grid">
          {[
            ['company','company'], ['national_id','nationalId'], ['order_number','orderNumber'],
            ['instrument_number','paymentInstrument'], ['currency','currency'],
            ['amount_min','amountMin'], ['amount_max','amountMax'],
          ].map(([name,key]) => <label key={name}>{t(`currencyPurchases.${key}`)}<input name={name} value={filters[name]} onChange={changeFilter} /></label>)}
          <label>{t('currencyPurchases.purchaseDateFrom')}<input type="date" name="purchase_date_from" value={filters.purchase_date_from} onChange={changeFilter}/></label>
          <label>{t('currencyPurchases.purchaseDateTo')}<input type="date" name="purchase_date_to" value={filters.purchase_date_to} onChange={changeFilter}/></label>
          <label>{t('currencyPurchases.deadlineFrom')}<input type="date" name="deadline_from" value={filters.deadline_from} onChange={changeFilter}/></label>
          <label>{t('currencyPurchases.deadlineTo')}<input type="date" name="deadline_to" value={filters.deadline_to} onChange={changeFilter}/></label>
          <label>{t('currencyPurchases.status')}
            <select name="status" value={filters.status} onChange={changeFilter}>
              <option value="">{t('currencyPurchases.allStatuses')}</option>
              <option value="active">{t('currencyPurchases.active')}</option>
              <option value="void">{t('currencyPurchases.voided')}</option>
            </select>
          </label>
        </div>
        <div className="table-actions">
          <button className="primary-button" type="submit">{t('currencyPurchases.search')}</button>
          <button className="secondary-button" type="button" onClick={resetFilters}>{t('currencyPurchases.reset')}</button>
        </div>
      </form>

      {isLoading ? <div className="page-state">{t('currencyPurchases.loading')}</div> :
       error ? <div className="page-state page-state--error">{error}</div> :
       <div className="purchases-table-wrapper"><table className="purchases-table">
        <thead><tr>
          <th>{t('currencyPurchases.company')}</th><th>{t('currencyPurchases.orderNumber')}</th>
          <th>{t('currencyPurchases.paymentInstrument')}</th><th>{t('currencyPurchases.purchaseSequence')}</th>
          <th>{t('currencyPurchases.registrationOrderAmount')}</th><th>{t('currencyPurchases.purchaseAmount')}</th>
          <th>{t('currencyPurchases.totalPurchased')}</th><th>{t('currencyPurchases.remainingToPurchase')}</th>
          <th>{t('currencyPurchases.currency')}</th><th>{t('currencyPurchases.purchaseDate')}</th>
          <th>{t('currencyPurchases.originalDeadline')}</th><th>{t('currencyPurchases.effectiveDeadline')}</th><th>{t('compliance.obligationStatus')}</th><th>{t('currencyPurchases.status')}</th>
          {(canEdit || canVoid || canSettle || canExtend) && <th>{t('currencyPurchases.actions')}</th>}
        </tr></thead>
        <tbody>{purchases.map((purchase) => <tr key={purchase.id}>
          <td>{purchase.company_name}</td><td>{purchase.order_number}</td>
          <td>{purchase.payment_instrument_number || '-'}</td>
          <td>{purchase.purchase_sequence ? t('currencyPurchases.purchaseSequenceValue',{count:purchase.purchase_sequence}) : '-'}</td>
          <td>{formatAmount(purchase.registration_order_amount)}</td><td>{formatAmount(purchase.amount)}</td>
          <td>{formatAmount(purchase.order_total_purchased)}</td><td>{formatAmount(purchase.order_remaining_to_purchase)}</td>
          <td>{purchase.currency}</td><td>{purchase.purchase_date_dual || purchase.purchase_date}</td>
          <td>{purchase.original_deadline || '-'}</td>
          <td><div>{purchase.deadline_dual || purchase.deadline || '-'}</div>{purchase.original_deadline && purchase.deadline && purchase.original_deadline !== purchase.deadline && <><div className="status-badge">{t('compliance.extended')}</div><button type="button" className="table-action-button" onClick={() => openDeadlineHistory(purchase)}>{t('compliance.extensionHistory')}</button></>}</td>
          <td>{t(`compliance.statuses.${purchase.obligation_status}`, purchase.obligation_status || '-')}</td>
          <td>{purchase.is_void ? t('currencyPurchases.voided') : t('currencyPurchases.active')}</td>
          {(canEdit || canVoid || canSettle || canExtend) && <td><div className="table-actions">
            {canEdit && !purchase.is_void && <button className="table-action-button" onClick={() => {setSelectedPurchase(purchase);setIsModalOpen(true)}}>{t('common.edit')}</button>}
            {canVoid && !purchase.is_void && <button className="table-action-button table-action-button--danger" onClick={() => {setVoidPurchase(purchase);setVoidReason('');setVoidError('')}}>{t('currencyPurchases.requestVoid')}</button>}
            {canExtend && !purchase.is_void && <button className="table-action-button" onClick={() => openCompliance(purchase, 'extend')}>{t('compliance.extendDeadline')}</button>}
            {canSettle && !purchase.is_void && purchase.obligation_status === 'CLEARED' && <button className="table-action-button" onClick={() => openCompliance(purchase, 'settle')}>{t('compliance.settle')}</button>}
            {canSettle && !purchase.is_void && purchase.obligation_status === 'SETTLED' && <button className="table-action-button" onClick={() => openCompliance(purchase, 'reopen')}>{t('compliance.reopen')}</button>}
          </div></td>}
        </tr>)}</tbody>
      </table></div>}

      {isModalOpen && <CurrencyPurchaseFormModal isOpen={isModalOpen} mode={selectedPurchase ? 'edit':'create'} purchase={selectedPurchase} onClose={() => {setIsModalOpen(false);setSelectedPurchase(null)}} onSubmit={handleSubmit}/>}
      {voidPurchase && <div className="modal-backdrop"><div className="modal-card"><h2>{t('currencyPurchases.requestVoid')}</h2><form className="modal-form" onSubmit={handleSubmitVoid}>
        <label>{t('currencyPurchases.voidReason')}<textarea value={voidReason} onChange={(e)=>setVoidReason(e.target.value)} /></label>
        {voidError && <div className="form-error">{voidError}</div>}
        <div className="modal-actions"><button type="button" className="secondary-button" onClick={()=>setVoidPurchase(null)} disabled={voidSubmitting}>{t('common.cancel')}</button><button type="submit" className="danger-button" disabled={voidSubmitting}>{t('currencyPurchases.requestVoid')}</button></div>
      </form></div></div>}
      {compliancePurchase && <div className="modal-backdrop"><div className="modal-card">
        <h2>{t(`compliance.${complianceMode}Title`)}</h2>
        <p>{compliancePurchase.company_name} | {compliancePurchase.order_number} | {formatAmount(compliancePurchase.amount)} {compliancePurchase.currency}</p>
        <form className="modal-form" onSubmit={submitCompliance}>
          {complianceMode === 'extend' && <>
            <label>{t('compliance.deadlineKind')}<select value={deadlineKind} onChange={(e)=>setDeadlineKind(e.target.value)}>
              <option value="IMPORT_CLEARANCE">{t('compliance.deadlineKinds.IMPORT_CLEARANCE')}</option>
              <option value="SHIPPING_DOCUMENTS">{t('compliance.deadlineKinds.SHIPPING_DOCUMENTS')}</option>
              <option value="FX_DIFFERENCE">{t('compliance.deadlineKinds.FX_DIFFERENCE')}</option>
            </select></label>
            <label>{t('compliance.newDeadline')}<input type="date" value={extensionDate} onChange={(e)=>setExtensionDate(e.target.value)} required /></label>
          </>}
          <label>{t('compliance.reason')}<textarea value={complianceReason} onChange={(e)=>setComplianceReason(e.target.value)} required /></label>
          <label>{t('compliance.reference')}<input value={complianceReference} onChange={(e)=>setComplianceReference(e.target.value)} /></label>
          {complianceError && <div className="form-error">{complianceError}</div>}
          <div className="modal-actions"><button type="button" className="secondary-button" onClick={()=>setCompliancePurchase(null)} disabled={complianceSubmitting}>{t('common.cancel')}</button><button type="submit" className="primary-button" disabled={complianceSubmitting}>{t('common.save')}</button></div>
        </form>
      </div></div>}
      {historyPurchase && <div className="modal-backdrop"><div className="modal-card">
        <h2>{t('compliance.extensionHistoryTitle')}</h2>
        <p>{historyPurchase.company_name} | {historyPurchase.order_number}</p>
        <div className="deadline-summary">
          <p><strong>{t('currencyPurchases.originalDeadline')}:</strong> {historyPurchase.original_deadline || '-'}</p>
          <p><strong>{t('currencyPurchases.effectiveDeadline')}:</strong> {historyPurchase.deadline_dual || historyPurchase.deadline || '-'}</p>
        </div>
        {historyLoading ? <div className="page-state">{t('compliance.historyLoading')}</div> : historyError ? <div className="form-error">{historyError}</div> : deadlineHistory.length === 0 ? <div className="page-state">{t('compliance.noExtensions')}</div> : <div className="purchases-table-wrapper"><table className="purchases-table"><thead><tr><th>{t('compliance.previousDeadline')}</th><th>{t('compliance.newDeadline')}</th><th>{t('compliance.reason')}</th><th>{t('compliance.reference')}</th><th>{t('compliance.approvedBy')}</th></tr></thead><tbody>{deadlineHistory.map((item) => <tr key={item.id}><td>{item.previous_deadline}</td><td>{item.new_deadline}</td><td>{item.reason || '-'}</td><td>{item.reference || '-'}</td><td>{item.approved_by_name || '-'}</td></tr>)}</tbody></table></div>}
        <div className="modal-actions"><button type="button" className="secondary-button" onClick={() => setHistoryPurchase(null)}>{t('common.cancel')}</button></div>
      </div></div>}
    </div>
  )
}
export default CurrencyPurchases
