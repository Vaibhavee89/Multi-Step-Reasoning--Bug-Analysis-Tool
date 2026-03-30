export interface RepoAnalysisRequest {
  repo_url: string
  analysis_type: string
  github_token?: string
}

export interface AnalysisResponse {
  analysis_id: string
  status: string
  repo_url: string
  message: string
}

export interface ReasoningStep {
  step: number
  tool: string
  input: string
  output: string
}

export interface AnalysisResult {
  analysis_id: string
  status: string
  repo_url: string
  output: string
  reasoning_steps: ReasoningStep[]
  timestamp: string
}

export interface ProgressUpdate {
  type: string
  analysis_id: string
  message: string
  timestamp: string
}

export interface RepoInfo {
  valid: boolean
  name: string
  description: string
  language: string
  stars: number
  is_private: boolean
}

export interface AnalysisTool {
  name: string
  description: string
}

export interface AnalysisType {
  type: string
  description: string
}
