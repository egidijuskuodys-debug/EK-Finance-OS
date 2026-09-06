import {
  useEffect,
  useState,
} from 'react'

import {
  getPortfolioActions,
} from '../api/analytics'

import type {
  ActionPriority,
  PortfolioActions,
} from '../api/analytics'


function getPriorityLabel(
  priority: ActionPriority,
) {
  if (priority === 'High') {
    return 'High priority'
  }

  if (priority === 'Medium') {
    return 'Medium priority'
  }

  return 'Low priority'
}


function getPriorityClass(
  priority: ActionPriority,
) {
  if (priority === 'High') {
    return 'negative'
  }

  if (priority === 'Medium') {
    return 'warning'
  }

  return 'positive'
}


function PortfolioActionsPanel() {
  const [
    data,
    setData,
  ] = useState<
    PortfolioActions | null
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
    async function loadActions() {
      try {
        const result = (
          await getPortfolioActions()
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
            'Failed to load portfolio actions.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadActions()
  }, [])


  if (loading) {
    return (
      <section className="panel">
        <p>
          Loading portfolio actions...
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
            Portfolio actions
          </h3>

          <p className="panel-subtitle">
            Suggested monitoring and review
            actions based on portfolio analytics
          </p>
        </div>

        <div className="base-currency-badge">
          {
            data
              .summary
              .health_score
              .toFixed(0)
          }
          /100 · {
            data
              .summary
              .health_label
          }
        </div>
      </div>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Total actions
          </div>

          <div className="kpi-value">
            {
              data
                .summary
                .actions_count
            }
          </div>

          <div className="kpi-subvalue">
            Suggested actions
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
            Review or monitor
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Low priority
          </div>

          <div className="kpi-value">
            {
              data
                .summary
                .low_priority_count
            }
          </div>

          <div className="kpi-subvalue">
            Maintain or monitor
          </div>
        </article>
      </section>


      <div className="table-scroll">
        <table className="positions-table">
          <thead>
            <tr>
              <th>Priority</th>
              <th>Action</th>
              <th>Category</th>
              <th>Title</th>
              <th>Suggested response</th>
              <th>Reason</th>
            </tr>
          </thead>

          <tbody>
            {
              data.actions.map(
                (
                  action,
                  index,
                ) => (
                  <tr
                    key={
                      `${action.category}-${action.title}-${index}`
                    }
                  >
                    <td>
                      <span
                        className={
                          getPriorityClass(
                            action.priority,
                          )
                        }
                      >
                        {
                          getPriorityLabel(
                            action.priority,
                          )
                        }
                      </span>
                    </td>

                    <td>
                      <strong>
                        {
                          action
                            .action_type
                        }
                      </strong>
                    </td>

                    <td>
                      {
                        action.category
                      }
                    </td>

                    <td>
                      <strong>
                        {
                          action.title
                        }
                      </strong>
                    </td>

                    <td>
                      {
                        action.message
                      }
                    </td>

                    <td>
                      {
                        action.reason
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


export default PortfolioActionsPanel