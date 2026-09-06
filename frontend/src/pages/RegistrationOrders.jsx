import { useEffect, useState } from 'react'

import {
  hasPermission,
} from '../utils/permissions'

import RegistrationOrderFormModal from '../components/RegistrationOrderFormModal'

import {
  createRegistrationOrder,
  deleteRegistrationOrder,
  exportRegistrationOrders,
  getRegistrationOrders,
  updateRegistrationOrder,
} from '../services/api'


function RegistrationOrders({
  user,
}) {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState(null)

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  const [currencyFilter, setCurrencyFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [ordering, setOrdering] = useState('-created_at')

  const [isExporting, setIsExporting] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
    }, 350)

    return () => {
      clearTimeout(timer)
    }
  }, [search])

  useEffect(() => {
    let isMounted = true

    async function fetchOrders() {
      try {
        setLoading(true)
        setError('')

        const data = await getRegistrationOrders({
          search: debouncedSearch,
          currency: currencyFilter,
          isActive: statusFilter,
          ordering,
        })

        if (!isMounted) {
          return
        }

        setOrders(data)
      } catch (err) {
        if (isMounted) {
          setError(err.message)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchOrders()

    return () => {
      isMounted = false
    }
  }, [
    debouncedSearch,
    currencyFilter,
    statusFilter,
    ordering,
  ])

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
        await createRegistrationOrder(
          formData
        )

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
      await deleteRegistrationOrder(
        order.id
      )

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

  async function handleExportOrders() {
    try {
      setIsExporting(true)

      await exportRegistrationOrders({
        search: debouncedSearch,
        currency: currencyFilter,
        isActive: statusFilter,
        ordering,
      })
    } catch (err) {
      window.alert(err.message)
    } finally {
      setIsExporting(false)
    }
  }

  const formatAmount = (value) => {
    return Number(value).toLocaleString(
      'en-US'
    )
  }

  const canAddOrder = hasPermission(
    user,
    'trade_orders.add_registrationorder'
  )

  const canEditOrder = hasPermission(
    user,
    'trade_orders.change_registrationorder'
  )

  const canDeleteOrder = hasPermission(
    user,
    'trade_orders.delete_registrationorder'
  )

  const canManageOrders =
    canEditOrder || canDeleteOrder

  if (
    loading &&
    orders.length === 0
  ) {
    return (
      <div className="orders-page">
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>
            Loading registration orders
          </h2>

          <p>
            Fetching trade registration
            orders.
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

          <h2>
            Unable to load registration
            orders
          </h2>

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
          <h1>
            Registration Orders
          </h1>

          <p>
            Manage registered trade orders
            and their currency allocations.
          </p>
        </div>

        <div className="orders-header-actions">

          <button
            type="button"
            className="table-action-button"
            onClick={handleExportOrders}
            disabled={isExporting}
          >
            {
              isExporting
                ? 'Exporting...'
                : 'Export CSV'
            }
          </button>

          {canAddOrder && (
            <button
              type="button"
              className="primary-button"
              onClick={
                handleOpenCreateModal
              }
            >
              Add Order
            </button>
          )}

        </div>
      </header>

      <div className="orders-filters">

        <div className="orders-search">
          <input
            type="search"
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder={
              'Search order, company, national ID or currency...'
            }
            aria-label={
              'Search registration orders'
            }
          />
        </div>

        <select
          value={currencyFilter}
          onChange={(event) =>
            setCurrencyFilter(
              event.target.value
            )
          }
          aria-label={
            'Filter by currency'
          }
        >
          <option value="">
            All Currencies
          </option>

          <option value="USD">
            USD
          </option>

          <option value="EUR">
            EUR
          </option>

          <option value="GBP">
            GBP
          </option>

          <option value="AED">
            AED
          </option>
        </select>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(
              event.target.value
            )
          }
          aria-label={
            'Filter by status'
          }
        >
          <option value="">
            All Statuses
          </option>

          <option value="true">
            Active
          </option>

          <option value="false">
            Inactive
          </option>
        </select>

        <select
          value={ordering}
          onChange={(event) =>
            setOrdering(
              event.target.value
            )
          }
          aria-label={
            'Sort registration orders'
          }
        >
          <option value="-created_at">
            Newest First
          </option>

          <option value="created_at">
            Oldest First
          </option>

          <option value="-registered_amount">
            Amount: High to Low
          </option>

          <option value="registered_amount">
            Amount: Low to High
          </option>

          <option value="order_number">
            Order Number: A-Z
          </option>

          <option value="-order_number">
            Order Number: Z-A
          </option>
        </select>

      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          No registration orders match
          the current search or filters.
        </div>
      ) : (
        <div className="orders-table-wrapper">

          <table className="orders-table">

            <thead>
              <tr>
                <th>
                  Order Number
                </th>

                <th>
                  Company
                </th>

                <th>
                  Registered Amount
                </th>

                <th>
                  Currency
                </th>

                <th>
                  Status
                </th>

                {canManageOrders && (
                  <th>
                    Actions
                  </th>
                )}
              </tr>
            </thead>

            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>

                  <td>
                    {order.order_number}
                  </td>

                  <td>
                    {
                      order.company_name ||
                      order.company
                    }
                  </td>

                  <td>
                    {formatAmount(
                      order.registered_amount
                    )}
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
                      {
                        order.is_active
                          ? 'Active'
                          : 'Inactive'
                      }
                    </span>
                  </td>

                  {canManageOrders && (
                    <td>
                      <div className="table-actions">

                        {canEditOrder && (
                          <button
                            type="button"
                            className="table-action-button"
                            onClick={() =>
                              handleOpenEditModal(
                                order
                              )
                            }
                          >
                            Edit
                          </button>
                        )}

                        {canDeleteOrder && (
                          <button
                            type="button"
                            className="table-delete-button"
                            onClick={() =>
                              handleDeleteOrder(
                                order
                              )
                            }
                          >
                            Delete
                          </button>
                        )}

                      </div>
                    </td>
                  )}

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