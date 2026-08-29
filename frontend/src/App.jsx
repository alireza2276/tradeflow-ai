import {
  BrowserRouter,
  Route,
  Routes,
} from 'react-router-dom'

import './App.css'
import DashboardLayout from './layouts/DashboardLayout'
import Companies from './pages/Companies'
import Dashboard from './pages/Dashboard'


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

        </Routes>
      </DashboardLayout>
    </BrowserRouter>
  )
}

export default App