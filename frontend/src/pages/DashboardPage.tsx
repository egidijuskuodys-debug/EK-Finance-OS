import { useEffect, useState } from 'react'

import { getDashboard } from '../api/dashboard'
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
        const data = (
          await getDashboard()
        )

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
            Investment portfolio overview
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
            Portfolio value
          </div>

          <div className="kpi-value">
            {formatCurrency(
              dashboard.portfolio_value,
              dashboard.base_currency,
            )}
          </div>

          <div className="kpi-subvalue">
            {
              dashboard.total_positions
            } positions
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Total invested
          </div>

          <div className="kpi-value">
            {formatCurrency(
              dashboard.total_invested,
              dashboard.base_currency,
            )}
          </div>

          <div className="kpi-subvalue">
            {
              dashboard.total_quantity
            } total units
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Unrealized P/L
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  dashboard.unrealized_profit,
                )
              }`
            }
          >
            {formatCurrency(
              dashboard.unrealized_profit,
              dashboard.base_currency,
            )}
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
            {formatPercent(
              dashboard
                .unrealized_profit_percent,
            )}
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Total return
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
            {formatCurrency(
              dashboard.total_profit,
              dashboard.base_currency,
            )}
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
            {formatPercent(
              dashboard
                .total_return_percent,
            )}
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
                : '—'
            }
          </div>

          <div className="kpi-subvalue">
            Annualized return
          </div>
        </article>
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
                      ) => (
                        <tr
                          key={
                            position
                              .ticker
                          }
                        >
                          <td>
                            <span className="ticker">
                              {
                                position
                                  .ticker
                              }
                            </span>
                          </td>

                          <td>
                            <span className="asset-type">
                              {
                                position
                                  .asset_type
                              }
                            </span>
                          </td>

                          <td className="number">
                            {
                              formatCurrency(
                                position
                                  .current_value,
                                dashboard
                                  .base_currency,
                              )
                            }
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  position
                                    .profit_loss,
                                )
                              }`
                            }
                          >
                            {
                              formatCurrency(
                                position
                                  .profit_loss,
                                dashboard
                                  .base_currency,
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
                Portfolio mix by
                asset type
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
                      key={
                        item.name
                      }
                    >
                      <div className="allocation-name">
                        {
                          item.name
                        }
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
            Income
          </h3>

          <p>
            Dividends:{' '}
            <strong>
              {
                formatCurrency(
                  dashboard
                    .dividend_net,
                  dashboard
                    .base_currency,
                )
              }
            </strong>
          </p>


          <h3>
            Portfolio leaders
          </h3>

          <p>
            Best position:{' '}
            <strong>
              {
                dashboard
                  .best_position
                ?? '—'
              }
            </strong>
          </p>

          <p>
            Worst position:{' '}
            <strong>
              {
                dashboard
                  .worst_position
                ?? '—'
              }
            </strong>
          </p>
        </div>
      </section>
    </main>
  )
}


export default DashboardPage