import { useState } from 'react'

import {
  executeImportFile,
  validateImportFile,
} from '../api/import'
import type {
  ImportResult,
  ImportValidationResult,
} from '../types/import'


function ImportPage() {
  const [
    broker,
    setBroker,
  ] = useState('IBKR')

  const [
    file,
    setFile,
  ] = useState<File | null>(null)

  const [
    validation,
    setValidation,
  ] = useState<
    ImportValidationResult | null
  >(null)

  const [
    importResult,
    setImportResult,
  ] = useState<
    ImportResult | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(null)


  function resetResults() {
    setValidation(null)
    setImportResult(null)
    setError(null)
  }


  async function handleValidate() {
    if (file === null) {
      setError(
        'Please select a file first.',
      )

      return
    }

    resetResults()
    setLoading(true)

    try {
      const result = (
        await validateImportFile(
          broker,
          file,
        )
      )

      setValidation(result)
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setError(
          error.message,
        )
      } else {
        setError(
          'Validation failed.',
        )
      }
    } finally {
      setLoading(false)
    }
  }


  async function handleImport() {
    if (file === null) {
      setError(
        'Please select a file first.',
      )

      return
    }

    setError(null)
    setLoading(true)

    try {
      const result = (
        await executeImportFile(
          broker,
          file,
        )
      )

      setImportResult(result)
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setError(
          error.message,
        )
      } else {
        setError(
          'Import failed.',
        )
      }
    } finally {
      setLoading(false)
    }
  }


  const canImport = (
    validation?.ready === true
    && validation.already_imported
      === false
  )


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Import
          </h1>

          <p>
            Import investment data
            from supported brokers
          </p>
        </div>

        <div className="base-currency-badge">
          CSV import
        </div>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">
              Import statement
            </h3>

            <p className="panel-subtitle">
              Select broker and upload
              an investment statement
            </p>
          </div>
        </div>


        <div className="import-form">
          <div className="form-group">
            <label
              htmlFor="broker"
              className="form-label"
            >
              Broker
            </label>

            <select
              id="broker"
              value={broker}
              onChange={
                (
                  event,
                ) => {
                  setBroker(
                    event.target.value,
                  )

                  resetResults()
                }
              }
              className="form-control"
            >
              <option value="IBKR">
                Interactive Brokers
              </option>

              <option value="REVOLUT">
                Revolut
              </option>

              <option
                value="SEB"
                disabled
              >
                SEB — coming soon
              </option>
            </select>
          </div>


          <div className="form-group">
            <label
              htmlFor="file"
              className="form-label"
            >
              Statement file
            </label>

            <input
              id="file"
              type="file"
              accept=".csv,text/csv"
              className="form-control"
              onChange={
                (
                  event,
                ) => {
                  const selectedFile = (
                    event.target
                      .files?.[0]
                    ?? null
                  )

                  setFile(
                    selectedFile,
                  )

                  resetResults()
                }
              }
            />
          </div>


          {
            file !== null
            && (
              <div className="file-summary">
                <strong>
                  Selected file:
                </strong>{' '}
                {file.name}
              </div>
            )
          }


          <div className="form-actions">
            <button
              type="button"
              className="button secondary"
              disabled={
                loading
                || file === null
              }
              onClick={
                handleValidate
              }
            >
              {
                loading
                  ? 'Processing...'
                  : 'Validate'
              }
            </button>

            <button
              type="button"
              className="button primary"
              disabled={
                loading
                || !canImport
              }
              onClick={
                handleImport
              }
            >
              Import file
            </button>
          </div>
        </div>
      </section>


      {
        error !== null
        && (
          <section className="error-state">
            <h3>
              Import error
            </h3>

            <p>
              {error}
            </p>
          </section>
        )
      }


      {
        validation !== null
        && (
          <section className="panel import-result">
            <div className="panel-header">
              <div>
                <h3 className="panel-title">
                  Validation result
                </h3>

                <p className="panel-subtitle">
                  {
                    validation
                      .uploaded_file_name
                    ?? file?.name
                    ?? 'File'
                  }
                </p>
              </div>
            </div>

            <div className="result-grid">
              <div>
                <span className="result-label">
                  Status
                </span>

                <strong>
                  {
                    validation.ready
                      ? 'Ready'
                      : 'Not ready'
                  }
                </strong>
              </div>

              <div>
                <span className="result-label">
                  Already imported
                </span>

                <strong>
                  {
                    validation
                      .already_imported
                      ? 'Yes'
                      : 'No'
                  }
                </strong>
              </div>
            </div>

            <p>
              {
                validation.message
              }
            </p>
          </section>
        )
      }


      {
        importResult !== null
        && (
          <section className="panel import-result">
            <div className="panel-header">
              <div>
                <h3 className="panel-title">
                  Import result
                </h3>

                <p className="panel-subtitle">
                  {
                    importResult
                      .uploaded_file_name
                    ?? importResult
                      .file_name
                    ?? 'Imported file'
                  }
                </p>
              </div>
            </div>

            <div className="result-grid">
              <div>
                <span className="result-label">
                  Status
                </span>

                <strong>
                  {
                    importResult.success
                      ? 'Completed'
                      : 'Skipped'
                  }
                </strong>
              </div>

              <div>
                <span className="result-label">
                  Positions
                </span>

                <strong>
                  {
                    importResult
                      .positions_in_statement
                    ?? 0
                  }
                </strong>
              </div>

              <div>
                <span className="result-label">
                  Transactions
                </span>

                <strong>
                  {
                    importResult
                      .transactions
                      ?.imported
                    ?? 0
                  }
                </strong>
              </div>

              <div>
                <span className="result-label">
                  Dividends
                </span>

                <strong>
                  {
                    importResult
                      .dividends
                      ?.imported
                    ?? 0
                  }
                </strong>
              </div>

              <div>
                <span className="result-label">
                  Cash movements
                </span>

                <strong>
                  {
                    importResult
                      .cash_movements
                      ?.imported
                    ?? 0
                  }
                </strong>
              </div>
            </div>

            <p>
              {
                importResult.message
              }
            </p>
          </section>
        )
      }
    </main>
  )
}


export default ImportPage