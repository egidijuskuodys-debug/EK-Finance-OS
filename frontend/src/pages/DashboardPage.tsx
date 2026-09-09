import {
  useEffect,
  useState,
} from 'react'

import { getDashboard } from '../api/dashboard'
import PortfolioActionsPanel from '../components/PortfolioActionsPanel'
import PortfolioHealthPanel from '../components/PortfolioHealthPanel'
import PortfolioHistoryChart from '../components/PortfolioHistoryChart'
import PortfolioInsightsPanel from '../components/PortfolioInsightsPanel'
import PortfolioPerformancePanel from '../components/PortfolioPerformancePanel'
import PortfolioRiskPanel from '../components/PortfolioRiskPanel'
import type { DashboardData } from '../types/dashboard'


function formatCurrency(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat(
    'lt-LT',
    {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  ).format(value)
}


function formatPercent(
  value: number,
) {
  return `${value.toFixed(2)}%`
}


function getValueClass(
  value: number,
) {
  if (value > 0) {
    return 'positive'
  }

  if (value < 0) {
    return 'negative'
  }

  return ''
}


function DashboardPage() {
  const [
    dashboard,
    setDashboard,
  ] = useState<
    DashboardData | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)


  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await getDashboard()

        setDashboard(data)
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load dashboard.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [])


  if (loading) {
    return (
      <div className="loading-state">
        <h1>EK Finance OS</h1>

        <p>
          Loading dashboard...
        </p>
      </div>
    )
  }


  if (error) {
    return (
      <div className="error-state">
        <h1>EK Finance OS</h1>

        <p>{error}</p>
      </div>
    )
  }


  if (dashboard === null) {
    return (
      <div className="empty-state">
        <h1>EK Finance OS</h1>

        <p>
          No dashboard data available.
        </p>
      </div>
    )
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Dashboard
          </h1>

          <p>
            Complete personal finance overview
          </p>
        </div>

        <div className="base-currency-badge">
          Base currency:{' '}
          {dashboard.base_currency}
        </div>
      </section>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Net worth
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.net_worth,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard.net_worth,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Investments plus property equity
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Investment wealth
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                dashboard.total_wealth,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            {
              dashboard.total_positions
            } positions including cash
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Property equity
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard
                    .real_estate_equity,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard
                  .real_estate_equity,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Property value minus mortgage
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Securities
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                dashboard.securities_value,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Current market value
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Cash
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.cash_balance,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard.cash_balance,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Broker cash balance
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Net contributions
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                dashboard.net_contributions,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Deposits minus withdrawals
          </div>
        </article>
      </section>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Investment gain
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.investment_gain,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard.investment_gain,
                dashboard.base_currency,
              )
            }
          </div>

          <div
            className={
              `kpi-subvalue ${
                getValueClass(
                  dashboard
                    .investment_gain_percent,
                )
              }`
            }
          >
            {
              formatPercent(
                dashboard
                  .investment_gain_percent,
              )
            }
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            XIRR
          </div>

          <div
            className={
              `kpi-value ${
                dashboard.xirr !== null
                  ? getValueClass(
                      dashboard.xirr,
                    )
                  : ''
              }`
            }
          >
            {
              dashboard.xirr !== null
                ? formatPercent(
                    dashboard.xirr,
                  )
                : '\u2014'
            }
          </div>

          <div className="kpi-subvalue">
            Annualized money-weighted return
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Total invested
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                dashboard.total_invested,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Total acquisition cost
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Total profit
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.total_profit,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard.total_profit,
                dashboard.base_currency,
              )
            }
          </div>

          <div
            className={
              `kpi-subvalue ${
                getValueClass(
                  dashboard
                    .total_return_percent,
                )
              }`
            }
          >
            {
              formatPercent(
                dashboard.total_return_percent,
              )
            }
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Unrealized profit
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard
                    .unrealized_profit,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard
                  .unrealized_profit,
                dashboard.base_currency,
              )
            }
          </div>

          <div
            className={
              `kpi-subvalue ${
                getValueClass(
                  dashboard
                    .unrealized_profit_percent,
                )
              }`
            }
          >
            {
              formatPercent(
                dashboard
                  .unrealized_profit_percent,
              )
            }
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Realized profit
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.realized_profit,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard.realized_profit,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Profit from completed sales
          </div>
        </article>
      </section>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Property value
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                dashboard.real_estate_value,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Current real estate value
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Mortgage balance
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                dashboard
                  .real_estate_loan_balance,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Outstanding property debt
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Rental cash flow
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard
                    .monthly_rental_cash_flow,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard
                  .monthly_rental_cash_flow,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Monthly after mortgage and expenses
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Net dividends
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.dividend_net,
                )
              }`
            }
          >
            {
              formatCurrency(
                dashboard.dividend_net,
                dashboard.base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Dividends after tax
          </div>
        </article>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">
              Portfolio market value
            </h3>

            <p className="panel-subtitle">
              Historical securities
              market value in EUR
            </p>
          </div>
        </div>

        <PortfolioHistoryChart
          currency={
            dashboard.base_currency
          }
        />
      </section>


      <section className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Top positions
              </h3>

              <p className="panel-subtitle">
                Largest positions by
                current EUR value
              </p>
            </div>
          </div>

          <div className="table-scroll">
            <table className="positions-table">
              <thead>
                <tr>
                  <th>Ticker</th>

                  <th>Type</th>

                  <th className="number">
                    Value
                  </th>

                  <th className="number">
                    P/L
                  </th>

                  <th className="number">
                    Return
                  </th>
                </tr>
              </thead>

              <tbody>
                {
                  dashboard
                    .top_positions
                    .map(
                      (
                        position,
                        index,
                      ) => (
                        <tr
                          key={
                            `${position.ticker}-${index}`
                          }
                        >
                          <td>
                            <span className="ticker">
                              {
                                position.ticker
                              }
                            </span>
                          </td>

                          <td>
                            <span className="asset-type">
                              {
                                position.asset_type
                              }
                            </span>
                          </td>

                          <td className="number">
                            {
                              formatCurrency(
                                position.current_value,
                                dashboard.base_currency,
                              )
                            }
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  position.profit_loss,
                                )
                              }`
                            }
                          >
                            {
                              formatCurrency(
                                position.profit_loss,
                                dashboard.base_currency,
                              )
                            }
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  position
                                    .profit_loss_percent,
                                )
                              }`
                            }
                          >
                            {
                              formatPercent(
                                position
                                  .profit_loss_percent,
                              )
                            }
                          </td>
                        </tr>
                      ),
                    )
                }
              </tbody>
            </table>
          </div>
        </div>


        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Asset allocation
              </h3>

              <p className="panel-subtitle">
                Investment portfolio
                by asset type
              </p>
            </div>
          </div>

          <div className="allocation-list">
            {
              dashboard
                .asset_allocation
                .map(
                  (
                    item,
                  ) => (
                    <div
                      className="allocation-row"
                      key={item.name}
                    >
                      <div className="allocation-name">
                        {item.name}
                      </div>

                      <div className="allocation-track">
                        <div
                          className="allocation-fill"
                          style={{
                            width:
                              `${item.percentage}%`,
                          }}
                        />
                      </div>

                      <div className="allocation-percentage">
                        {
                          formatPercent(
                            item.percentage,
                          )
                        }
                      </div>
                    </div>
                  ),
                )
            }
          </div>


          <h3>
            Portfolio leaders
          </h3>

          <p>
            Best position:{' '}
            <strong>
              {
                dashboard.best_position
                ?? '\u2014'
              }
            </strong>
          </p>

          <p>
            Worst position:{' '}
            <strong>
              {
                dashboard.worst_position
                ?? '\u2014'
              }
            </strong>
          </p>
        </div>
      </section>


      <PortfolioHealthPanel />


      <PortfolioActionsPanel />


      <PortfolioInsightsPanel />


      <PortfolioPerformancePanel />


      <PortfolioRiskPanel />
    </main>
  )
}


export default DashboardPage