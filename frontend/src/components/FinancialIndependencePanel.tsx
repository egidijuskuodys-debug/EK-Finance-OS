import {
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'

import {
  getFinancialIndependence,
} from '../api/financialIndependence'
import type {
  FinancialIndependence,
} from '../types/financialIndependence'


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


function formatPercent(
  value: number,
) {
  return `${value.toFixed(2)}%`
}


function FinancialIndependencePanel() {
  const [
    projection,
    setProjection,
  ] = useState<
    FinancialIndependence | null
  >(null)

  const [
    monthlyIncomeTarget,
    setMonthlyIncomeTarget,
  ] = useState('1000')

  const [
    withdrawalRate,
    setWithdrawalRate,
  ] = useState('4')

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
    currentAge,
    setCurrentAge,
  ] = useState('45')

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
    incomeTarget: number,
    rate: number,
    contribution: number,
    returnPercent: number,
    growthPercent: number,
    age: number,
  ) {
    setLoading(true)
    setError(null)

    try {
      const data = (
        await getFinancialIndependence(
          incomeTarget,
          rate,
          contribution,
          returnPercent,
          growthPercent,
          age,
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
          (
            'Failed to load financial '
            + 'independence projection.'
          ),
        )
      }
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadProjection(
      1000,
      4,
      1000,
      7,
      2,
      45,
    )
  }, [])


  function calculateProjection(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const incomeTarget = Number(
      monthlyIncomeTarget,
    )

    const rate = Number(
      withdrawalRate,
    )

    const contribution = Number(
      monthlyContribution,
    )

    const returnPercent = Number(
      annualReturn,
    )

    const growthPercent = Number(
      propertyGrowth,
    )

    const age = Number(
      currentAge,
    )

    if (
      !Number.isFinite(incomeTarget)
      || incomeTarget <= 0
      || !Number.isFinite(rate)
      || rate <= 0
      || rate > 100
      || !Number.isFinite(contribution)
      || contribution < 0
      || !Number.isFinite(returnPercent)
      || returnPercent <= -100
      || returnPercent > 100
      || !Number.isFinite(growthPercent)
      || growthPercent <= -100
      || growthPercent > 100
      || !Number.isInteger(age)
      || age < 0
      || age > 120
    ) {
      setError(
        'Enter valid projection assumptions.',
      )

      return
    }

    loadProjection(
      incomeTarget,
      rate,
      contribution,
      returnPercent,
      growthPercent,
      age,
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
        || point.year
        === projection.years_to_goal
      ),
    )
    ?? []
  )


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Financial independence
          </h3>

          <p className="panel-subtitle">
            Estimate when passive income
            can reach your monthly target
          </p>
        </div>
      </div>


      <form
        className="target-form"
        onSubmit={calculateProjection}
      >
        <label>
          Monthly income target
          <input
            type="number"
            min="1"
            step="50"
            value={monthlyIncomeTarget}
            onChange={
              (
                event,
              ) => (
                setMonthlyIncomeTarget(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          Withdrawal rate (%)
          <input
            type="number"
            min="0.1"
            max="100"
            step="0.1"
            value={withdrawalRate}
            onChange={
              (
                event,
              ) => (
                setWithdrawalRate(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          Monthly investment
          <input
            type="number"
            min="0"
            step="50"
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

        <label>
          Current age
          <input
            type="number"
            min="0"
            max="120"
            step="1"
            value={currentAge}
            onChange={
              (
                event,
              ) => (
                setCurrentAge(
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
              : 'Calculate FI goal'
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
                      Required capital
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .required_capital,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      {
                        formatCurrency(
                          projection
                            .monthly_income_target,
                          projection.currency,
                        )
                      } monthly target
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Current passive income
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .current_monthly_passive_income,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      At {
                        formatPercent(
                          projection
                            .withdrawal_rate_percent,
                        )
                      } withdrawal rate
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Progress
                    </div>

                    <div className="kpi-value positive">
                      {
                        formatPercent(
                          projection
                            .progress_percent,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Gap:{' '}
                      {
                        formatCurrency(
                          projection
                            .remaining_gap,
                          projection.currency,
                        )
                      }
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Estimated goal
                    </div>

                    <div className="kpi-value positive">
                      {
                        projection.years_to_goal
                        !== null
                          ? (
                              `${projection
                                .years_to_goal} years`
                            )
                          : 'Beyond projection'
                      }
                    </div>

                    <div className="kpi-subvalue">
                      {
                        projection
                          .projected_age_at_goal
                        !== null
                          ? (
                              `Age ${
                                projection
                                  .projected_age_at_goal
                              }`
                            )
                          : (
                              'Goal not reached '
                              + 'within 15 years'
                            )
                      }
                    </div>
                  </article>
                </section>


                <div className="allocation-list">
                  <div className="allocation-row">
                    <div className="allocation-name">
                      FI progress
                    </div>

                    <div className="allocation-track">
                      <div
                        className="allocation-fill"
                        style={{
                          width: (
                            `${projection
                              .progress_percent}%`
                          ),
                        }}
                      />
                    </div>

                    <div className="allocation-percentage">
                      {
                        formatPercent(
                          projection
                            .progress_percent,
                        )
                      }
                    </div>
                  </div>
                </div>


                <div className="table-scroll">
                  <table className="positions-table">
                    <thead>
                      <tr>
                        <th>
                          Period
                        </th>

                        <th className="number">
                          Net worth
                        </th>

                        <th className="number">
                          Monthly passive income
                        </th>

                        <th>
                          Status
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
                                    point.net_worth,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .monthly_passive_income,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td
                                className={
                                  point.target_reached
                                    ? 'positive'
                                    : ''
                                }
                              >
                                {
                                  point.target_reached
                                    ? 'Target reached'
                                    : 'Building wealth'
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


export default FinancialIndependencePanel