import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { hasPermission } from '../utils/permissions'
import InvoiceFormModal from '../components/InvoiceFormModal'
import ShipmentPartFormModal from '../components/ShipmentPartFormModal'
import {
  createInvoice, createShipmentPart, exportInvoicesXlsx, getCurrencyPurchases,
  getInvoices, getShipmentParts, updateInvoice,
} from '../services/api'

function formatAmount(value) {
  if (value === null || value === undefined || value === '') return '-'
  return Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
const emptyFilters = {
  company:'', national_id:'', order_number:'', instrument_number:'', reference_number:'',
  purchase_date_from:'', purchase_date_to:'', deadline_from:'', deadline_to:'',
  submission_date_from:'', submission_date_to:'',
}

function Invoices({ user }) {
  const { t } = useTranslation()
  const [invoices,setInvoices]=useState([])
  const [shipmentParts,setShipmentParts]=useState([])
  const [currencyPurchases,setCurrencyPurchases]=useState([])
  const [filters,setFilters]=useState(emptyFilters)
  const [appliedFilters,setAppliedFilters]=useState(emptyFilters)
  const [loading,setLoading]=useState(true)
  const [error,setError]=useState('')
  const [invoiceModal,setInvoiceModal]=useState(false)
  const [selectedInvoice,setSelectedInvoice]=useState(null)
  const [shipmentModal,setShipmentModal]=useState(false)

  const canAddInvoice=hasPermission(user,'documents.add_invoice')
  const canChangeInvoice=hasPermission(user,'documents.change_invoice')
  const canAddShipment=hasPermission(user,'trade_orders.add_shipmentpart')

  async function loadData(activeFilters=appliedFilters) {
    try {
      setError('')
      const [invoiceData, shipmentData, purchaseData] = await Promise.all([
        getInvoices(activeFilters),
        getShipmentParts(),
        canAddShipment ? getCurrencyPurchases({status:'active'}) : Promise.resolve([]),
      ])
      setInvoices(invoiceData); setShipmentParts(shipmentData); setCurrencyPurchases(purchaseData)
    } catch(err) { setError(err.message || t('invoices.loadError')) }
    finally { setLoading(false) }
  }
  useEffect(()=>{loadData(emptyFilters)},[])

  function changeFilter(e){const{name,value}=e.target;setFilters(c=>({...c,[name]:value}))}
  async function search(e){e.preventDefault();setAppliedFilters(filters);setLoading(true);await loadData(filters)}
  async function reset(){setFilters(emptyFilters);setAppliedFilters(emptyFilters);setLoading(true);await loadData(emptyFilters)}

  const availableShipmentParts=shipmentParts.filter(part=>!part.is_void && !invoices.some(inv=>inv.shipment_part===part.id))

  async function saveInvoice(payload){
    if(selectedInvoice) await updateInvoice(selectedInvoice.id,payload)
    else await createInvoice(payload)
    setInvoiceModal(false);setSelectedInvoice(null);await loadData()
  }
  async function submitShipment(payload){
    await createShipmentPart(payload)
    setShipmentModal(false)
    window.alert(t('invoices.shipmentApprovalNotice'))
    await loadData()
  }

  return <div className="invoices-page">
    <div className="invoices-header"><div><h1>{t('invoices.unifiedTitle')}</h1><p>{t('invoices.unifiedDescription')}</p></div>
      <div className="table-actions">
        <button className="secondary-button" type="button" onClick={()=>exportInvoicesXlsx(appliedFilters)}>{t('invoices.exportExcel')}</button>
        {canAddShipment && <button className="secondary-button" type="button" onClick={()=>setShipmentModal(true)}>{t('invoices.addShippingDocument')}</button>}
        {canAddInvoice && <button className="primary-button" type="button" onClick={()=>{setSelectedInvoice(null);setInvoiceModal(true)}}>{t('invoices.addInvoice')}</button>}
      </div>
    </div>

    <form className="advanced-search-panel" onSubmit={search}><h3>{t('invoices.advancedSearch')}</h3>
      <div className="advanced-search-grid">
        {[['company','company'],['national_id','nationalId'],['order_number','order'],['instrument_number','paymentInstrument'],['reference_number','shipmentReference']].map(([name,key])=>
          <label key={name}>{t(`invoices.${key}`)}<input name={name} value={filters[name]} onChange={changeFilter}/></label>)}
        <label>{t('invoices.purchaseDateFrom')}<input type="date" name="purchase_date_from" value={filters.purchase_date_from} onChange={changeFilter}/></label>
        <label>{t('invoices.purchaseDateTo')}<input type="date" name="purchase_date_to" value={filters.purchase_date_to} onChange={changeFilter}/></label>
        <label>{t('invoices.deadlineFrom')}<input type="date" name="deadline_from" value={filters.deadline_from} onChange={changeFilter}/></label>
        <label>{t('invoices.deadlineTo')}<input type="date" name="deadline_to" value={filters.deadline_to} onChange={changeFilter}/></label>
        <label>{t('invoices.submissionDateFrom')}<input type="date" name="submission_date_from" value={filters.submission_date_from} onChange={changeFilter}/></label>
        <label>{t('invoices.submissionDateTo')}<input type="date" name="submission_date_to" value={filters.submission_date_to} onChange={changeFilter}/></label>
      </div><div className="table-actions"><button className="primary-button" type="submit">{t('invoices.search')}</button><button className="secondary-button" type="button" onClick={reset}>{t('invoices.reset')}</button></div>
    </form>

    {canAddInvoice && availableShipmentParts.length>0 && <div className="info-state">{t('invoices.awaitingInvoice',{count:availableShipmentParts.length})}</div>}
    {loading?<div className="loading-state">{t('invoices.loading')}</div>:error?<div className="error-state">{error}</div>:
    invoices.length===0?<div className="empty-state">{t('invoices.empty')}</div>:
    <div className="invoices-table-wrapper"><table className="invoices-table"><thead><tr>
      <th>{t('invoices.company')}</th><th>{t('invoices.order')}</th><th>{t('invoices.paymentInstrument')}</th>
      <th>{t('invoices.documentPart')}</th><th>{t('invoices.shipmentReference')}</th>
      <th>{t('invoices.purchaseDate')}</th><th>{t('invoices.deadline')}</th>
      <th>{t('invoices.purchaseTrancheAmount')}</th><th>{t('invoices.totalPurchased')}</th>
      <th>{t('invoices.fob')}</th><th>{t('invoices.freight')}</th><th>{t('invoices.total')}</th>
      <th>{t('invoices.remainingAmount')}</th><th>{t('invoices.currency')}</th><th>{t('invoices.submissionDate')}</th>
      {canChangeInvoice&&<th>{t('invoices.actions')}</th>}
    </tr></thead><tbody>{invoices.map(invoice=><tr key={invoice.id}>
      <td>{invoice.company_name}</td><td>{invoice.order_number}</td><td>{invoice.payment_instrument_number||'-'}</td>
      <td>{t('invoices.partValue',{count:invoice.document_part_number})}</td><td>{invoice.shipment_reference_number||'-'}</td>
      <td>{invoice.purchase_date_dual||invoice.purchase_date}</td><td>{invoice.deadline_dual||invoice.deadline}</td>
      <td>{formatAmount(invoice.currency_purchase_amount)}</td><td>{formatAmount(invoice.order_total_purchased)}</td>
      <td>{formatAmount(invoice.fob_amount)}</td><td>{formatAmount(invoice.freight_amount)}</td><td>{formatAmount(invoice.total_amount)}</td>
      <td>{formatAmount(invoice.remaining_amount)}</td><td>{invoice.order_currency}</td><td>{invoice.submission_date_dual||invoice.submission_date}</td>
      {canChangeInvoice&&<td><button className="secondary-button" onClick={()=>{setSelectedInvoice(invoice);setInvoiceModal(true)}}>{t('common.edit')}</button></td>}
    </tr>)}</tbody></table></div>}

    {invoiceModal&&<InvoiceFormModal mode={selectedInvoice?'edit':'create'} invoice={selectedInvoice} shipmentParts={availableShipmentParts} onClose={()=>{setInvoiceModal(false);setSelectedInvoice(null)}} onSubmit={saveInvoice}/>}
    <ShipmentPartFormModal isOpen={shipmentModal} mode="create" shipmentPart={null} currencyPurchases={currencyPurchases} onClose={()=>setShipmentModal(false)} onSubmit={submitShipment}/>
  </div>
}
export default Invoices
