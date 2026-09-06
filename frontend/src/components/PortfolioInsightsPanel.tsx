import {
  useEffect,
  useState,
} from 'react'

import {
  getPortfolioInsights,
} from '../api/analytics'

import type {
  InsightPriority,
  PortfolioInsights,
} from '../api/analytics'


function getPriorityLabel(
  priority: InsightPriority,
) {
  if (priority === 'High') {
    return 'High priority'
  }

  if (priority === 'Medium') {
    return 'Medium priority'
  }

  if (priority === 'Low') {
    return 'Low priority'
  }

  return 'Info'
}


function getPriorityClass(
  priority: InsightPriority,
) {
  if (priority === 'High') {
    return 'negative'
  }

  if (priority === 'Medium') {
    return 'warning'
  }

  if (priority === 'Low') {
    return 'positive'
  }

  return ''
}


function PortfolioInsightsPanel() {
  const [
    data,
    setData,
  ] = useState<
    PortfolioInsights | null
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
    async function loadInsights() {
      try {
        const result = (
          await getPortfolioInsights()
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
            'Failed to load portfolio insights.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadInsights()
  }, [])


  if (loading) {
    return (
      <section className="panel">
        <p>
          Loading portfolio insights...
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
            Portfolio insights
          </h3>

          <p className="panel-subtitle">
            Prioritized interpretation of
            portfolio health, risk and performance
          </p>
        </div>

        <div className="base-currency-badge">
          {
            data.summary.health_score.toFixed(
              0,
            )
          }
          /100 · {
            data.summary.health_label
          }
        </div>
      </div>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Total insights
          </div>

          <div className="kpi-value">
            {
              data
                .summary
                .insights_count
            }
          </div>

          <div className="kpi-subvalue">
            Portfolio signals
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            High priority
          </div>

          <div
            className={
              `kpi-value ${
                data
                  .summary
                  .high_priority_count > 0
                  ? 'negative'
                  : ''
              }`
            }
          >
            {
              data
                .summary
                .high_priority_count
            }
          </div>

          <div className="kpi-subvalue">
            Immediate attention
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Medium priority
          </div>

          <div className="kpi-value">
            {
              data
                .summary
                .medium_priority_count
            }
          </div>

          <div className="kpi-subvalue">
            Items to monitor
          </div>
        </article>
      </section>


      <div className="table-scroll">
        <table className="positions-table">
          <thead>
            <tr>
              <th>Priority</th>
              <th>Category</th>
              <th>Insight</th>
              <th>Details</th>
            </tr>
          </thead>

          <tbody>
            {
              data.insights.map(
                (
                  insight,
                  index,
                ) => (
                  <tr
                    key={
                      `${insight.category}-${insight.title}-${index}`
                    }
                  >
                    <td>
                      <span
                        className={
                          getPriorityClass(
                            insight.priority,
                          )
                        }
                      >
                        {
                          getPriorityLabel(
                            insight.priority,
                          )
                        }
                      </span>
                    </td>

                    <td>
                      {
                        insight.category
                      }
                    </td>

                    <td>
                      <strong>
                        {
                          insight.title
                        }
                      </strong>
                    </td>

                    <td>
                      {
                        insight.message
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


export default PortfolioInsightsPanel