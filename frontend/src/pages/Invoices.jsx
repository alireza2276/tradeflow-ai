import {
  useEffect,
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import InvoiceFormModal
  from '../components/InvoiceFormModal'

import {
  createInvoice,
  getInvoices,
  getShipmentParts,
  updateInvoice,
} from '../services/api'

import {
  hasPermission,
} from '../utils/permissions'


function formatAmount(value) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return '-'
  }

  const amount = Number(value)

  if (!Number.isFinite(amount)) {
    return value
  }

  return new Intl.NumberFormat(
    'en-US',
    {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }
  ).format(amount)
}


function Invoices({ user }) {
  const { t } = useTranslation()

  const [invoices, setInvoices] =
    useState([])

  const [
    shipmentParts,
    setShipmentParts,
  ] = useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [
    isModalOpen,
    setIsModalOpen,
  ] = useState(false)

  const [
    modalMode,
    setModalMode,
  ] = useState('create')

  const [
    selectedInvoice,
    setSelectedInvoice,
  ] = useState(null)


  const canAddInvoice = hasPermission(
    user,
    'documents.add_invoice'
  )

  const canChangeInvoice = hasPermission(
    user,
    'documents.change_invoice'
  )


  useEffect(() => {
    let isMounted = true

    async function fetchData() {
      try {
        const invoiceData =
          await getInvoices()

        if (!isMounted) {
          return
        }

        setInvoices(invoiceData)

        if (canAddInvoice) {
          const shipmentData =
            await getShipmentParts()

          if (!isMounted) {
            return
          }

          setShipmentParts(shipmentData)
        } else {
          setShipmentParts([])
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError.message ||
            t('invoices.loadError')
          )
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      isMounted = false
    }
  }, [canAddInvoice, t])


  function openCreateModal() {
    setSelectedInvoice(null)
    setModalMode('create')
    setIsModalOpen(true)
  }


  function openEditModal(invoice) {
    setSelectedInvoice(invoice)
    setModalMode('edit')
    setIsModalOpen(true)
  }


  function closeModal() {
    setIsModalOpen(false)
    setSelectedInvoice(null)
  }


  async function loadData() {
    const invoiceData =
      await getInvoices()

    setInvoices(invoiceData)

    if (canAddInvoice) {
      const shipmentData =
        await getShipmentParts()

      setShipmentParts(shipmentData)
    } else {
      setShipmentParts([])
    }
  }


  async function handleSubmit(payload) {
    if (modalMode === 'create') {
      await createInvoice(payload)
    } else {
      await updateInvoice(
        selectedInvoice.id,
        payload
      )
    }

    closeModal()
    await loadData()
  }


  const availableShipmentParts =
    shipmentParts.filter(
      (shipmentPart) =>
        !invoices.some(
          (invoiceItem) =>
            invoiceItem.shipment_part ===
            shipmentPart.id
        )
    )


  if (loading) {
    return (
      <div className="loading-state">
        {t('invoices.loading')}
      </div>
    )
  }


  if (error) {
    return (
      <div className="error-state">
        {error}
      </div>
    )
  }


  return (
    <div className="invoices-page">
      <div className="invoices-header">
        <div>
          <h1>
            {t('invoices.title')}
          </h1>

          <p>
            {t('invoices.description')}
          </p>
        </div>

        {canAddInvoice && (
          <button
            type="button"
            className="primary-button"
            onClick={openCreateModal}
          >
            {t('invoices.addInvoice')}
          </button>
        )}
      </div>


      {invoices.length === 0 ? (
        <div className="empty-state">
          {t('invoices.empty')}
        </div>
      ) : (
        <div className="invoices-table-wrapper">
          <table className="invoices-table">
            <thead>
              <tr>
                <th>
                  {t('invoices.company')}
                </th>

                <th>
                  {t('invoices.order')}
                </th>

                <th>
                  {t('invoices.documentPart')}
                </th>

                <th>
                  {t('invoices.purchaseTrancheAmount')}
                </th>

                <th>
                  {t('invoices.totalPurchased')}
                </th>

                <th>
                  {t('invoices.fob')}
                </th>

                <th>
                  {t('invoices.freight')}
                </th>

                <th>
                  {t('invoices.total')}
                </th>

                <th>
                  {t('invoices.remainingAmount')}
                </th>

                <th>
                  {t('invoices.currency')}
                </th>

                <th>
                  {t('invoices.submissionDate')}
                </th>

                <th>
                  {t('invoices.actions')}
                </th>
              </tr>
            </thead>

            <tbody>
              {invoices.map(
                (invoice) => (
                  <tr key={invoice.id}>
                    <td>
                      {invoice.company_name}
                    </td>

                    <td>
                      {invoice.order_number}
                    </td>

                    <td>
                      {t(
                        'invoices.partValue',
                        {
                          count:
                            invoice.document_part_number,
                        }
                      )}
                    </td>

                    <td>
                      {formatAmount(invoice.currency_purchase_amount)}
                    </td>

                    <td>
                      {formatAmount(invoice.order_total_purchased)}
                    </td>

                    <td>
                      {formatAmount(invoice.fob_amount)}
                    </td>

                    <td>
                      {formatAmount(invoice.freight_amount)}
                    </td>

                    <td>
                      {formatAmount(invoice.total_amount)}
                    </td>

                    <td>
                      {formatAmount(invoice.remaining_amount)}
                    </td>

                    <td>
                      <span className="table-currency">
                        {invoice.order_currency}
                      </span>
                    </td>

                    <td>
                      {
                        invoice.submission_date_dual ||
                        invoice.submission_date
                      }
                    </td>

                    <td>
                      {canChangeInvoice ? (
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() =>
                            openEditModal(
                              invoice
                            )
                          }
                        >
                          {t('common.edit')}
                        </button>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}


      {isModalOpen && (
        <InvoiceFormModal
          mode={modalMode}
          invoice={selectedInvoice}
          shipmentParts={
            availableShipmentParts
          }
          onClose={closeModal}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  )
}


export default Invoices