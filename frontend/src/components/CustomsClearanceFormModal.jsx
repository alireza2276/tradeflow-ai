import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

const emptyForm = { currency_purchase:'', declaration_number:'', clearance_date:'', amount:'', status:'DECLARED', notes:'' }

export default function CustomsClearanceFormModal({ isOpen, mode='create', clearance=null, currencyPurchases=[], onClose, onSubmit }) {
  const { t } = useTranslation()
  const [form,setForm]=useState(emptyForm)
  const [error,setError]=useState('')
  const [saving,setSaving]=useState(false)

  useEffect(()=>{
    if (!isOpen) return
    setError('')
    setForm(clearance ? {
      currency_purchase: clearance.currency_purchase || '',
      declaration_number: clearance.declaration_number || '',
      clearance_date: clearance.clearance_date || '',
      amount: clearance.amount || '',
      status: clearance.status || 'DECLARED',
      notes: clearance.notes || '',
    } : emptyForm)
  },[isOpen,clearance])

  if(!isOpen) return null
  function change(e){const{name,value}=e.target;setForm(c=>({...c,[name]:value}))}
  async function submit(e){
    e.preventDefault(); setError(''); setSaving(true)
    try {
      await onSubmit({...form, amount:String(form.amount).trim()})
    } catch(err){ setError(err.message || t('customsClearances.saveError')) }
    finally { setSaving(false) }
  }

  return <div className="modal-backdrop" role="presentation">
    <div className="modal-card" role="dialog" aria-modal="true">
      <div className="modal-header"><h2>{mode==='edit'?t('customsClearances.edit'):t('customsClearances.add')}</h2><button type="button" className="secondary-button" onClick={onClose}>{t('common.close')}</button></div>
      {error&&<div className="error-message">{error}</div>}
      <form onSubmit={submit} className="modal-form">
        <label>{t('customsClearances.purchase')}
          <select name="currency_purchase" value={form.currency_purchase} onChange={change} required disabled={mode==='edit'}>
            <option value="">{t('customsClearances.selectPurchase')}</option>
            {currencyPurchases.map(x=><option key={x.id} value={x.id}>{x.company_name} | {x.order_number} | #{x.purchase_sequence} | {Number(x.amount).toLocaleString()} {x.currency}</option>)}
          </select>
        </label>
        <label>{t('customsClearances.declarationNumber')}<input name="declaration_number" value={form.declaration_number} onChange={change} maxLength="100" required/></label>
        <label>{t('customsClearances.clearanceDate')}<input type="date" name="clearance_date" value={form.clearance_date} onChange={change}/></label>
        <label>{t('customsClearances.amount')}<input type="number" min="0.0001" step="0.0001" name="amount" value={form.amount} onChange={change} required/></label>
        <label>{t('customsClearances.status')}<select name="status" value={form.status} onChange={change} required>
          <option value="DECLARED">{t('customsClearances.statuses.DECLARED')}</option><option value="PARTIAL">{t('customsClearances.statuses.PARTIAL')}</option><option value="FINAL">{t('customsClearances.statuses.FINAL')}</option><option value="REJECTED">{t('customsClearances.statuses.REJECTED')}</option>
        </select></label>
        <label>{t('customsClearances.notes')}<textarea name="notes" value={form.notes} onChange={change} rows="3"/></label>
        <div className="table-actions"><button type="button" className="secondary-button" onClick={onClose}>{t('common.cancel')}</button><button type="submit" className="primary-button" disabled={saving}>{saving?t('common.loading'):t('common.save')}</button></div>
      </form>
    </div>
  </div>
}
