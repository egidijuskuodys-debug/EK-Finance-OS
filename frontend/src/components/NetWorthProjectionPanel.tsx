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
  getNetWorthProjection,
} from '../api/netWorthProjection'
import type {
  NetWorthProjection,
} from '../types/netWorthProjection'


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


function formatCompactNumber(
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


function NetWorthProjectionPanel() {
  const [
    projection,
    setProjection,
  ] = useState<
    NetWorthProjection | null
  >(null)

  const [
    monthlyContribution,
    setMonthlyContribution,
  ] = useState('1000')

  const [
    annualReturn,
    setAnnualReturn,
  ] = useState('7')

  const [
    propertyGrowth,
    setPropertyGrowth,
  ] = useState('2')

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
    contribution: number,
    returnPercent: number,
    growthPercent: number,
  ) {
    setLoading(true)
    setError(null)

    try {
      const data = (
        await getNetWorthProjection(
          contribution,
          returnPercent,
          growthPercent,
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
      1000,
      7,
      2,
    )
  }, [])


  function calculateProjection(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const contribution = Number(
      monthlyContribution,
    )

    const returnPercent = Number(
      annualReturn,
    )

    const growthPercent = Number(
      propertyGrowth,
    )

    if (
      !Number.isFinite(contribution)
      || contribution < 0
      || !Number.isFinite(returnPercent)
      || returnPercent <= -100
      || returnPercent > 100
      || !Number.isFinite(growthPercent)
      || growthPercent <= -100
      || growthPercent > 100
    ) {
      setError(
        'Enter valid projection assumptions.',
      )

      return
    }

    loadProjection(
      contribution,
      returnPercent,
      growthPercent,
    )
  }


  const milestoneYears = new Set([
    0,
    5,
    10,
    15,
  ])

  const milestonePoints = (
    projection?.yearly_projection.filter(
      (
        point,
      ) => (
        milestoneYears.has(
          point.year,
        )
      ),
    )
    ?? []
  )


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Net worth projection
          </h3>

          <p className="panel-subtitle">
            Combined investment portfolio
            and real estate equity
          </p>
        </div>
      </div>


      <form
        className="contribution-form"
        onSubmit={calculateProjection}
      >
        <label>
          Monthly investment
          <input
            type="number"
            min="0"
            step="10"
            value={monthlyContribution}
            onChange={
              (
                event,
              ) => (
                setMonthlyContribution(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          Investment return (%)
          <input
            type="number"
            min="-99"
            max="100"
            step="0.1"
            value={annualReturn}
            onChange={
              (
                event,
              ) => (
                setAnnualReturn(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          Property growth (%)
          <input
            type="number"
            min="-99"
            max="100"
            step="0.1"
            value={propertyGrowth}
            onChange={
              (
                event,
              ) => (
                setPropertyGrowth(
                  event.target.value,
                )
              )
            }
          />
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
          ? (
              <>
                <section className="kpi-grid">
                  <article className="kpi-card">
                    <div className="kpi-label">
                      Current net worth
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .starting_net_worth,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Investments plus
                      property equity
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Net worth in 15 years
                    </div>

                    <div className="kpi-value positive">
                      {
                        formatCurrency(
                          projection
                            .final_net_worth,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Combined projected value
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Investments in 15 years
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .final_investment_value,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Portfolio projection
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Property equity in 15 years
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .final_real_estate_equity,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Property value minus debt
                    </div>
                  </article>
                </section>


                <div
                  style={{
                    width: '100%',
                    height: 400,
                    marginTop: 24,
                  }}
                >
                  <ResponsiveContainer>
                    <LineChart
                      data={
                        projection
                          .yearly_projection
                      }
                      margin={{
                        top: 10,
                        right: 20,
                        bottom: 5,
                        left: 25,
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
                        width={75}
                        tickFormatter={
                          formatCompactNumber
                        }
                      />

                      <Tooltip />

                      <Legend />

                      <Line
                        type="monotone"
                        dataKey="net_worth"
                        name="Net worth"
                        stroke="#16a34a"
                        strokeWidth={4}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="investment_value"
                        name="Investments"
                        stroke="#2563eb"
                        strokeWidth={3}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="real_estate_equity"
                        name="Property equity"
                        stroke="#f59e0b"
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
                          Investments
                        </th>

                        <th className="number">
                          Property equity
                        </th>

                        <th className="number">
                          Net worth
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
                                      .investment_value,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .real_estate_equity,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td className="number positive">
                                {
                                  formatCurrency(
                                    point.net_worth,
                                    projection.currency,
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


export default NetWorthProjectionPanel