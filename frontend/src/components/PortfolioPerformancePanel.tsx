import {
  useEffect,
  useState,
} from 'react'

import {
  getPerformanceBreakdown,
} from '../api/analytics'

import type {
  PortfolioPerformanceBreakdown,
} from '../api/analytics'


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


function PortfolioPerformancePanel() {
  const [
    data,
    setData,
  ] = useState<
    PortfolioPerformanceBreakdown | null
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
    async function loadPerformance() {
      try {
        const result = (
          await getPerformanceBreakdown()
        )

        setData(result)
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load performance breakdown.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadPerformance()
  }, [])


  if (loading) {
    return (
      <section className="panel">
        <p>
          Loading performance breakdown...
        </p>
      </section>
    )
  }


  if (
    error !== null
  ) {
    return (
      <section className="panel">
        <p className="negative">
          {error}
        </p>
      </section>
    )
  }


  if (
    data === null
  ) {
    return null
  }


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Performance breakdown
          </h3>

          <p className="panel-subtitle">
            Unrealized, realized and dividend
            contribution by position and broker
          </p>
        </div>
      </div>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Open cost basis
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                data
                  .summary
                  .open_cost_basis,
                data
                  .summary
                  .base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Remaining open positions
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Current value
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                data
                  .summary
                  .current_value,
                data
                  .summary
                  .base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Securities market value
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
                  data
                    .summary
                    .unrealized_profit,
                )
              }`
            }
          >
            {
              formatCurrency(
                data
                  .summary
                  .unrealized_profit,
                data
                  .summary
                  .base_currency,
              )
            }
          </div>

          <div
            className={
              `kpi-subvalue ${
                getValueClass(
                  data
                    .summary
                    .unrealized_return_percent,
                )
              }`
            }
          >
            {
              formatPercent(
                data
                  .summary
                  .unrealized_return_percent,
              )
            }
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Realized P/L
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  data
                    .summary
                    .realized_profit,
                )
              }`
            }
          >
            {
              formatCurrency(
                data
                  .summary
                  .realized_profit,
                data
                  .summary
                  .base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Closed and partial sales
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
                  data
                    .summary
                    .dividend_net,
                )
              }`
            }
          >
            {
              formatCurrency(
                data
                  .summary
                  .dividend_net,
                data
                  .summary
                  .base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Net dividend income
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Total P/L
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  data
                    .summary
                    .total_profit,
                )
              }`
            }
          >
            {
              formatCurrency(
                data
                  .summary
                  .total_profit,
                data
                  .summary
                  .base_currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Unrealized + realized + dividends
          </div>
        </article>
      </section>


      <section className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Broker performance
              </h3>

              <p className="panel-subtitle">
                Total profit contribution
              </p>
            </div>
          </div>

          <div className="table-scroll">
            <table className="positions-table">
              <thead>
                <tr>
                  <th>Broker</th>
                  <th className="number">
                    Current value
                  </th>
                  <th className="number">
                    Unrealized
                  </th>
                  <th className="number">
                    Realized
                  </th>
                  <th className="number">
                    Dividends
                  </th>
                  <th className="number">
                    Total P/L
                  </th>
                </tr>
              </thead>

              <tbody>
                {
                  data.by_broker.map(
                    (item) => (
                      <tr
                        key={item.broker}
                      >
                        <td>
                          {item.broker}
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              item.current_value,
                              item.base_currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                item
                                  .unrealized_profit,
                              )
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              item
                                .unrealized_profit,
                              item.base_currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                item
                                  .realized_profit,
                              )
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              item
                                .realized_profit,
                              item.base_currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                item
                                  .dividend_net,
                              )
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              item
                                .dividend_net,
                              item.base_currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                item
                                  .total_profit,
                              )
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              item
                                .total_profit,
                              item.base_currency,
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
                Asset type performance
              </h3>

              <p className="panel-subtitle">
                Profit by asset class
              </p>
            </div>
          </div>

          <div className="table-scroll">
            <table className="positions-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th className="number">
                    Current value
                  </th>
                  <th className="number">
                    Total P/L
                  </th>
                  <th className="number">
                    Open
                  </th>
                </tr>
              </thead>

              <tbody>
                {
                  data.by_asset_type.map(
                    (item) => (
                      <tr
                        key={
                          item.asset_type
                        }
                      >
                        <td>
                          <span className="asset-type">
                            {
                              item
                                .asset_type
                            }
                          </span>
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              item.current_value,
                              item.base_currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                item
                                  .total_profit,
                              )
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              item.total_profit,
                              item.base_currency,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            item.open_positions
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
      </section>


      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Position performance
          </h3>

          <p className="panel-subtitle">
            Best and worst contributors
          </p>
        </div>
      </div>


      <div className="table-scroll">
        <table className="positions-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Broker</th>
              <th>Status</th>
              <th className="number">
                Value
              </th>
              <th className="number">
                Unrealized
              </th>
              <th className="number">
                Realized
              </th>
              <th className="number">
                Dividends
              </th>
              <th className="number">
                Total P/L
              </th>
            </tr>
          </thead>

          <tbody>
            {
              data.positions.map(
                (position) => (
                  <tr
                    key={
                      position
                        .investment_id
                    }
                  >
                    <td>
                      <span className="ticker">
                        {position.ticker}
                      </span>
                    </td>

                    <td>
                      {position.broker}
                    </td>

                    <td>
                      {position.status}
                    </td>

                    <td className="number">
                      {
                        formatCurrency(
                          position
                            .current_value,
                          position
                            .base_currency,
                        )
                      }
                    </td>

                    <td
                      className={
                        `number ${
                          getValueClass(
                            position
                              .unrealized_profit,
                          )
                        }`
                      }
                    >
                      {
                        formatCurrency(
                          position
                            .unrealized_profit,
                          position
                            .base_currency,
                        )
                      }
                    </td>

                    <td
                      className={
                        `number ${
                          getValueClass(
                            position
                              .realized_profit,
                          )
                        }`
                      }
                    >
                      {
                        formatCurrency(
                          position
                            .realized_profit,
                          position
                            .base_currency,
                        )
                      }
                    </td>

                    <td
                      className={
                        `number ${
                          getValueClass(
                            position
                              .dividend_net,
                          )
                        }`
                      }
                    >
                      {
                        formatCurrency(
                          position
                            .dividend_net,
                          position
                            .base_currency,
                        )
                      }
                    </td>

                    <td
                      className={
                        `number ${
                          getValueClass(
                            position
                              .total_profit,
                          )
                        }`
                      }
                    >
                      {
                        formatCurrency(
                          position
                            .total_profit,
                          position
                            .base_currency,
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
    </section>
  )
}


export default PortfolioPerformancePanel