import {
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getRealEstateProjection,
} from '../api/realEstate'
import type {
  RealEstateProjection,
} from '../types/realEstate'


interface RealEstateProjectionPanelProps {
  propertyId: number
  propertyName: string
  currency: string
}


function formatCurrency(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat(
    'lt-LT',
    {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    },
  ).format(value)
}


function formatCompactCurrency(
  value: number,
) {
  return new Intl.NumberFormat(
    'lt-LT',
    {
      notation: 'compact',
      maximumFractionDigits: 1,
    },
  ).format(value)
}


function RealEstateProjectionPanel({
  propertyId,
  propertyName,
  currency,
}: RealEstateProjectionPanelProps) {
  const [
    projection,
    setProjection,
  ] = useState<
    RealEstateProjection | null
  >(null)

  const [
    annualGrowth,
    setAnnualGrowth,
  ] = useState('2')

  const [
    projectionYears,
    setProjectionYears,
  ] = useState('20')

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


  async function loadProjection(
    growth: number,
    years: number,
  ) {
    setLoading(true)
    setError(null)

    try {
      const data = (
        await getRealEstateProjection(
          propertyId,
          growth,
          years,
        )
      )

      setProjection(data)
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setError(
          error.message,
        )
      } else {
        setError(
          'Failed to load projection.',
        )
      }
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadProjection(
      2,
      20,
    )
  }, [propertyId])


  function calculateProjection(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const growth = Number(
      annualGrowth,
    )

    const years = Number(
      projectionYears,
    )

    if (
      !Number.isFinite(growth)
      || growth <= -100
      || growth > 100
      || !Number.isInteger(years)
      || years < 1
      || years > 40
    ) {
      setError(
        'Enter valid projection assumptions.',
      )

      return
    }

    loadProjection(
      growth,
      years,
    )
  }


  const milestoneYears = new Set([
    0,
    5,
    10,
    15,
    20,
    25,
    30,
    35,
    40,
  ])

  const milestonePoints = (
    projection?.points.filter(
      (
        point,
      ) => (
        milestoneYears.has(
          point.year,
        )
        || point.year
        === projection.projection_years
      ),
    )
    ?? []
  )

  const finalPoint = (
    projection?.points[
      projection.points.length - 1
    ]
    ?? null
  )


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Property equity projection
          </h3>

          <p className="panel-subtitle">
            {propertyName}: property value,
            mortgage balance and equity
          </p>
        </div>
      </div>


      <form
        className="contribution-form"
        onSubmit={calculateProjection}
      >
        <label>
          Annual property growth (%)
          <input
            type="number"
            min="-99"
            max="100"
            step="0.1"
            value={annualGrowth}
            onChange={
              (
                event,
              ) => (
                setAnnualGrowth(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          Projection period
          <select
            value={projectionYears}
            onChange={
              (
                event,
              ) => (
                setProjectionYears(
                  event.target.value,
                )
              )
            }
          >
            <option value="5">
              5 years
            </option>

            <option value="10">
              10 years
            </option>

            <option value="15">
              15 years
            </option>

            <option value="20">
              20 years
            </option>

            <option value="30">
              30 years
            </option>

            <option value="40">
              40 years
            </option>
          </select>
        </label>

        <button
          className="target-primary-button"
          type="submit"
          disabled={loading}
        >
          {
            loading
              ? 'Calculating...'
              : 'Calculate projection'
          }
        </button>
      </form>


      {
        error
          ? (
              <p className="negative">
                {error}
              </p>
            )
          : null
      }


      {
        projection !== null
        && finalPoint !== null
          ? (
              <>
                <section className="kpi-grid">
                  <article className="kpi-card">
                    <div className="kpi-label">
                      Final property value
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          finalPoint
                            .property_value,
                          currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      {
                        projection
                          .annual_property_growth
                      }% annual growth
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Final mortgage balance
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          finalPoint
                            .loan_balance,
                          currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Loan end:{' '}
                      {
                        projection.loan_end_date
                        ?? '\u2014'
                      }
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Final property equity
                    </div>

                    <div className="kpi-value positive">
                      {
                        formatCurrency(
                          finalPoint.equity,
                          currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Value minus mortgage
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Projected interest
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .total_interest_paid,
                          currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Assuming unchanged rate
                    </div>
                  </article>
                </section>


                <div
                  style={{
                    width: '100%',
                    height: 380,
                    marginTop: 24,
                  }}
                >
                  <ResponsiveContainer>
                    <LineChart
                      data={projection.points}
                      margin={{
                        top: 10,
                        right: 20,
                        bottom: 5,
                        left: 10,
                      }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis
                        dataKey="year"
                        tickFormatter={
                          (
                            value,
                          ) => `${value} y.`
                        }
                      />

                      <YAxis
                        tickFormatter={
                          formatCompactCurrency
                        }
                      />

                      <Tooltip />

                      <Legend />

                      <Line
                        type="monotone"
                        dataKey="property_value"
                        name="Property value"
                        stroke="#2563eb"
                        strokeWidth={3}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="equity"
                        name="Property equity"
                        stroke="#16a34a"
                        strokeWidth={3}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="loan_balance"
                        name="Mortgage balance"
                        stroke="#dc2626"
                        strokeWidth={3}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>


                <div className="table-scroll">
                  <table className="positions-table">
                    <thead>
                      <tr>
                        <th>
                          Period
                        </th>

                        <th className="number">
                          Property value
                        </th>

                        <th className="number">
                          Mortgage
                        </th>

                        <th className="number">
                          Equity
                        </th>

                        <th className="number">
                          Interest paid
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {
                        milestonePoints.map(
                          (
                            point,
                          ) => (
                            <tr key={point.year}>
                              <td>
                                {
                                  point.year
                                  === 0
                                    ? 'Today'
                                    : `${point.year} years`
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .property_value,
                                    currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .loan_balance,
                                    currency,
                                  )
                                }
                              </td>

                              <td className="number positive">
                                {
                                  formatCurrency(
                                    point.equity,
                                    currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .interest_paid,
                                    currency,
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
              </>
            )
          : null
      }
    </section>
  )
}


export default RealEstateProjectionPanel