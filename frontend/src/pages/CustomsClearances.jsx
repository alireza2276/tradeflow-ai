import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import CustomsClearanceFormModal from '../components/CustomsClearanceFormModal'
import { createCustomsClearance, getCurrencyPurchases, getCustomsClearances, updateCustomsClearance } from '../services/api'
import { hasPermission } from '../utils/permissions'

function amount(v){return Number(v||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:4})}
export default function CustomsClearances({user}){
 const {t}=useTranslation(); const [rows,setRows]=useState([]); const [purchases,setPurchases]=useState([]); const [loading,setLoading]=useState(true); const [error,setError]=useState(''); const [open,setOpen]=useState(false); const [selected,setSelected]=useState(null)
 const canAdd=hasPermission(user,'trade_orders.add_customsclearance'); const canChange=hasPermission(user,'trade_orders.change_customsclearance')
 async function load(){try{setError(''); const [r,p]=await Promise.all([getCustomsClearances(),getCurrencyPurchases({status:'active'})]); setRows(r);setPurchases(p.filter(x=>!x.is_void))}catch(e){setError(e.message||t('customsClearances.loadError'))}finally{setLoading(false)}}
 useEffect(()=>{load()},[])
 async function save(payload){if(selected) await updateCustomsClearance(selected.id,payload); else await createCustomsClearance(payload); setOpen(false);setSelected(null);await load()}
 const purchaseById=Object.fromEntries(purchases.map(x=>[x.id,x]))
 return <div className="invoices-page"><div className="invoices-header"><div><h1>{t('customsClearances.title')}</h1><p>{t('customsClearances.description')}</p></div>{canAdd&&<button className="primary-button" onClick={()=>{setSelected(null);setOpen(true)}}>{t('customsClearances.add')}</button>}</div>
 {error&&<div className="error-state">{error}</div>}
 {loading?<div className="loading-state">{t('common.loading')}</div>:rows.length===0?<div className="empty-state">{t('customsClearances.empty')}</div>:<div className="invoices-table-wrapper"><table className="invoices-table"><thead><tr><th>{t('customsClearances.company')}</th><th>{t('customsClearances.order')}</th><th>{t('customsClearances.purchase')}</th><th>{t('customsClearances.declarationNumber')}</th><th>{t('customsClearances.clearanceDate')}</th><th>{t('customsClearances.amount')}</th><th>{t('customsClearances.status')}</th><th>{t('customsClearances.notes')}</th>{canChange&&<th>{t('customsClearances.actions')}</th>}</tr></thead><tbody>{rows.map(r=>{const x=purchaseById[r.currency_purchase]||{};return <tr key={r.id}><td>{x.company_name||'-'}</td><td>{x.order_number||'-'}</td><td>{x.purchase_sequence?`#${x.purchase_sequence}`:'-'}</td><td>{r.declaration_number}</td><td>{r.clearance_date||'-'}</td><td>{amount(r.amount)} {x.currency||''}</td><td>{t(`customsClearances.statuses.${r.status}`,{defaultValue:r.status})}</td><td>{r.notes||'-'}</td>{canChange&&<td><button className="secondary-button" onClick={()=>{setSelected(r);setOpen(true)}}>{t('common.edit')}</button></td>}</tr>})}</tbody></table></div>}
 <CustomsClearanceFormModal isOpen={open} mode={selected?'edit':'create'} clearance={selected} currencyPurchases={purchases} onClose={()=>{setOpen(false);setSelected(null)}} onSubmit={save}/></div>
}
