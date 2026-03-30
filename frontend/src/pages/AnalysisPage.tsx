import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAnalysisResult } from '../services/api'
import type { AnalysisResult, ProgressUpdate } from '../types'
import ReactMarkdown from 'react-markdown'

function AnalysisPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const navigate = useNavigate()
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState<string[]>([])
  const [showReasoningTrace, setShowReasoningTrace] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!analysisId) return

    // Connect to WebSocket for progress updates
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws')

      ws.onopen = () => {
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        const data: ProgressUpdate = JSON.parse(event.data)
        if (data.type === 'progress' && data.analysis_id === analysisId) {
          setProgress((prev) => [...prev, data.message])
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
      }

      wsRef.current = ws
    }

    connectWebSocket()

    // Poll for results
    const pollInterval = setInterval(async () => {
      try {
        const data = await getAnalysisResult(analysisId)
        setResult(data)
        setLoading(false)
        clearInterval(pollInterval)
      } catch (err: any) {
        if (err.response?.status !== 404) {
          setError('Failed to fetch analysis results')
          clearInterval(pollInterval)
        }
      }
    }, 3000)

    return () => {
      clearInterval(pollInterval)
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [analysisId])

  const getSeverityColor = (text: string) => {
    if (text.toLowerCase().includes('critical')) return 'text-red-600 bg-red-50'
    if (text.toLowerCase().includes('high')) return 'text-orange-600 bg-orange-50'
    if (text.toLowerCase().includes('medium')) return 'text-yellow-600 bg-yellow-50'
    if (text.toLowerCase().includes('low')) return 'text-blue-600 bg-blue-50'
    return 'text-gray-600 bg-gray-50'
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-red-600 mb-4">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-center mb-4">Analysis Failed</h2>
          <p className="text-gray-600 text-center mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Start New Analysis
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="text-gray-600 hover:text-gray-900"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Analysis Results</h1>
                <p className="text-sm text-gray-500">ID: {analysisId}</p>
              </div>
            </div>
            {result && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                ✓ Complete
              </span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {loading ? (
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* Loading State */}
            <div className="text-center mb-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Repository...</h2>
              <p className="text-gray-600">This may take a few minutes depending on repository size</p>
            </div>

            {/* Progress Updates */}
            {progress.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <svg className="animate-spin h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Progress
                </h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {progress.map((msg, idx) => (
                    <div key={idx} className="flex items-start space-x-3 text-sm">
                      <span className="text-blue-600">→</span>
                      <span className="text-gray-700">{msg}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : result ? (
          <div className="space-y-6">
            {/* Analysis Output */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Analysis Report</h2>
                <button
                  onClick={() => setShowReasoningTrace(!showReasoningTrace)}
                  className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100"
                >
                  {showReasoningTrace ? 'Hide' : 'Show'} Reasoning Trace
                </button>
              </div>

              <div className="prose max-w-none">
                <ReactMarkdown className="text-gray-800 whitespace-pre-wrap">
                  {result.output}
                </ReactMarkdown>
              </div>

              {/* Summary Stats */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {result.reasoning_steps.length}
                    </div>
                    <div className="text-sm text-gray-600">Reasoning Steps</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {(result.output.match(/critical/gi) || []).length}
                    </div>
                    <div className="text-sm text-gray-600">Critical Issues</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {(result.output.match(/high/gi) || []).length}
                    </div>
                    <div className="text-sm text-gray-600">High Priority</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">
                      {(result.output.match(/medium/gi) || []).length}
                    </div>
                    <div className="text-sm text-gray-600">Medium Priority</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Reasoning Trace */}
            {showReasoningTrace && result.reasoning_steps.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Reasoning Trace</h2>
                <div className="space-y-4">
                  {result.reasoning_steps.map((step) => (
                    <div key={step.step} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center mb-3">
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-semibold text-sm mr-3">
                          {step.step}
                        </span>
                        <span className="font-semibold text-gray-900">{step.tool}</span>
                      </div>

                      <div className="ml-11 space-y-3">
                        <div>
                          <span className="text-xs font-medium text-gray-500 uppercase">Input</span>
                          <div className="mt-1 text-sm text-gray-700 bg-gray-50 p-2 rounded">
                            {step.input}
                          </div>
                        </div>

                        <div>
                          <span className="text-xs font-medium text-gray-500 uppercase">Output</span>
                          <div className="mt-1 text-sm text-gray-700 bg-gray-50 p-2 rounded max-h-40 overflow-y-auto">
                            {step.output}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Next Steps</h3>
              <div className="flex space-x-4">
                <button
                  onClick={() => navigate('/')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Analyze Another Repository
                </button>
                <button
                  onClick={() => {
                    const blob = new Blob([JSON.stringify(result, null, 2)], {
                      type: 'application/json',
                    })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `analysis-${analysisId}.json`
                    a.click()
                  }}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                >
                  Download Report
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  )
}

export default AnalysisPage
