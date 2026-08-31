import {
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  login,
} from '../services/api'


function Login({ onLogin }) {
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setIsSubmitting(true)

    try {
      const data = await login(
        username,
        password
      )

      onLogin(data.user)

      navigate(
        '/',
        {
          replace: true,
        }
      )

    } catch (loginError) {
      setError(
        loginError.message ||
        'Login failed.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <h1>TradeFlowAI</h1>

          <p>
            Trade Finance Management System
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              disabled={isSubmitting}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              disabled={isSubmitting}
              required
            />
          </div>

          {error && (
            <div
              className="form-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={isSubmitting}
          >
            {
              isSubmitting
                ? 'Signing in...'
                : 'Sign in'
            }
          </button>
        </form>
      </div>
    </div>
  )
}


export default Login
