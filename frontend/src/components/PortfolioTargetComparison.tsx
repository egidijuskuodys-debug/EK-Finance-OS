import { useEffect, useMemo, useState } from 'react'

import {
  getPortfolioAllocation,
} from '../api/allocation'
import type {
  PortfolioAllocation,
} from '../api/allocation'
import type {
  PortfolioTarget,
} from '../types/portfolioTarget'


interface Props {
  targets: PortfolioTarget[]
}


function currentPercentage(
  allocation: PortfolioAllocation,
  target: PortfolioTarget,
) {
  if (target.dimension === 'asset_type') {
    return allocation.by_asset_type.find(
      (item) => (
        item.asset_type.toLowerCase()
        === target.target_key.toLowerCase()
      ),
    )?.percentage ?? 0
  }

  return allocation.by_broker.find(
    (item) => (
      item.broker.toLowerCase()
      === target.target_key.toLowerCase()
    ),
  )?.percentage ?? 0
}


function PortfolioTargetComparison({
  targets,
}: Props) {
  const [allocation, setAllocation] = (
    useState<PortfolioAllocation | null>(null)
  )

  const [error, setError] = (
    useState<string | null>(null)
  )


  useEffect(() => {
    async function loadAllocation() {
      try {
        setAllocation(
          await getPortfolioAllocation(),
        )
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Failed to load current allocation.',
        )
      }
    }

    void loadAllocation()
  }, [])


  const rows = useMemo(() => {
    if (!allocation) {
      return []
    }

    return targets.map((target) => {
      const current = currentPercentage(
        allocation,
        target,
      )

      return {
        ...target,
        current,
        difference: current - target.target_percentage,
      }
    })
  }, [allocation, targets])


  if (error) {
    return (
      <section className="panel">
        <div className="target-error">
          {error}
        </div>
      </section>
    )
  }


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Current vs target
          </h3>

          <p className="panel-subtitle">
            Positive deviation means overweight
          </p>
        </div>
      </div>

      <div className="table-scroll">
        <table className="positions-table">
          <thead>
            <tr>
              <th>Dimension</th>
              <th>Target</th>
              <th className="number">Current</th>
              <th className="number">Goal</th>
              <th className="number">Deviation</th>
            </tr>
          </thead>

          <tbody>
            {!allocation ? (
              <tr>
                <td
                  colSpan={5}
                  className="target-empty"
                >
                  Loading current allocation...
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="target-empty"
                >
                  Add targets to see the comparison.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.id}>
                  <td>
                    {
                      row.dimension === 'asset_type'
                        ? 'Asset type'
                        : 'Broker'
                    }
                  </td>

                  <td>
                    <span className="ticker">
                      {row.target_key}
                    </span>
                  </td>

                  <td className="number">
                    {row.current.toFixed(1)}%
                  </td>

                  <td className="number">
                    {row.target_percentage.toFixed(1)}%
                  </td>

                  <td
                    className={
                      `number target-deviation ${
                        Math.abs(row.difference) < 0.1
                          ? 'on-target'
                          : row.difference > 0
                            ? 'overweight'
                            : 'underweight'
                      }`
                    }
                  >
                    {
                      row.difference > 0
                        ? '+'
                        : ''
                    }
                    {row.difference.toFixed(1)} pp
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}


export default PortfolioTargetComparison
