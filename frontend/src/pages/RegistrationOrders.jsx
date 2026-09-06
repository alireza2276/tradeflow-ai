import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

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
  const { t } = useTranslation()

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
      `${t('common.delete')} "${order.order_number}"?`
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
            {t(
              'registrationOrders.loadingTitle'
            )}
          </h2>

          <p>
            {t(
              'registrationOrders.loadingDescription'
            )}
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
            {t(
              'registrationOrders.loadError'
            )}
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
            {t(
              'registrationOrders.title'
            )}
          </h1>

          <p>
            {t(
              'registrationOrders.description'
            )}
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
                ? t(
                    'registrationOrders.exporting'
                  )
                : t(
                    'common.exportCsv'
                  )
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
              {t(
                'registrationOrders.addOrder'
              )}
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
              t(
                'registrationOrders.searchPlaceholder'
              )
            }
            aria-label={
              t(
                'common.search'
              )
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
            t(
              'registrationOrders.currency'
            )
          }
        >
          <option value="">
            {t(
              'registrationOrders.allCurrencies'
            )}
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
            t(
              'registrationOrders.status'
            )
          }
        >
          <option value="">
            {t(
              'registrationOrders.allStatuses'
            )}
          </option>

          <option value="true">
            {t(
              'common.active'
            )}
          </option>

          <option value="false">
            {t(
              'common.inactive'
            )}
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
            t(
              'registrationOrders.sort'
            )
          }
        >
          <option value="-created_at">
            {t(
              'registrationOrders.newestFirst'
            )}
          </option>

          <option value="created_at">
            {t(
              'registrationOrders.oldestFirst'
            )}
          </option>

          <option value="-registered_amount">
            {t(
              'registrationOrders.amountHighToLow'
            )}
          </option>

          <option value="registered_amount">
            {t(
              'registrationOrders.amountLowToHigh'
            )}
          </option>

          <option value="order_number">
            {t(
              'registrationOrders.orderNumberAsc'
            )}
          </option>

          <option value="-order_number">
            {t(
              'registrationOrders.orderNumberDesc'
            )}
          </option>
        </select>

      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          {t(
            'registrationOrders.empty'
          )}
        </div>
      ) : (
        <div className="orders-table-wrapper">

          <table className="orders-table">

            <thead>
              <tr>
                <th>
                  {t(
                    'registrationOrders.orderNumber'
                  )}
                </th>

                <th>
                  {t(
                    'registrationOrders.company'
                  )}
                </th>

                <th>
                  {t(
                    'registrationOrders.registeredAmount'
                  )}
                </th>

                <th>
                  {t(
                    'registrationOrders.currency'
                  )}
                </th>

                <th>
                  {t(
                    'registrationOrders.status'
                  )}
                </th>

                {canManageOrders && (
                  <th>
                    {t(
                      'registrationOrders.actions'
                    )}
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
                          ? t(
                              'common.active'
                            )
                          : t(
                              'common.inactive'
                            )
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
                            {t(
                              'common.edit'
                            )}
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
                            {t(
                              'common.delete'
                            )}
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