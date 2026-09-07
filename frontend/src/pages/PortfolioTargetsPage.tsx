import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'

import {
  createPortfolioTarget,
  deletePortfolioTarget,
  getPortfolioTargets,
  updatePortfolioTarget,
} from '../api/portfolioTargets'
import PortfolioTargetComparison from '../components/PortfolioTargetComparison'
import type { PortfolioTarget } from '../types/portfolioTarget'


function labelDimension(value: string) {
  return value === 'asset_type'
    ? 'Asset type'
    : 'Broker'
}


function PortfolioTargetsPage() {
  const [targets, setTargets] = useState<PortfolioTarget[]>([])
  const [dimension, setDimension] = useState('asset_type')
  const [targetKey, setTargetKey] = useState('')
  const [percentage, setPercentage] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)


  async function loadTargets() {
    try {
      setError(null)
      setTargets(await getPortfolioTargets())
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : 'Failed to load portfolio targets.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadTargets()
  }, [])


  const totals = useMemo(() => {
    return targets.reduce<Record<string, number>>(
      (result, target) => {
        result[target.dimension] = (
          result[target.dimension] ?? 0
        ) + target.target_percentage

        return result
      },
      {},
    )
  }, [targets])


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const numericPercentage = Number(percentage)

    if (!targetKey.trim()) {
      setError('Enter a target name.')
      return
    }

    if (
      Number.isNaN(numericPercentage)
      || numericPercentage < 0
      || numericPercentage > 100
    ) {
      setError('Percentage must be between 0 and 100.')
      return
    }

    try {
      setSaving(true)
      setError(null)

      const created = await createPortfolioTarget({
        dimension,
        target_key: targetKey.trim(),
        target_percentage: numericPercentage,
      })

      setTargets((current) => [...current, created])
      setTargetKey('')
      setPercentage('')
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Failed to save portfolio target.',
      )
    } finally {
      setSaving(false)
    }
  }


  async function handleEdit(target: PortfolioTarget) {
    const value = window.prompt(
      `New target percentage for ${target.target_key}:`,
      String(target.target_percentage),
    )

    if (value === null) {
      return
    }

    const numericPercentage = Number(value)

    if (
      Number.isNaN(numericPercentage)
      || numericPercentage < 0
      || numericPercentage > 100
    ) {
      setError('Percentage must be between 0 and 100.')
      return
    }

    try {
      setError(null)

      const updated = await updatePortfolioTarget(
        target.id,
        {
          target_percentage: numericPercentage,
        },
      )

      setTargets((current) => current.map(
        (item) => (
          item.id === updated.id
            ? updated
            : item
        ),
      ))
    } catch (updateError) {
      setError(
        updateError instanceof Error
          ? updateError.message
          : 'Failed to update portfolio target.',
      )
    }
  }


  async function handleDelete(target: PortfolioTarget) {
    const confirmed = window.confirm(
      `Delete target "${target.target_key}"?`,
    )

    if (!confirmed) {
      return
    }

    try {
      setError(null)
      await deletePortfolioTarget(target.id)

      setTargets((current) => current.filter(
        (item) => item.id !== target.id,
      ))
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : 'Failed to delete portfolio target.',
      )
    }
  }


  if (loading) {
    return (
      <main>
        <div className="loading-state">
          <h1>Portfolio targets</h1>
          <p>Loading targets...</p>
        </div>
      </main>
    )
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>Portfolio targets</h1>
          <p>Define the allocation you want to maintain</p>
        </div>

        <div className="base-currency-badge">
          {targets.length} targets
        </div>
      </section>

      {error && (
        <div className="target-error" role="alert">
          {error}
        </div>
      )}

      <section className="target-summary-grid">
        {['asset_type', 'broker'].map((item) => {
          const total = totals[item] ?? 0
          const isComplete = Math.abs(total - 100) < 0.01

          return (
            <article className="kpi-card" key={item}>
              <div className="kpi-label">
                {labelDimension(item)} total
              </div>

              <div
                className={
                  `kpi-value ${isComplete ? 'positive' : ''}`
                }
              >
                {total.toFixed(1)}%
              </div>

              <div className="kpi-subvalue">
                {isComplete
                  ? 'Allocation is complete'
                  : `${(100 - total).toFixed(1)}% remaining`}
              </div>
            </article>
          )
        })}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">Add target</h3>
            <p className="panel-subtitle">
              Targets within each dimension should total 100%
            </p>
          </div>
        </div>

        <form className="target-form" onSubmit={handleSubmit}>
          <label>
            Dimension
            <select
              value={dimension}
              onChange={(event) => setDimension(event.target.value)}
            >
              <option value="asset_type">Asset type</option>
              <option value="broker">Broker</option>
            </select>
          </label>

          <label>
            Target
            <input
              value={targetKey}
              onChange={(event) => setTargetKey(event.target.value)}
              placeholder={
                dimension === 'asset_type'
                  ? 'ETF, Fund, Stock...'
                  : 'SEB, REVOLUT...'
              }
              maxLength={100}
              required
            />
          </label>

          <label>
            Percentage
            <input
              type="number"
              value={percentage}
              onChange={(event) => setPercentage(event.target.value)}
              min="0"
              max="100"
              step="0.1"
              placeholder="0.0"
              required
            />
          </label>

          <button
            className="target-primary-button"
            type="submit"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Add target'}
          </button>
        </form>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">Target allocation</h3>
            <p className="panel-subtitle">
              Desired allocation by asset type and broker
            </p>
          </div>
        </div>

        <div className="table-scroll">
          <table className="positions-table">
            <thead>
              <tr>
                <th>Dimension</th>
                <th>Target</th>
                <th className="number">Percentage</th>
                <th className="number">Actions</th>
              </tr>
            </thead>

            <tbody>
              {targets.length === 0 ? (
                <tr>
                  <td colSpan={4} className="target-empty">
                    No portfolio targets yet.
                  </td>
                </tr>
              ) : (
                targets.map((target) => (
                  <tr key={target.id}>
                    <td>{labelDimension(target.dimension)}</td>
                    <td>
                      <span className="ticker">
                        {target.target_key}
                      </span>
                    </td>
                    <td className="number">
                      {target.target_percentage.toFixed(1)}%
                    </td>
                    <td className="number">
                      <div className="target-actions">
                        <button
                          className="target-secondary-button"
                          type="button"
                          onClick={() => void handleEdit(target)}
                        >
                          Edit
                        </button>

                        <button
                          className="target-delete-button"
                          type="button"
                          onClick={() => void handleDelete(target)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <PortfolioTargetComparison targets={targets} />
    </main>
  )
}


export default PortfolioTargetsPage


