import {
  BrowserRouter,
  Route,
  Routes,
} from 'react-router-dom'

import './App.css'
import DashboardLayout from './layouts/DashboardLayout'
import Companies from './pages/Companies'
import Dashboard from './pages/Dashboard'
import RegistrationOrders from './pages/RegistrationOrders'


function App() {
  return (
    <BrowserRouter>
      <DashboardLayout>
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
    </BrowserRouter>
  )
}

export default App