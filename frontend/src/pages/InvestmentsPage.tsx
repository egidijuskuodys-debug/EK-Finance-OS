import { useEffect, useMemo, useState } from 'react'

import { getInvestments } from '../api/investments'
import type { Investment } from '../types/investment'


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


function formatNumber(
  value: number,
) {
  return new Intl.NumberFormat(
    'lt-LT',
    {
      maximumFractionDigits: 8,
    },
  ).format(value)
}


function getProfitLoss(
  investment: Investment,
) {
  return (
    investment.quantity
    * (
      investment.current_price
      - investment.purchase_price
    )
  )
}


function getProfitLossPercent(
  investment: Investment,
) {
  const invested = (
    investment.quantity
    * investment.purchase_price
  )

  if (invested <= 0) {
    return 0
  }

  return (
    getProfitLoss(investment)
    / invested
  ) * 100
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


function InvestmentsPage() {
  const [
    investments,
    setInvestments,
  ] = useState<Investment[]>([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(null)

  useEffect(() => {
    async function loadInvestments() {
      try {
        const data = await getInvestments()

        setInvestments(data)
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message)
        } else {
          setError(
            'Failed to load investments.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadInvestments()
  }, [])


  const sortedInvestments = useMemo(
    () => (
      [...investments].sort(
        (
          first,
          second,
        ) => {
          const firstValue = (
            first.quantity
            * first.current_price
          )

          const secondValue = (
            second.quantity
            * second.current_price
          )

          return (
            secondValue
            - firstValue
          )
        },
      )
    ),
    [investments],
  )


  if (loading) {
    return (
      <main>
        <div className="loading-state">
          <h1>Investments</h1>

          <p>
            Loading investments...
          </p>
        </div>
      </main>
    )
  }


  if (error) {
    return (
      <main>
        <div className="error-state">
          <h1>Investments</h1>

          <p>{error}</p>
        </div>
      </main>
    )
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Investments
          </h1>

          <p>
            Current investment positions
            across connected brokers
          </p>
        </div>

        <div className="base-currency-badge">
          {investments.length} positions
        </div>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">
              Portfolio positions
            </h3>

            <p className="panel-subtitle">
              Purchase price, current
              value and unrealized return
            </p>
          </div>
        </div>


        <div className="table-scroll">
          <table className="positions-table">
            <thead>
              <tr>
                <th>
                  Ticker
                </th>

                <th>
                  Type
                </th>

                <th>
                  Broker
                </th>

                <th className="number">
                  Quantity
                </th>

                <th className="number">
                  Avg. cost
                </th>

                <th className="number">
                  Price
                </th>

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
                sortedInvestments.map(
                  (
                    investment,
                  ) => {
                    const currentValue = (
                      investment.quantity
                      * investment.current_price
                    )

                    const profitLoss = (
                      getProfitLoss(
                        investment,
                      )
                    )

                    const profitLossPercent = (
                      getProfitLossPercent(
                        investment,
                      )
                    )

                    return (
                      <tr
                        key={
                          investment.id
                        }
                      >
                        <td>
                          <span className="ticker">
                            {
                              investment.ticker
                            }
                          </span>
                        </td>

                        <td>
                          <span className="asset-type">
                            {
                              investment.asset_type
                            }
                          </span>
                        </td>

                        <td>
                          {
                            investment.broker
                          }
                        </td>

                        <td className="number">
                          {
                            formatNumber(
                              investment.quantity,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              investment.purchase_price,
                              investment.currency,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              investment.current_price,
                              investment.currency,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              currentValue,
                              investment.currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                profitLoss,
                              )
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              profitLoss,
                              investment.currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              getValueClass(
                                profitLossPercent,
                              )
                            }`
                          }
                        >
                          {
                            profitLossPercent.toFixed(
                              2,
                            )
                          }%
                        </td>
                      </tr>
                    )
                  },
                )
              }
            </tbody>
          </table>
        </div>
      </section>
    </main>
  )
}


export default InvestmentsPage