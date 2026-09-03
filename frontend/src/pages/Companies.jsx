import { useEffect, useState } from 'react'

import {
  hasPermission,
} from '../utils/permissions'

import CompanyFormModal from '../components/CompanyFormModal'
import {
  createCompany,
  deleteCompany,
  getCompanies,
  updateCompany,
} from '../services/api'


function Companies({
  user,
}) {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState(null)

  const [deletingCompanyId, setDeletingCompanyId] =
    useState(null)


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


  function handleOpenCreateModal() {
    setSelectedCompany(null)
    setIsModalOpen(true)
  }


  function handleOpenEditModal(company) {
    setSelectedCompany(company)
    setIsModalOpen(true)
  }


  function handleCloseModal() {
    setIsModalOpen(false)
    setSelectedCompany(null)
  }


  async function handleSubmitCompany(formData) {
    if (selectedCompany) {
      const updatedCompany = await updateCompany(
        selectedCompany.id,
        formData
      )

      setCompanies((currentCompanies) =>
        currentCompanies.map((company) =>
          company.id === updatedCompany.id
            ? updatedCompany
            : company
        )
      )
    } else {
      const newCompany = await createCompany(formData)

      setCompanies((currentCompanies) => [
        ...currentCompanies,
        newCompany,
      ])
    }

    handleCloseModal()
  }


  async function handleDeleteCompany(company) {
    const confirmed = window.confirm(
      `Delete "${company.name}"? This action cannot be undone.`
    )

    if (!confirmed) {
      return
    }

    try {
      setDeletingCompanyId(company.id)

      await deleteCompany(company.id)

      setCompanies((currentCompanies) =>
        currentCompanies.filter(
          (item) => item.id !== company.id
        )
      )
    } catch (err) {
      window.alert(err.message)
    } finally {
      setDeletingCompanyId(null)
    }
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

  const canEditCompany = hasPermission(
    user,
    'companies.change_company'
  )

  const canDeleteCompany = hasPermission(
    user,
    'companies.delete_company'
  )

  const canManageCompanies =
    canEditCompany || canDeleteCompany

  return (
    <div className="companies-page">

      <header className="companies-header">
        <div>
          <h1>Companies</h1>

          <p>
            Manage companies involved in trade finance operations.
          </p>
        </div>

        {hasPermission(
          user,
          'companies.add_company'
        ) && (
          <button
            type="button"
            className="primary-button"
            onClick={handleOpenCreateModal}
          >
            Add Company
          </button>
        )}

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
                {canManageCompanies && (
                  <th>Actions</th>
                )}
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
                    <span className="company-type-badge">
                      {company.company_type === 'PRODUCTION'
                        ? 'Production'
                        : 'Commercial'}
                    </span>
                  </td>

                  {canManageCompanies && (
                    <td>
                      <div className="table-actions">
                        {canEditCompany && (
                          <button
                            type="button"
                            className="table-action-button"
                            onClick={() =>
                              handleOpenEditModal(company)
                            }
                          >
                            Edit
                          </button>
                        )}

                        {canDeleteCompany && (
                          <button
                            type="button"
                            className="table-action-button table-action-button--danger"
                            onClick={() =>
                              handleDeleteCompany(company)
                            }
                            disabled={
                              deletingCompanyId === company.id
                            }
                          >
                            {deletingCompanyId === company.id
                              ? 'Deleting...'
                              : 'Delete'}
                          </button>
                        )}
                      </div>
                    </td>
                  )}

                </tr>
              ))}
            </tbody>

          </table>
        </div>
      )}


      {isModalOpen && (
        <CompanyFormModal
          company={selectedCompany}
          onClose={handleCloseModal}
          onSubmit={handleSubmitCompany}
        />
      )}

    </div>
  )
}

export default Companies