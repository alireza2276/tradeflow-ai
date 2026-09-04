import './App.css'

import {
  useEffect,
  useState,
} from 'react'

import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import PermissionRoute from './components/PermissionRoute'
import ProtectedRoute from './components/ProtectedRoute'

import DashboardLayout from './layouts/DashboardLayout'

import Companies from './pages/Companies'
import CurrencyPurchases from './pages/CurrencyPurchases'
import Dashboard from './pages/Dashboard'
import Forbidden from './pages/Forbidden'
import Login from './pages/Login'
import RegistrationOrders from './pages/RegistrationOrders'
import ShipmentParts from './pages/ShipmentParts'

import {
  getCurrentUser,
} from './services/api'

import Invoices from './pages/Invoices'


function App() {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function restoreSession() {
      try {
        const data = await getCurrentUser()

        setUser(data.user)
      } catch {
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    restoreSession()
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            user ? (
              <Navigate
                to="/"
                replace
              />
            ) : (
              <Login
                onLogin={setUser}
              />
            )
          }
        />

        <Route
          element={
            <ProtectedRoute
              isAuthenticated={Boolean(user)}
              isLoading={isLoading}
            />
          }
        >
          <Route
            path="*"
            element={
              <DashboardLayout
                user={user}
                onLogout={() => setUser(null)}
              >
                <Routes>
                  <Route
                    path="/forbidden"
                    element={
                      <Forbidden
                        user={user}
                      />
                    }
                  />

                  <Route
                    element={
                      <PermissionRoute
                        user={user}
                        permissions={[
                          'trade_orders.view_registrationorder',
                          'trade_orders.view_currencypurchase',
                        ]}
                      />
                    }
                  >
                    <Route
                      path="/"
                      element={<Dashboard />}
                    />
                  </Route>

                  <Route
                    element={
                      <PermissionRoute
                        user={user}
                        permission="companies.view_company"
                      />
                    }
                  >
                    <Route
                      path="/companies"
                      element={
                        <Companies
                          user={user}
                        />
                      }
                    />
                  </Route>

                  <Route
                    element={
                      <PermissionRoute
                        user={user}
                        permission="trade_orders.view_registrationorder"
                      />
                    }
                  >
                    <Route
                      path="/registration-orders"
                      element={
                        <RegistrationOrders
                          user={user}
                        />
                      }
                    />
                  </Route>

                  <Route
                    element={
                      <PermissionRoute
                        user={user}
                        permission="trade_orders.view_currencypurchase"
                      />
                    }
                  >
                    <Route
                      path="/currency-purchases"
                      element={
                        <CurrencyPurchases
                          user={user}
                        />
                      }
                    />
                  </Route>

                  <Route
                    element={
                      <PermissionRoute
                        user={user}
                        permission="trade_orders.view_shipmentpart"
                      />
                    }
                  >
                    <Route
                      path="/shipment-parts"
                      element={
                        <ShipmentParts
                          user={user}
                        />
                      }
                    />
                  </Route>

                  <Route
                      element={
                        <PermissionRoute
                          user={user}
                          permission="documents.view_invoice"
                        />
                      }
                    >
                      <Route
                        path="/invoices"
                        element={
                          <Invoices
                            user={user}
                          />
                        }
                      />
                  </Route>

                </Routes>
              </DashboardLayout>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}


export default App