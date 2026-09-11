import {
  lazy,
  Suspense,
} from 'react'
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import AppLayout from './components/AppLayout'


const DashboardPage = lazy(
  () => import(
    './pages/DashboardPage'
  ),
)

const DividendsPage = lazy(
  () => import(
    './pages/DividendsPage'
  ),
)

const ImportPage = lazy(
  () => import(
    './pages/ImportPage'
  ),
)

const InvestmentsPage = lazy(
  () => import(
    './pages/InvestmentsPage'
  ),
)

const MonthlyInvestmentPlanPage = lazy(
  () => import(
    './pages/MonthlyInvestmentPlanPage'
  ),
)

const PortfolioTargetsPage = lazy(
  () => import(
    './pages/PortfolioTargetsPage'
  ),
)

const RealEstatePage = lazy(
  () => import(
    './pages/RealEstatePage'
  ),
)

const TransactionsPage = lazy(
  () => import(
    './pages/TransactionsPage'
  ),
)


function PageLoadingState() {
  return (
    <main>
      <div className="loading-state">
        <h1>
          Loading
        </h1>

        <p>
          Loading page...
        </p>
      </div>
    </main>
  )
}


function App() {
  return (
    <BrowserRouter>
      <Suspense
        fallback={
          <PageLoadingState />
        }
      >
        <Routes>
          <Route element={<AppLayout />}>
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
              element={<DashboardPage />}
            />

            <Route
              path="/monthly-plan"
              element={
                <MonthlyInvestmentPlanPage />
              }
            />

            <Route
              path="/investments"
              element={<InvestmentsPage />}
            />

            <Route
              path="/transactions"
              element={<TransactionsPage />}
            />

            <Route
              path="/dividends"
              element={<DividendsPage />}
            />

            <Route
              path="/portfolio-targets"
              element={
                <PortfolioTargetsPage />
              }
            />

            <Route
              path="/real-estate"
              element={<RealEstatePage />}
            />

            <Route
              path="/import"
              element={<ImportPage />}
            />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}


export default App