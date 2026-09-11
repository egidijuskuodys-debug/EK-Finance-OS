import {
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'

import {
  getMonthlyInvestmentPlan,
} from '../api/monthlyInvestmentPlan'
import type {
  MonthlyInvestmentPlan,
} from '../types/monthlyInvestmentPlan'


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


function formatDimension(
  value: string,
) {
  if (value === 'asset_type') {
    return 'Asset type'
  }

  if (value === 'broker') {
    return 'Broker'
  }

  return value
}


function MonthlyInvestmentPlanPage() {
  const [
    monthlyAmount,
    setMonthlyAmount,
  ] = useState('1000')

  const [
    plan,
    setPlan,
  ] = useState<
    MonthlyInvestmentPlan | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  )


  async function loadPlan(
    amount: number,
  ) {
    setLoading(true)
    setError(null)

    try {
      const data = (
        await getMonthlyInvestmentPlan(
          amount,
        )
      )

      setPlan(data)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message)
      } else {
        setError(
          'Failed to load monthly plan.',
        )
      }
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadPlan(1000)
  }, [])


  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const parsedAmount = Number(
      monthlyAmount,
    )

    if (
      !Number.isFinite(parsedAmount)
      || parsedAmount <= 0
    ) {
      setError(
        'Monthly amount must be greater than zero.',
      )

      return
    }

    loadPlan(parsedAmount)
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Monthly investment plan
          </h1>

          <p>
            Monthly allocation based on
            portfolio targets, concentration
            and performance
          </p>
        </div>

        {
          plan !== null
          && (
            <div className="base-currency-badge">
              Generated {plan.generated_date}
            </div>
          )
        }
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">
              Monthly contribution
            </h3>

            <p className="panel-subtitle">
              Enter the amount available
              for investment this month
            </p>
          </div>
        </div>

        <form
          className="contribution-form"
          onSubmit={handleSubmit}
        >
          <label>
            Monthly amount

            <input
              type="number"
              min="0.01"
              step="0.01"
              value={monthlyAmount}
              onChange={
                (event) => (
                  setMonthlyAmount(
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
                : 'Calculate monthly plan'
            }
          </button>
        </form>

        {
          error !== null
          && (
            <div className="error-state">
              <p>{error}</p>
            </div>
          )
        }

        {
          plan !== null
          && (
            <div className="contribution-summary">
              <div>
                <span>
                  Monthly amount
                </span>

                <strong>
                  {
                    formatCurrency(
                      plan.monthly_amount,
                      plan.currency,
                    )
                  }
                </strong>
              </div>

              <div>
                <span>
                  Allocated now
                </span>

                <strong className="positive">
                  {
                    formatCurrency(
                      plan.allocated_amount,
                      plan.currency,
                    )
                  }
                </strong>
              </div>

              <div>
                <span>
                  Unallocated
                </span>

                <strong>
                  {
                    formatCurrency(
                      plan.unallocated_amount,
                      plan.currency,
                    )
                  }
                </strong>
              </div>

              <div>
                <span>
                  Portfolio value
                </span>

                <strong>
                  {
                    formatCurrency(
                      plan.portfolio_value,
                      plan.currency,
                    )
                  }
                </strong>
              </div>
            </div>
          )
        }
      </section>


      {
        plan !== null
        && (
          <>
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">
                    Invest now
                  </h3>

                  <p className="panel-subtitle">
                    Suggested allocation
                    by asset type
                  </p>
                </div>
              </div>

              <div className="table-scroll">
                <table className="positions-table">
                  <thead>
                    <tr>
                      <th>Target</th>
                      <th>Priority</th>

                      <th className="number">
                        Invest now
                      </th>

                      <th className="number">
                        Current
                      </th>

                      <th className="number">
                        Future share
                      </th>

                      <th className="number">
                        Goal
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {
                      plan.invest_now.map(
                        (item) => (
                          <tr key={item.target}>
                            <td>
                              <span className="ticker">
                                {item.target}
                              </span>

                              <div className="panel-subtitle">
                                {item.reason}
                              </div>
                            </td>

                            <td>
                              <span className="asset-type">
                                {item.priority}
                              </span>
                            </td>

                            <td className="number positive">
                              {
                                formatCurrency(
                                  item.amount,
                                  item.currency,
                                )
                              }
                            </td>

                            <td className="number">
                              {
                                formatPercent(
                                  item.current_percentage,
                                )
                              }
                            </td>

                            <td className="number">
                              {
                                formatPercent(
                                  item.future_percentage,
                                )
                              }
                            </td>

                            <td className="number">
                              {
                                formatPercent(
                                  item.target_percentage,
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


            <section className="panel">
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">
                    Broker routing
                  </h3>

                  <p className="panel-subtitle">
                    Broker for the same
                    monthly contribution
                  </p>
                </div>
              </div>

              <div className="table-scroll">
                <table className="positions-table">
                  <thead>
                    <tr>
                      <th>Broker</th>

                      <th className="number">
                        Route now
                      </th>

                      <th className="number">
                        Current
                      </th>

                      <th className="number">
                        Future share
                      </th>

                      <th className="number">
                        Goal
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {
                      plan.broker_routing.map(
                        (item) => (
                          <tr key={item.broker}>
                            <td>
                              <span className="ticker">
                                {item.broker}
                              </span>
                            </td>

                            <td className="number positive">
                              {
                                formatCurrency(
                                  item.amount,
                                  item.currency,
                                )
                              }
                            </td>

                            <td className="number">
                              {
                                formatPercent(
                                  item.current_percentage,
                                )
                              }
                            </td>

                            <td className="number">
                              {
                                formatPercent(
                                  item.future_percentage,
                                )
                              }
                            </td>

                            <td className="number">
                              {
                                formatPercent(
                                  item.target_percentage,
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

              <p className="panel-subtitle">
                {
                  plan.guidance
                    .asset_and_broker_note
                }
              </p>
            </section>


            <section className="panel">
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">
                    Pause new contributions
                  </h3>

                  <p className="panel-subtitle">
                    Portfolio areas currently
                    above their targets
                  </p>
                </div>
              </div>

              <div className="table-scroll">
                <table className="positions-table">
                  <thead>
                    <tr>
                      <th>View</th>
                      <th>Target</th>
                      <th>Action</th>

                      <th className="number">
                        Current
                      </th>

                      <th className="number">
                        Goal
                      </th>

                      <th className="number">
                        Above goal
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {
                      plan
                        .pause_new_contributions
                        .map(
                          (item) => (
                            <tr
                              key={
                                `${item.dimension}-${item.target}`
                              }
                            >
                              <td>
                                {
                                  formatDimension(
                                    item.dimension,
                                  )
                                }
                              </td>

                              <td>
                                <span className="ticker">
                                  {item.target}
                                </span>
                              </td>

                              <td className="negative">
                                {item.action}
                              </td>

                              <td className="number">
                                {
                                  formatPercent(
                                    item.current_percentage,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatPercent(
                                    item.target_percentage,
                                  )
                                }
                              </td>

                              <td className="number negative">
                                {
                                  formatCurrency(
                                    item.amount_over_target,
                                    item.currency,
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


            <section className="panel">
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">
                    Review before investing
                  </h3>

                  <p className="panel-subtitle">
                    Risks and positions that
                    deserve attention
                  </p>
                </div>
              </div>

              <div className="table-scroll">
                <table className="positions-table">
                  <thead>
                    <tr>
                      <th>Priority</th>
                      <th>Category</th>
                      <th>Recommendation</th>
                      <th>Reason</th>
                    </tr>
                  </thead>

                  <tbody>
                    {
                      plan.review_items.map(
                        (
                          item,
                          index,
                        ) => (
                          <tr
                            key={
                              `${item.category}-${item.title}-${index}`
                            }
                          >
                            <td>
                              <span className="asset-type">
                                {item.priority}
                              </span>
                            </td>

                            <td>
                              {item.category}
                            </td>

                            <td>
                              <span className="ticker">
                                {item.title}
                              </span>

                              <div className="panel-subtitle">
                                {item.message}
                              </div>
                            </td>

                            <td>
                              {item.reason}
                            </td>
                          </tr>
                        ),
                      )
                    }
                  </tbody>
                </table>
              </div>

              <p className="panel-subtitle">
                {plan.guidance.sell_note}
              </p>
            </section>
          </>
        )
      }
    </main>
  )
}


export default MonthlyInvestmentPlanPage