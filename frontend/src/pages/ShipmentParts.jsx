import {
  useEffect,
  useState,
} from 'react'

import { useTranslation } from 'react-i18next'

import ShipmentPartFormModal
  from '../components/ShipmentPartFormModal'

import {
  createShipmentPart,
  getCurrencyPurchases,
  getShipmentParts,
  updateShipmentPart,
} from '../services/api'

import {
  hasPermission,
} from '../utils/permissions'


function ShipmentParts({
  user,
}) {
  const { t } = useTranslation()

  const [shipmentParts, setShipmentParts] = useState([])
  const [currencyPurchases, setCurrencyPurchases] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [modalMode, setModalMode] = useState('create')
  const [selectedShipmentPart, setSelectedShipmentPart] =
    useState(null)


  const canAddShipmentPart = hasPermission(
    user,
    'trade_orders.add_shipmentpart'
  )

  const canEditShipmentPart = hasPermission(
    user,
    'trade_orders.change_shipmentpart'
  )


  async function loadData() {
    const shipmentData = await getShipmentParts()

    setShipmentParts(shipmentData)

    if (canAddShipmentPart) {
      const purchaseData =
        await getCurrencyPurchases()

      setCurrencyPurchases(purchaseData)
    } else {
      setCurrencyPurchases([])
    }
  }


  useEffect(() => {
    let isMounted = true

    async function fetchData() {
      try {
        const shipmentData =
          await getShipmentParts()

        if (!isMounted) {
          return
        }

        setShipmentParts(shipmentData)

        if (canAddShipmentPart) {
          const purchaseData =
            await getCurrencyPurchases()

          if (!isMounted) {
            return
          }

          setCurrencyPurchases(purchaseData)
        } else {
          setCurrencyPurchases([])
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError.message ||
            t('shipmentParts.loadError')
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
  }, [canAddShipmentPart, t])


  function openCreateModal() {
    setModalMode('create')
    setSelectedShipmentPart(null)
    setIsModalOpen(true)
  }


  function openEditModal(shipmentPart) {
    setModalMode('edit')
    setSelectedShipmentPart(shipmentPart)
    setIsModalOpen(true)
  }


  function closeModal() {
    setIsModalOpen(false)
    setSelectedShipmentPart(null)
  }


  async function handleSubmit(payload) {
    if (modalMode === 'create') {
      await createShipmentPart(payload)
    } else {
      await updateShipmentPart(
        selectedShipmentPart.id,
        payload
      )
    }

    closeModal()
    await loadData()
  }


  if (loading) {
    return (
      <div className="page-loading">
        {t('shipmentParts.loading')}
      </div>
    )
  }


  return (
    <div className="shipments-page">
      <div className="shipments-header">
        <div>
          <h1>
            {t('shipmentParts.title')}
          </h1>

          <p>
            {t('shipmentParts.description')}
          </p>
        </div>

        {canAddShipmentPart && (
          <button
            type="button"
            className="primary-button"
            onClick={openCreateModal}
          >
            {t('shipmentParts.addShipmentPart')}
          </button>
        )}
      </div>


      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      <div className="shipments-table-wrapper">
        <table className="shipments-table">
          <thead>
            <tr>
              <th>
                {t('shipmentParts.company')}
              </th>

              <th>
                {t('shipmentParts.orderNumber')}
              </th>

              <th>
                {t('shipmentParts.reference')}
              </th>

              <th>
                {t('shipmentParts.amount')}
              </th>

              <th>
                {t('shipmentParts.currency')}
              </th>

              <th>
                {t('shipmentParts.shipmentDate')}
              </th>

              <th>
                {t('shipmentParts.receivedDate')}
              </th>

              <th>
                {t('shipmentParts.notes')}
              </th>

              {canEditShipmentPart && (
                <th>
                  {t('shipmentParts.actions')}
                </th>
              )}
            </tr>
          </thead>

          <tbody>
            {shipmentParts.length === 0 ? (
              <tr>
                <td
                  colSpan={
                    canEditShipmentPart
                      ? 9
                      : 8
                  }
                  className="empty-state"
                >
                  {t('shipmentParts.empty')}
                </td>
              </tr>
            ) : (
              shipmentParts.map((shipmentPart) => (
                <tr key={shipmentPart.id}>
                  <td>
                    {shipmentPart.company_name || '-'}
                  </td>

                  <td>
                    {shipmentPart.order_number || '-'}
                  </td>

                  <td>
                    <span className="shipment-reference">
                      {shipmentPart.reference_number || '-'}
                    </span>
                  </td>

                  <td>
                    <span className="shipment-amount">
                      {Number(
                        shipmentPart.amount
                      ).toLocaleString(
                        'en-US',
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }
                      )}
                    </span>
                  </td>

                  <td>
                    <span className="table-currency">
                      {shipmentPart.purchase_currency || '-'}
                    </span>
                  </td>

                  <td>
                    <span className="shipment-date">
                      {shipmentPart.shipment_date || '-'}
                    </span>
                  </td>

                  <td>
                    <span className="shipment-date">
                      {shipmentPart.received_date || '-'}
                    </span>
                  </td>

                  <td>
                    <span
                      className="shipment-notes"
                      title={shipmentPart.notes || ''}
                    >
                      {shipmentPart.notes || '-'}
                    </span>
                  </td>

                  {canEditShipmentPart && (
                    <td>
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          openEditModal(shipmentPart)
                        }
                      >
                        {t('common.edit')}
                      </button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>


      {isModalOpen && (
        <ShipmentPartFormModal
          isOpen={isModalOpen}
          mode={modalMode}
          shipmentPart={selectedShipmentPart}
          currencyPurchases={currencyPurchases}
          onClose={closeModal}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  )
}


export default ShipmentParts