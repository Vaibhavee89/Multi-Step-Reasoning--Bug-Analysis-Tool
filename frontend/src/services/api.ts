import axios from 'axios'
import type {
  RepoAnalysisRequest,
  AnalysisResponse,
  AnalysisResult,
  RepoInfo,
  AnalysisTool,
  AnalysisType
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const analyzeRepository = async (
  request: RepoAnalysisRequest
): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/api/analyze', request)
  return response.data
}

export const getAnalysisResult = async (
  analysisId: string
): Promise<AnalysisResult> => {
  const response = await api.get<AnalysisResult>(`/api/analysis/${analysisId}`)
  return response.data
}

export const validateGitHubRepo = async (
  repoUrl: string,
  githubToken?: string
): Promise<RepoInfo> => {
  const response = await api.post<RepoInfo>('/api/github/validate', {
    repo_url: repoUrl,
    github_token: githubToken,
  })
  return response.data
}

export const getAvailableTools = async (): Promise<{
  tools: AnalysisTool[]
  analysis_types: AnalysisType[]
}> => {
  const response = await api.get('/api/tools')
  return response.data
}

export const checkHealth = async (): Promise<any> => {
  const response = await api.get('/api/health')
  return response.data
}

export default api
