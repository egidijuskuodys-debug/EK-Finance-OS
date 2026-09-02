import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import AppLayout from './components/AppLayout'
import DashboardPage from './pages/DashboardPage'
import DividendsPage from './pages/DividendsPage'
import ImportPage from './pages/ImportPage'
import InvestmentsPage from './pages/InvestmentsPage'
import TransactionsPage from './pages/TransactionsPage'


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <AppLayout />
          }
        >
          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="/dashboard"
            element={
              <DashboardPage />
            }
          />

          <Route
            path="/investments"
            element={
              <InvestmentsPage />
            }
          />

          <Route
            path="/transactions"
            element={
              <TransactionsPage />
            }
          />

          <Route
            path="/dividends"
            element={
              <DividendsPage />
            }
          />

          <Route
            path="/import"
            element={
              <ImportPage />
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}


export default App