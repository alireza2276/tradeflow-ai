import { useEffect, useState } from 'react'

import CompanyFormModal from '../components/CompanyFormModal'
import {
  createCompany,
  getCompanies,
} from '../services/api'


function Companies() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    async function loadCompanies() {
      try {
        const data = await getCompanies()
        setCompanies(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadCompanies()
  }, [])

  async function handleCreateCompany(formData) {
    const newCompany = await createCompany(formData)

    setCompanies((currentCompanies) => [
      ...currentCompanies,
      newCompany,
    ])

    setIsModalOpen(false)
  }

  if (loading) {
    return (
      <div className="companies-page">
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>Loading companies</h2>

          <p>
            Fetching company records from TradeFlowAI.
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="companies-page">
        <div className="page-state page-state--error">
          <div className="error-icon">
            !
          </div>

          <h2>Unable to load companies</h2>

          <p>
            {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="companies-page">

      <header className="companies-header">
        <div>
          <h1>Companies</h1>

          <p>
            Manage companies involved in trade finance operations.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => setIsModalOpen(true)}
        >
          Add Company
        </button>
      </header>

      {companies.length === 0 ? (
        <div className="empty-state">
          No companies have been registered yet.
        </div>
      ) : (
        <div className="companies-table-wrapper">
          <table className="companies-table">

            <thead>
              <tr>
                <th>Company</th>
                <th>National ID</th>
                <th>Type</th>
              </tr>
            </thead>

            <tbody>
              {companies.map((company) => (
                <tr key={company.id}>
                  <td>
                    {company.name}
                  </td>

                  <td>
                    {company.national_id}
                  </td>

                  <td>
                    {company.company_type}
                  </td>
                </tr>
              ))}
            </tbody>

          </table>
        </div>
      )}

      {isModalOpen && (
        <CompanyFormModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateCompany}
        />
      )}

    </div>
  )
}

export default Companies