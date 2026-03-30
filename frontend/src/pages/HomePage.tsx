import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeRepository, validateGitHubRepo, getAvailableTools } from '../services/api'
import type { AnalysisType } from '../types'

function HomePage() {
  const navigate = useNavigate()
  const [repoUrl, setRepoUrl] = useState('')
  const [analysisType, setAnalysisType] = useState('comprehensive')
  const [githubToken, setGithubToken] = useState('')
  const [usePrivateRepo, setUsePrivateRepo] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [validating, setValidating] = useState(false)
  const [repoInfo, setRepoInfo] = useState<any>(null)
  const [analysisTypes, setAnalysisTypes] = useState<AnalysisType[]>([])

  useEffect(() => {
    loadAnalysisTypes()
  }, [])

  const loadAnalysisTypes = async () => {
    try {
      const data = await getAvailableTools()
      setAnalysisTypes(data.analysis_types)
    } catch (err) {
      console.error('Failed to load analysis types:', err)
    }
  }

  const handleValidateRepo = async () => {
    if (!repoUrl) return

    setValidating(true)
    setError('')
    setRepoInfo(null)

    try {
      const info = await validateGitHubRepo(repoUrl, usePrivateRepo ? githubToken : undefined)
      setRepoInfo(info)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to validate repository')
    } finally {
      setValidating(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!repoUrl) {
      setError('Please enter a repository URL')
      return
    }

    if (usePrivateRepo && !githubToken) {
      setError('Please provide a GitHub token for private repositories')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await analyzeRepository({
        repo_url: repoUrl,
        analysis_type: analysisType,
        github_token: usePrivateRepo ? githubToken : undefined,
      })

      // Navigate to analysis page
      navigate(`/analysis/${response.analysis_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start analysis')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Code Analysis Agent
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Multi-step reasoning powered by LangChain + Claude
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <span className="w-2 h-2 mr-2 bg-green-400 rounded-full"></span>
                Online
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Analyze Any GitHub Repository
          </h2>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered code analysis that finds bugs, security vulnerabilities,
            and suggests improvements through multi-step reasoning
          </p>
        </div>

        {/* Analysis Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Repository URL Input */}
            <div>
              <label htmlFor="repoUrl" className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Repository URL
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="repoUrl"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/owner/repository"
                  className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  type="button"
                  onClick={handleValidateRepo}
                  disabled={!repoUrl || validating}
                  className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 disabled:opacity-50"
                >
                  {validating ? 'Validating...' : 'Validate'}
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Example: https://github.com/facebook/react
              </p>
            </div>

            {/* Repository Info Display */}
            {repoInfo && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-green-800">
                      Repository Validated
                    </h3>
                    <div className="mt-2 text-sm text-green-700">
                      <p><strong>{repoInfo.name}</strong></p>
                      <p className="text-xs mt-1">{repoInfo.description}</p>
                      <div className="mt-2 flex items-center space-x-4 text-xs">
                        <span>⭐ {repoInfo.stars} stars</span>
                        <span>📝 {repoInfo.language}</span>
                        {repoInfo.is_private && <span className="text-orange-600">🔒 Private</span>}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Private Repository Toggle */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="usePrivateRepo"
                checked={usePrivateRepo}
                onChange={(e) => setUsePrivateRepo(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="usePrivateRepo" className="ml-2 block text-sm text-gray-700">
                This is a private repository (requires authentication)
              </label>
            </div>

            {/* GitHub Token Input (shown if private repo) */}
            {usePrivateRepo && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <label htmlFor="githubToken" className="block text-sm font-medium text-gray-700 mb-2">
                  GitHub Personal Access Token
                </label>
                <input
                  type="password"
                  id="githubToken"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  className="block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-2 text-xs text-gray-600">
                  Create a token at: <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    github.com/settings/tokens
                  </a>
                  <br />
                  Required scope: <code className="bg-gray-100 px-1 rounded">repo</code>
                </p>
              </div>
            )}

            {/* Analysis Type Selection */}
            <div>
              <label htmlFor="analysisType" className="block text-sm font-medium text-gray-700 mb-2">
                Analysis Type
              </label>
              <select
                id="analysisType"
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {analysisTypes.map((type) => (
                  <option key={type.type} value={type.type}>
                    {type.type.replace('_', ' ').toUpperCase()} - {type.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !repoUrl}
              className="w-full flex justify-center items-center px-6 py-4 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Starting Analysis...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  Start Analysis
                </>
              )}
            </button>
          </form>
        </div>

        {/* Features Section */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">Bug Detection</h3>
            <p className="mt-2 text-sm text-gray-600">
              Identify logical errors and runtime bugs with AI-powered analysis
            </p>
          </div>

          <div className="text-center">
            <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-purple-100">
              <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">Security Scan</h3>
            <p className="mt-2 text-sm text-gray-600">
              Detect vulnerabilities like SQL injection, XSS, and more
            </p>
          </div>

          <div className="text-center">
            <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-green-100">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">Code Quality</h3>
            <p className="mt-2 text-sm text-gray-600">
              Improve maintainability with actionable suggestions
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default HomePage
