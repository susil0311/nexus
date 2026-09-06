import axios, { AxiosInstance, AxiosError } from 'axios'

// ─── Axios Instance ─────────────────────────────────────────────────────────
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// ─── Request Interceptor ─────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('nexus_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ─── Response Interceptor ────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('nexus_token')
        localStorage.removeItem('nexus_user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ─── Types ───────────────────────────────────────────────────────────────────
export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface User {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'pm' | 'field' | 'viewer'
  avatar_url?: string
}

export interface Project {
  id: string
  name: string
  client: string
  location: string
  lat: number
  lng: number
  start_date: string
  planned_finish: string
  status: 'active' | 'on_hold' | 'completed'
  spi: number
  cpi: number
  progress: number
  disciplines: string[]
}

export interface DashboardData {
  spi: number
  cpi: number
  spi_trend: number
  cpi_trend: number
  total_activities: number
  completed_activities: number
  at_risk_count: number
  delayed_count: number
  not_started_count: number
  recent_submissions: Submission[]
  discipline_breakdown: DisciplineBreakdown[]
  scurve_data: SCurvePoint[]
}

export interface Submission {
  id: string
  description: string
  status: 'done' | 'processing' | 'failed' | 'pending'
  discipline: string
  submitted_by: string
  submitted_at: string
  matched_activity?: string
  confidence?: number
}

export interface DisciplineBreakdown {
  discipline: string
  total: number
  completed: number
  at_risk: number
  delayed: number
}

export interface SCurvePoint {
  date: string
  planned: number
  actual: number
}

export interface ScheduleActivity {
  id: string
  activity_id?: string
  wbs_code: string
  name: string
  discipline: string
  planned_start: string
  planned_finish: string
  actual_start?: string
  actual_finish?: string
  progress: number
  planned_progress?: number
  actual_progress?: number
  float_days: number
  status: 'on_track' | 'at_risk' | 'delayed' | 'not_started' | 'completed' | 'in_progress'
  children?: ScheduleActivity[]
  level: number
  parent_id?: string
}

export interface ReviewItem {
  id: string
  submission_id?: string
  extracted_text?: string
  raw_description?: string
  extracted_date?: string
  submitted_at?: string
  source?: string
  discipline: string
  status: 'pending' | 'approved' | 'rejected' | 'needs_review' | 'flagged_new' | 'auto_accepted'
  candidates: MatchCandidate[]
  created_at?: string
}

export interface MatchCandidate {
  activity_id: string
  activity_name: string
  wbs_code?: string
  score: number
  explanation?: string
  discipline?: string
}

export interface ForecastData {
  predicted_finish: string
  planned_finish: string
  delay_days: number
  confidence: number
  risk_factors: RiskFactor[]
  scurve_forecast: ForecastSCurve[]
  critical_path: CriticalActivity[]
}

export interface RiskFactor {
  name: string
  impact_percent: number
  description: string
}

export interface ForecastSCurve {
  date: string
  planned: number
  actual: number
  optimistic: number
  pessimistic: number
}

export interface CriticalActivity {
  id: string
  name: string
  discipline: string
  risk_score: number
  delay_days: number
  reason: string
}

export interface Anomaly {
  id: string
  type: 'productivity_drop' | 'schedule_deviation' | 'cost_overrun' | 'data_gap' | 'weather_impact'
  title: string
  description: string
  severity: 'critical' | 'medium' | 'low'
  related_activity_id?: string
  related_activity_name?: string
  detected_at: string
  status: 'open' | 'investigating' | 'resolved'
  resolved_at?: string
}

export interface MemoryResponse {
  answer: string
  sources: MemorySource[]
  confidence: number
  query_id: string
}

export interface MemorySource {
  id: string
  project_name: string
  activity_name: string
  date: string
  excerpt: string
  relevance: number
}

export interface IngestTextRequest {
  text: string
  project_id: string
  source?: string
  discipline?: string
}

export interface IngestResponse {
  submission_id: string
  status: string
  extracted_fields: {
    date?: string
    activity_description?: string
    progress?: number
    discipline?: string
    remarks?: string
  }
  best_match?: {
    activity_id: string
    activity_name: string
    score: number
  }
}

export interface ApproveMatchRequest {
  activity_id: string
  notes?: string
  override_progress?: number
}

// ─── Auth API ────────────────────────────────────────────────────────────────
export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const { data } = await api.post<LoginResponse>('/auth/login', { email, password })
    return data
  },
  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },
  getMe: async (): Promise<User> => {
    const { data } = await api.get<User>('/auth/me')
    return data
  },
}

// ─── Projects API ─────────────────────────────────────────────────────────────
export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    const { data } = await api.get<Project[]>('/projects')
    return data
  },
  getProject: async (id: string): Promise<Project> => {
    const { data } = await api.get<Project>(`/projects/${id}`)
    return data
  },
  getProjectSchedule: async (id: string): Promise<ScheduleActivity[]> => {
    const { data } = await api.get<ScheduleActivity[]>(`/projects/${id}/schedule`)
    return data
  },
  createProject: async (projectData: Partial<Project>): Promise<Project> => {
    const { data } = await api.post<Project>('/projects', projectData)
    return data
  },
}

// ─── Ingest API ───────────────────────────────────────────────────────────────
export const ingestApi = {
  ingestText: async (reqData: IngestTextRequest): Promise<IngestResponse> => {
    const { data } = await api.post<IngestResponse>('/ingest/text', reqData)
    return data
  },
  ingestFile: async (file: File, projectId: string, discipline: string): Promise<IngestResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId)
    formData.append('discipline', discipline)
    const { data } = await api.post<IngestResponse>('/ingest/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  getSubmission: async (id: string): Promise<Submission> => {
    const { data } = await api.get<Submission>(`/ingest/submissions/${id}`)
    return data
  },
}

// ─── Matches API ──────────────────────────────────────────────────────────────
export const matchesApi = {
  getReviewQueue: async (projectId: string, status?: string): Promise<ReviewItem[]> => {
    const params = status ? { project_id: projectId, status } : { project_id: projectId }
    const { data } = await api.get<ReviewItem[]>('/matches/queue', { params })
    return data
  },
  approveMatch: async (id: string, reqData: ApproveMatchRequest): Promise<ReviewItem> => {
    const { data } = await api.post<ReviewItem>(`/matches/${id}/approve`, reqData)
    return data
  },
  rejectMatch: async (id: string, reason?: string): Promise<ReviewItem> => {
    const { data } = await api.post<ReviewItem>(`/matches/${id}/reject`, { reason })
    return data
  },
  bulkApprove: async (ids: string[]): Promise<{ approved: number }> => {
    const { data } = await api.post<{ approved: number }>('/matches/bulk-approve', { ids })
    return data
  },
}

// ─── Analytics API ────────────────────────────────────────────────────────────
export const analyticsApi = {
  getDashboard: async (projectId: string): Promise<DashboardData> => {
    const { data } = await api.get<DashboardData>('/analytics/dashboard', {
      params: { project_id: projectId },
    })
    return data
  },
  getSpiTrend: async (projectId: string, from: string, to: string): Promise<SCurvePoint[]> => {
    const { data } = await api.get<SCurvePoint[]>('/analytics/spi-trend', {
      params: { project_id: projectId, from, to },
    })
    return data
  },
  getPortfolio: async (): Promise<Project[]> => {
    const { data } = await api.get<Project[]>('/analytics/portfolio')
    return data
  },
}

// ─── AI API ───────────────────────────────────────────────────────────────────
export const aiApi = {
  getForecast: async (projectId: string): Promise<ForecastData> => {
    const { data } = await api.get<ForecastData>('/ai/forecast', {
      params: { project_id: projectId },
    })
    return data
  },
  queryMemory: async (question: string, context?: string): Promise<MemoryResponse> => {
    const { data } = await api.post<MemoryResponse>('/ai/memory/query', { question, context })
    return data
  },
  getAnomalies: async (projectId: string): Promise<Anomaly[]> => {
    const { data } = await api.get<Anomaly[]>('/ai/anomalies', {
      params: { project_id: projectId },
    })
    return data
  },
  resolveAnomaly: async (id: string): Promise<Anomaly> => {
    const { data } = await api.post<Anomaly>(`/ai/anomalies/${id}/resolve`)
    return data
  },
}

export default api
