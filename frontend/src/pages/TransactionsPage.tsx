import { useEffect, useMemo, useState } from 'react'

import { getInvestments } from '../api/investments'
import { getTransactions } from '../api/transactions'
import type { Investment } from '../types/investment'
import type { Transaction } from '../types/transaction'


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


function formatDate(
  value: string,
) {
  return new Intl.DateTimeFormat(
    'lt-LT',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    },
  ).format(
    new Date(value),
  )
}


function TransactionsPage() {
  const [
    transactions,
    setTransactions,
  ] = useState<Transaction[]>([])

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
    async function loadData() {
      try {
        const [
          transactionData,
          investmentData,
        ] = await Promise.all([
          getTransactions(),
          getInvestments(),
        ])

        setTransactions(
          transactionData,
        )

        setInvestments(
          investmentData,
        )
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load transactions.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])


  const investmentLookup = useMemo(
    () => (
      new Map(
        investments.map(
          (
            investment,
          ) => [
            investment.id,
            investment,
          ],
        ),
      )
    ),
    [investments],
  )


  const totalBuyValue = useMemo(
    () => (
      transactions.reduce(
        (
          total,
          transaction,
        ) => {
          if (
            transaction.transaction_type
            !== 'BUY'
          ) {
            return total
          }

          const investment = (
            investmentLookup.get(
              transaction.investment_id,
            )
          )

          if (
            investment?.currency
            !== 'EUR'
          ) {
            return total
          }

          return (
            total
            + (
              transaction.quantity
              * transaction.price
            )
          )
        },
        0,
      )
    ),
    [
      transactions,
      investmentLookup,
    ],
  )


  if (loading) {
    return (
      <main>
        <div className="loading-state">
          <h1>
            Transactions
          </h1>

          <p>
            Loading transactions...
          </p>
        </div>
      </main>
    )
  }


  if (error) {
    return (
      <main>
        <div className="error-state">
          <h1>
            Transactions
          </h1>

          <p>
            {error}
          </p>
        </div>
      </main>
    )
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Transactions
          </h1>

          <p>
            Complete investment transaction history
          </p>
        </div>

        <div className="base-currency-badge">
          {
            transactions.length
          } transactions
        </div>
      </section>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Transactions
          </div>

          <div className="kpi-value">
            {
              transactions.length
            }
          </div>

          <div className="kpi-subvalue">
            Imported records
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            BUY transactions
          </div>

          <div className="kpi-value">
            {
              transactions.filter(
                (
                  transaction,
                ) => (
                  transaction
                    .transaction_type
                  === 'BUY'
                ),
              ).length
            }
          </div>

          <div className="kpi-subvalue">
            Purchase transactions
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            SELL transactions
          </div>

          <div className="kpi-value">
            {
              transactions.filter(
                (
                  transaction,
                ) => (
                  transaction
                    .transaction_type
                  === 'SELL'
                ),
              ).length
            }
          </div>

          <div className="kpi-subvalue">
            Sale transactions
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            EUR buy volume
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                totalBuyValue,
                'EUR',
              )
            }
          </div>

          <div className="kpi-subvalue">
            EUR transactions only
          </div>
        </article>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">
              Transaction history
            </h3>

            <p className="panel-subtitle">
              Newest transactions first
            </p>
          </div>
        </div>


        <div className="table-scroll">
          <table className="positions-table">
            <thead>
              <tr>
                <th>
                  Date
                </th>

                <th>
                  Ticker
                </th>

                <th>
                  Type
                </th>

                <th className="number">
                  Quantity
                </th>

                <th className="number">
                  Price
                </th>

                <th className="number">
                  Value
                </th>

                <th className="number">
                  Realized P/L
                </th>
              </tr>
            </thead>


            <tbody>
              {
                transactions.map(
                  (
                    transaction,
                  ) => {
                    const investment = (
                      investmentLookup.get(
                        transaction
                          .investment_id,
                      )
                    )

                    const ticker = (
                      investment?.ticker
                      ?? `#${transaction.investment_id}`
                    )

                    const value = (
                      transaction.quantity
                      * transaction.price
                    )

                    return (
                      <tr
                        key={
                          transaction.id
                        }
                      >
                        <td>
                          {
                            formatDate(
                              transaction
                                .transaction_date,
                            )
                          }
                        </td>

                        <td>
                          <span className="ticker">
                            {
                              ticker
                            }
                          </span>
                        </td>

                        <td>
                          <span className="asset-type">
                            {
                              transaction
                                .transaction_type
                            }
                          </span>
                        </td>

                        <td className="number">
                          {
                            formatNumber(
                              transaction
                                .quantity,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              transaction
                                .price,
                              transaction
                                .currency,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              value,
                              transaction
                                .currency,
                            )
                          }
                        </td>

                        <td
                          className={
                            `number ${
                              transaction
                                .realized_profit
                              > 0
                                ? 'positive'
                                : transaction
                                    .realized_profit
                                  < 0
                                  ? 'negative'
                                  : ''
                            }`
                          }
                        >
                          {
                            formatCurrency(
                              transaction
                                .realized_profit,
                              transaction
                                .currency,
                            )
                          }
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


export default TransactionsPage