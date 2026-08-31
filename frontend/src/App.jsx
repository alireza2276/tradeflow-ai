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

import './App.css'

import ProtectedRoute from './components/ProtectedRoute'
import DashboardLayout from './layouts/DashboardLayout'
import Companies from './pages/Companies'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import RegistrationOrders from './pages/RegistrationOrders'

import {
  getCurrentUser,
} from './services/api'


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
            user
              ? (
                <Navigate
                  to="/"
                  replace
                />
              )
              : (
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
            path="/*"
            element={
              <DashboardLayout
                onLogout={() => setUser(null)}
              >
                <Routes>
                  <Route
                    path="/"
                    element={<Dashboard />}
                  />

                  <Route
                    path="/companies"
                    element={<Companies />}
                  />

                  <Route
                    path="/registration-orders"
                    element={<RegistrationOrders />}
                  />
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