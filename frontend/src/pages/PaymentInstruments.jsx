import {
  useEffect,
  useState,
} from 'react'

import PaymentInstrumentFormModal
  from '../components/PaymentInstrumentFormModal'

import {
  createPaymentInstrument,
  getPaymentInstruments,
  getRegistrationOrders,
  updatePaymentInstrument,
} from '../services/api'

import {
  hasPermission,
} from '../utils/permissions'


function PaymentInstruments({ user }) {
  const [
    paymentInstruments,
    setPaymentInstruments,
  ] = useState([])

  const [
    registrationOrders,
    setRegistrationOrders,
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
    selectedPaymentInstrument,
    setSelectedPaymentInstrument,
  ] = useState(null)

  const canAddPaymentInstrument =
    hasPermission(
      user,
      'trade_orders.add_paymentinstrument'
    )

  const canChangePaymentInstrument =
    hasPermission(
      user,
      'trade_orders.change_paymentinstrument'
    )

  useEffect(() => {
    let isMounted = true

    async function fetchData() {
      try {
        const instruments =
          await getPaymentInstruments()

        if (!isMounted) {
          return
        }

        setPaymentInstruments(instruments)

        if (canAddPaymentInstrument) {
          const orders =
            await getRegistrationOrders()

          if (!isMounted) {
            return
          }

          setRegistrationOrders(orders)
        } else {
          setRegistrationOrders([])
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError.message ||
            'Failed to load payment instruments.'
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
  }, [canAddPaymentInstrument])

  function openCreateModal() {
    setSelectedPaymentInstrument(null)
    setModalMode('create')
    setIsModalOpen(true)
  }

  function openEditModal(paymentInstrument) {
    setSelectedPaymentInstrument(
      paymentInstrument
    )
    setModalMode('edit')
    setIsModalOpen(true)
  }

  function closeModal() {
    setIsModalOpen(false)
    setSelectedPaymentInstrument(null)
  }

  async function handleSubmit(payload) {
    let savedPaymentInstrument

    if (modalMode === 'create') {
      savedPaymentInstrument =
        await createPaymentInstrument(
          payload
        )

      setPaymentInstruments(
        (currentItems) => [
          savedPaymentInstrument,
          ...currentItems,
        ]
      )
    } else {
      savedPaymentInstrument =
        await updatePaymentInstrument(
          selectedPaymentInstrument.id,
          payload
        )

      setPaymentInstruments(
        (currentItems) =>
          currentItems.map(
            (item) =>
              item.id ===
              savedPaymentInstrument.id
                ? savedPaymentInstrument
                : item
          )
      )
    }

    closeModal()
  }

  const availableRegistrationOrders =
    registrationOrders.filter(
      (order) =>
        !paymentInstruments.some(
          (instrument) =>
            instrument.registration_order ===
            order.id
        )
    )

  if (loading) {
    return (
      <div className="loading-state">
        Loading payment instruments...
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
    <div className="payment-instruments-page">
      <div className="payment-instruments-header">
        <div>
          <h1>Payment Instruments</h1>

          <p>
            Manage payment instrument numbers
            linked to registration orders.
          </p>
        </div>

        {canAddPaymentInstrument && (
          <button
            type="button"
            className="primary-button"
            onClick={openCreateModal}
          >
            Add Payment Instrument
          </button>
        )}
      </div>

      {paymentInstruments.length === 0 ? (
        <div className="empty-state">
          No payment instruments found.
        </div>
      ) : (
        <div className="payment-instruments-table-wrapper">
          <table className="payment-instruments-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Order</th>
                <th>Instrument Number</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {paymentInstruments.map(
                (instrument) => (
                  <tr key={instrument.id}>
                    <td>
                      {instrument.company_name}
                    </td>

                    <td>
                      {instrument.order_number}
                    </td>

                    <td>
                      {instrument.instrument_number}
                    </td>

                    <td>
                      {canChangePaymentInstrument ? (
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() =>
                            openEditModal(
                              instrument
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
        <PaymentInstrumentFormModal
          mode={modalMode}
          paymentInstrument={
            selectedPaymentInstrument
          }
          registrationOrders={
            availableRegistrationOrders
          }
          onClose={closeModal}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  )
}


export default PaymentInstruments