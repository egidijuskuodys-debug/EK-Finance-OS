import { useEffect, useMemo, useState } from 'react'

import { getDividends } from '../api/dividends'
import { getInvestments } from '../api/investments'
import type { Dividend } from '../types/dividend'
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


function DividendsPage() {
  const [
    dividends,
    setDividends,
  ] = useState<Dividend[]>([])

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
          dividendData,
          investmentData,
        ] = await Promise.all([
          getDividends(),
          getInvestments(),
        ])

        setDividends(
          dividendData,
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
            'Failed to load dividends.',
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


  const totalGrossUsd = useMemo(
    () => (
      dividends
        .filter(
          (
            dividend,
          ) => (
            dividend.currency
            === 'USD'
          ),
        )
        .reduce(
          (
            total,
            dividend,
          ) => (
            total
            + dividend.gross_amount
          ),
          0,
        )
    ),
    [dividends],
  )


  const totalNetUsd = useMemo(
    () => (
      dividends
        .filter(
          (
            dividend,
          ) => (
            dividend.currency
            === 'USD'
          ),
        )
        .reduce(
          (
            total,
            dividend,
          ) => (
            total
            + dividend.net_amount
          ),
          0,
        )
    ),
    [dividends],
  )


  const totalTaxUsd = useMemo(
    () => (
      dividends
        .filter(
          (
            dividend,
          ) => (
            dividend.currency
            === 'USD'
          ),
        )
        .reduce(
          (
            total,
            dividend,
          ) => (
            total
            + dividend.tax_amount
          ),
          0,
        )
    ),
    [dividends],
  )


  if (loading) {
    return (
      <main>
        <div className="loading-state">
          <h1>
            Dividends
          </h1>

          <p>
            Loading dividends...
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
            Dividends
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
            Dividends
          </h1>

          <p>
            Dividend income and payment history
          </p>
        </div>

        <div className="base-currency-badge">
          {
            dividends.length
          } payments
        </div>
      </section>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Dividend payments
          </div>

          <div className="kpi-value">
            {
              dividends.length
            }
          </div>

          <div className="kpi-subvalue">
            Imported payments
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Gross income
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                totalGrossUsd,
                'USD',
              )
            }
          </div>

          <div className="kpi-subvalue">
            Gross USD dividends
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Taxes
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                totalTaxUsd,
                'USD',
              )
            }
          </div>

          <div className="kpi-subvalue">
            Withholding tax
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Net income
          </div>

          <div className="kpi-value positive">
            {
              formatCurrency(
                totalNetUsd,
                'USD',
              )
            }
          </div>

          <div className="kpi-subvalue">
            Net USD dividends
          </div>
        </article>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">
              Dividend history
            </h3>

            <p className="panel-subtitle">
              Most recent payments first
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

                <th className="number">
                  Gross
                </th>

                <th className="number">
                  Tax
                </th>

                <th className="number">
                  Net
                </th>

                <th>
                  Notes
                </th>
              </tr>
            </thead>


            <tbody>
              {
                dividends.map(
                  (
                    dividend,
                  ) => {
                    const investment = (
                      investmentLookup.get(
                        dividend
                          .investment_id,
                      )
                    )

                    const ticker = (
                      investment?.ticker
                      ?? `#${dividend.investment_id}`
                    )

                    return (
                      <tr
                        key={
                          dividend.id
                        }
                      >
                        <td>
                          {
                            formatDate(
                              dividend
                                .payment_date,
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

                        <td className="number">
                          {
                            formatCurrency(
                              dividend
                                .gross_amount,
                              dividend
                                .currency,
                            )
                          }
                        </td>

                        <td className="number">
                          {
                            formatCurrency(
                              dividend
                                .tax_amount,
                              dividend
                                .currency,
                            )
                          }
                        </td>

                        <td className="number positive">
                          {
                            formatCurrency(
                              dividend
                                .net_amount,
                              dividend
                                .currency,
                            )
                          }
                        </td>

                        <td>
                          {
                            dividend.notes
                            ?? '—'
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


export default DividendsPage