import {
  useEffect,
  useState,
} from 'react'

import {
  getRealEstateProperties,
  getRealEstateSummary,
} from '../api/realEstate'
import type {
  RealEstateProperty,
  RealEstateSummary,
} from '../types/realEstate'


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


function RealEstatePage() {
  const [
    properties,
    setProperties,
  ] = useState<
    RealEstateProperty[]
  >([])

  const [
    summary,
    setSummary,
  ] = useState<
    RealEstateSummary | null
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
    async function loadRealEstate() {
      try {
        const [
          propertyData,
          summaryData,
        ] = await Promise.all([
          getRealEstateProperties(),
          getRealEstateSummary(),
        ])

        setProperties(
          propertyData,
        )

        setSummary(
          summaryData,
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
            'Failed to load real estate.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadRealEstate()
  }, [])


  if (loading) {
    return (
      <div className="loading-state">
        <h1>
          Real estate
        </h1>

        <p>
          Loading real estate...
        </p>
      </div>
    )
  }


  if (
    error !== null
    || summary === null
  ) {
    return (
      <div className="error-state">
        <h1>
          Real estate
        </h1>

        <p>
          {
            error
            ?? 'No real estate data available.'
          }
        </p>
      </div>
    )
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Real estate
          </h1>

          <p>
            Property, mortgage and
            rental overview
          </p>
        </div>

        <div className="base-currency-badge">
          Base currency:{' '}
          {summary.currency}
        </div>
      </section>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Property value
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                summary
                  .total_current_value,
                summary.currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            {
              summary
                .properties_count
            } properties
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Mortgage balance
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                summary
                  .total_loan_balance,
                summary.currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Outstanding debt
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
                  summary.total_equity,
                )
              }`
            }
          >
            {
              formatCurrency(
                summary.total_equity,
                summary.currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Value minus mortgage
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Monthly rent
          </div>

          <div className="kpi-value">
            {
              formatCurrency(
                summary
                  .total_monthly_rent,
                summary.currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Gross rental income
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Monthly cash flow
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  summary
                    .total_monthly_cash_flow,
                )
              }`
            }
          >
            {
              formatCurrency(
                summary
                  .total_monthly_cash_flow,
                summary.currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            After mortgage and expenses
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Annual cash flow
          </div>

          <div
            className={
              `kpi-value ${
                getValueClass(
                  summary
                    .total_annual_cash_flow,
                )
              }`
            }
          >
            {
              formatCurrency(
                summary
                  .total_annual_cash_flow,
                summary.currency,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Net cash flow per year
          </div>
        </article>
      </section>


      {
        properties.length === 0
          ? (
              <section className="panel">
                <div className="empty-state">
                  <h3>
                    No properties
                  </h3>

                  <p>
                    Add your first real
                    estate property.
                  </p>
                </div>
              </section>
            )
          : properties.map(
              (
                property,
              ) => (
                <section
                  className="panel"
                  key={property.id}
                >
                  <div className="panel-header">
                    <div>
                      <h3 className="panel-title">
                        {property.name}
                      </h3>

                      <p className="panel-subtitle">
                        {
                          property.address
                          ?? property.property_type
                        }
                      </p>
                    </div>

                    <div className="base-currency-badge">
                      {
                        property.currency
                      }
                    </div>
                  </div>


                  <section className="kpi-grid">
                    <article className="kpi-card">
                      <div className="kpi-label">
                        Current value
                      </div>

                      <div className="kpi-value">
                        {
                          formatCurrency(
                            property.current_value,
                            property.currency,
                          )
                        }
                      </div>

                      <div className="kpi-subvalue">
                        Purchase price:{' '}
                        {
                          formatCurrency(
                            property.purchase_price,
                            property.currency,
                          )
                        }
                      </div>
                    </article>


                    <article className="kpi-card">
                      <div className="kpi-label">
                        Equity
                      </div>

                      <div
                        className={
                          `kpi-value ${
                            getValueClass(
                              property.equity,
                            )
                          }`
                        }
                      >
                        {
                          formatCurrency(
                            property.equity,
                            property.currency,
                          )
                        }
                      </div>

                      <div className="kpi-subvalue">
                        Down payment:{' '}
                        {
                          formatCurrency(
                            property.down_payment,
                            property.currency,
                          )
                        }
                      </div>
                    </article>


                    <article className="kpi-card">
                      <div className="kpi-label">
                        Mortgage
                      </div>

                      <div className="kpi-value">
                        {
                          formatCurrency(
                            property.loan_balance,
                            property.currency,
                          )
                        }
                      </div>

                      <div className="kpi-subvalue">
                        LTV:{' '}
                        {
                          formatPercent(
                            property.loan_to_value,
                          )
                        }
                      </div>
                    </article>


                    <article className="kpi-card">
                      <div className="kpi-label">
                        Interest rate
                      </div>

                      <div className="kpi-value">
                        {
                          property.interest_rate
                          !== null
                            ? formatPercent(
                                property
                                  .interest_rate,
                              )
                            : '\u2014'
                        }
                      </div>

                      <div className="kpi-subvalue">
                        Monthly payment:{' '}
                        {
                          formatCurrency(
                            property.monthly_payment,
                            property.currency,
                          )
                        }
                      </div>
                    </article>


                    <article className="kpi-card">
                      <div className="kpi-label">
                        Gross yield
                      </div>

                      <div className="kpi-value">
                        {
                          formatPercent(
                            property
                              .gross_rental_yield,
                          )
                        }
                      </div>

                      <div className="kpi-subvalue">
                        Annual rent divided
                        by value
                      </div>
                    </article>


                    <article className="kpi-card">
                      <div className="kpi-label">
                        Net yield
                      </div>

                      <div className="kpi-value">
                        {
                          formatPercent(
                            property
                              .net_rental_yield,
                          )
                        }
                      </div>

                      <div className="kpi-subvalue">
                        After property expenses
                      </div>
                    </article>
                  </section>


                  <div className="table-scroll">
                    <table className="positions-table">
                      <thead>
                        <tr>
                          <th>
                            Metric
                          </th>

                          <th className="number">
                            Monthly
                          </th>

                          <th className="number">
                            Annual
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        <tr>
                          <td>
                            Rental income
                          </td>

                          <td className="number positive">
                            {
                              formatCurrency(
                                property.monthly_rent,
                                property.currency,
                              )
                            }
                          </td>

                          <td className="number positive">
                            {
                              formatCurrency(
                                property.annual_rent,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>

                        <tr>
                          <td>
                            Mortgage payments
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .monthly_payment,
                                property.currency,
                              )
                            }
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .annual_loan_payments,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>

                        <tr>
                          <td>
                            Property expenses
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .monthly_expenses,
                                property.currency,
                              )
                            }
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .annual_expenses,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>

                        <tr>
                          <td>
                            Net cash flow
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  property
                                    .monthly_cash_flow,
                                )
                              }`
                            }
                          >
                            {
                              formatCurrency(
                                property
                                  .monthly_cash_flow,
                                property.currency,
                              )
                            }
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  property
                                    .annual_cash_flow,
                                )
                              }`
                            }
                          >
                            {
                              formatCurrency(
                                property
                                  .annual_cash_flow,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </section>
              ),
            )
      }
    </main>
  )
}


export default RealEstatePage