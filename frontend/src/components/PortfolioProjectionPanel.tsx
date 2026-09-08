import {
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getPortfolioProjection,
} from '../api/projection'
import type {
  PortfolioProjection,
} from '../types/projection'


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


function PortfolioProjectionPanel() {
  const [
    monthlyContribution,
    setMonthlyContribution,
  ] = useState('1000')

  const [
    annualReturn,
    setAnnualReturn,
  ] = useState('7')

  const [
    assumptions,
    setAssumptions,
  ] = useState({
    monthlyContribution: 1000,
    annualReturn: 7,
  })

  const [
    data,
    setData,
  ] = useState<
    PortfolioProjection | null
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
    let active = true

    async function loadProjection() {
      try {
        setLoading(true)
        setError(null)

        const result = (
          await getPortfolioProjection(
            assumptions.monthlyContribution,
            assumptions.annualReturn,
          )
        )

        if (active) {
          setData(result)
        }
      } catch (loadError) {
        if (active) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Failed to load portfolio projection.',
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadProjection()

    return () => {
      active = false
    }
  }, [assumptions])


  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const contribution = Number(
      monthlyContribution,
    )
    const returnPercent = Number(
      annualReturn,
    )

    if (
      Number.isNaN(contribution)
      || contribution < 0
    ) {
      setError(
        'Monthly contribution cannot be negative.',
      )
      return
    }

    if (
      Number.isNaN(returnPercent)
      || returnPercent <= -100
      || returnPercent > 100
    ) {
      setError(
        'Annual return must be greater than -100% and no more than 100%.',
      )
      return
    }

    setAssumptions({
      monthlyContribution: contribution,
      annualReturn: returnPercent,
    })
  }


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Portfolio growth projection
          </h3>

          <p className="panel-subtitle">
            Estimate future portfolio value using monthly
            contributions and an assumed annual return
          </p>
        </div>
      </div>

      <form
        className="contribution-form"
        onSubmit={handleSubmit}
      >
        <label>
          Monthly contribution
          <input
            type="number"
            value={monthlyContribution}
            onChange={
              (event) => (
                setMonthlyContribution(
                  event.target.value,
                )
              )
            }
            min="0"
            step="0.01"
            required
          />
        </label>

        <label>
          Annual return (%)
          <input
            type="number"
            value={annualReturn}
            onChange={
              (event) => (
                setAnnualReturn(
                  event.target.value,
                )
              )
            }
            min="-99.99"
            max="100"
            step="0.1"
            required
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

      {error && (
        <div
          className="target-error"
          role="alert"
        >
          {error}
        </div>
      )}

      {data && !error && (
        <>
          <div className="contribution-summary">
            <div>
              <span>Current portfolio</span>
              <strong>
                {formatCurrency(
                  data.starting_value,
                  data.currency,
                )}
              </strong>
            </div>

            <div>
              <span>Monthly contribution</span>
              <strong>
                {formatCurrency(
                  data.monthly_contribution,
                  data.currency,
                )}
              </strong>
            </div>
          </div>

          <div
            style={{
              width: '100%',
              height: 360,
              marginTop: 24,
            }}
          >
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <AreaChart
                data={data.yearly_projection}
                margin={{
                  top: 10,
                  right: 10,
                  left: 10,
                  bottom: 0,
                }}
              >
                <defs>
                  <linearGradient
                    id="projectionValueGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="currentColor"
                      stopOpacity={0.25}
                    />

                    <stop
                      offset="95%"
                      stopColor="currentColor"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

                <XAxis
                  dataKey="year"
                  tickFormatter={
                    (year: number) => (
                      `${year} y.`
                    )
                  }
                />

                <YAxis
                  tickFormatter={
                    (value: number) => (
                      formatCurrency(
                        value,
                        data.currency,
                      )
                    )
                  }
                  width={90}
                />

                <Tooltip
                  labelFormatter={
                    (year) => (
                      `After ${year} years`
                    )
                  }
                  formatter={
                    (value) => [
                      formatCurrency(
                        Number(value),
                        data.currency,
                      ),
                      'Portfolio value',
                    ]
                  }
                />

                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="currentColor"
                  fill={
                    'url(#projectionValueGradient)'
                  }
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 4,
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div
            className="table-scroll"
            style={{
              marginTop: 24,
            }}
          >
            <table className="positions-table">
              <thead>
                <tr>
                  <th>Period</th>

                  <th className="number">
                    Portfolio value
                  </th>

                  <th className="number">
                    Total invested
                  </th>

                  <th className="number">
                    Investment growth
                  </th>
                </tr>
              </thead>

              <tbody>
                {data.milestones.map(
                  (milestone) => (
                    <tr key={milestone.years}>
                      <td>
                        <span className="ticker">
                          {milestone.years} years
                        </span>
                      </td>

                      <td className="number">
                        <strong>
                          {formatCurrency(
                            milestone.projected_value,
                            data.currency,
                          )}
                        </strong>
                      </td>

                      <td className="number">
                        {formatCurrency(
                          milestone.total_contributions,
                          data.currency,
                        )}
                      </td>

                      <td className="number">
                        <strong className="rebalance-positive">
                          {formatCurrency(
                            milestone.investment_growth,
                            data.currency,
                          )}
                        </strong>
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  )
}


export default PortfolioProjectionPanel