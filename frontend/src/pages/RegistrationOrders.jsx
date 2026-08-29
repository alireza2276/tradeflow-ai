import { useEffect, useState } from 'react'

import RegistrationOrderFormModal from '../components/RegistrationOrderFormModal'
import {
  createRegistrationOrder,
  deleteRegistrationOrder,
  getRegistrationOrders,
  updateRegistrationOrder,
} from '../services/api'


function RegistrationOrders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState(null)

  useEffect(() => {
    loadOrders()
  }, [])

  async function loadOrders() {
    try {
      setLoading(true)
      setError('')

      const data = await getRegistrationOrders()
      setOrders(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleOpenCreateModal() {
    setSelectedOrder(null)
    setIsModalOpen(true)
  }

  function handleOpenEditModal(order) {
    setSelectedOrder(order)
    setIsModalOpen(true)
  }

  function handleCloseModal() {
    setIsModalOpen(false)
    setSelectedOrder(null)
  }

  async function handleSubmitOrder(formData) {
    if (selectedOrder) {
      const updatedOrder =
        await updateRegistrationOrder(
          selectedOrder.id,
          formData
        )

      setOrders((currentOrders) =>
        currentOrders.map((order) =>
          order.id === updatedOrder.id
            ? updatedOrder
            : order
        )
      )
    } else {
      const newOrder =
        await createRegistrationOrder(formData)

      setOrders((currentOrders) => [
        ...currentOrders,
        newOrder,
      ])
    }

    handleCloseModal()
  }

  async function handleDeleteOrder(order) {
    const confirmed = window.confirm(
      `Delete registration order "${order.order_number}"?`
    )

    if (!confirmed) {
      return
    }

    try {
      await deleteRegistrationOrder(order.id)

      setOrders((currentOrders) =>
        currentOrders.filter(
          (currentOrder) =>
            currentOrder.id !== order.id
        )
      )
    } catch (err) {
      window.alert(err.message)
    }
  }

  const formatAmount = (value) => {
    return Number(value).toLocaleString('en-US')
  }

  if (loading) {
    return (
      <div className="orders-page">
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>Loading registration orders</h2>

          <p>
            Fetching trade registration orders.
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="orders-page">
        <div className="page-state page-state--error">
          <div className="error-icon">
            !
          </div>

          <h2>Unable to load registration orders</h2>

          <p>
            {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="orders-page">

      <header className="orders-header">
        <div>
          <h1>Registration Orders</h1>

          <p>
            Manage registered trade orders and their currency allocations.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={handleOpenCreateModal}
        >
          Add Order
        </button>
      </header>

      {orders.length === 0 ? (
        <div className="empty-state">
          No registration orders have been created yet.
        </div>
      ) : (
        <div className="orders-table-wrapper">
          <table className="orders-table">

            <thead>
              <tr>
                <th>Order Number</th>
                <th>Company</th>
                <th>Registered Amount</th>
                <th>Currency</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>

                  <td>
                    {order.order_number}
                  </td>

                  <td>
                    {order.company_name || order.company}
                  </td>

                  <td>
                    {formatAmount(order.registered_amount)}
                  </td>

                  <td>
                    <span className="table-currency">
                      {order.currency}
                    </span>
                  </td>

                  <td>
                    <span
                      className={
                        order.is_active
                          ? 'order-status order-status--active'
                          : 'order-status order-status--inactive'
                      }
                    >
                      {order.is_active
                        ? 'Active'
                        : 'Inactive'}
                    </span>
                  </td>

                  <td>
                    <div className="table-actions">
                      <button
                        type="button"
                        className="table-action-button"
                        onClick={() =>
                          handleOpenEditModal(order)
                        }
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="table-delete-button"
                        onClick={() =>
                          handleDeleteOrder(order)
                        }
                      >
                        Delete
                      </button>
                    </div>
                  </td>

                </tr>
              ))}
            </tbody>

          </table>
        </div>
      )}

      <RegistrationOrderFormModal
        isOpen={isModalOpen}
        order={selectedOrder}
        onClose={handleCloseModal}
        onSubmit={handleSubmitOrder}
      />

    </div>
  )
}

export default RegistrationOrders