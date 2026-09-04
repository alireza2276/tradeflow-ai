import {
  useEffect,
  useState,
} from 'react'

import InvoiceFormModal from '../components/InvoiceFormModal'

import {
  createInvoice,
  getInvoices,
  getShipmentParts,
  updateInvoice,
} from '../services/api'

import {
  hasPermission,
} from '../utils/permissions'


function Invoices({ user }) {
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
            'Failed to load invoice data.'
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
  }, [canAddInvoice])

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
        Loading invoices...
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
          <h1>Invoices</h1>

          <p>
            Manage shipment invoices and
            financial document values.
          </p>
        </div>

        {canAddInvoice && (
          <button
            type="button"
            className="primary-button"
            onClick={openCreateModal}
          >
            Add Invoice
          </button>
        )}
      </div>

      {invoices.length === 0 ? (
        <div className="empty-state">
          No invoices found.
        </div>
      ) : (
        <div className="invoices-table-wrapper">
          <table className="invoices-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Order</th>
                <th>FOB</th>
                <th>Freight</th>
                <th>Total</th>
                <th>Currency</th>
                <th>Submission Date</th>
                <th>Actions</th>
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
                      {invoice.fob_amount}
                    </td>

                    <td>
                      {invoice.freight_amount}
                    </td>

                    <td>
                      {invoice.total_amount}
                    </td>

                    <td>
                      <span className="table-currency">
                        {invoice.order_currency}
                      </span>
                    </td>

                    <td>
                      {invoice.submission_date_dual ||
                        invoice.submission_date}
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
                          Edit
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
