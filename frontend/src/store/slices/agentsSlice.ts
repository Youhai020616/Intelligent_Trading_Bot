import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface Agent {
  id: string
  name: string
  type: 'analyst' | 'researcher' | 'trader' | 'risk_manager'
  status: 'active' | 'idle' | 'error'
  confidence: number
  lastActivity: Date
  avatar?: string
}

export interface AgentActivity {
  id: string
  agentId: string
  action: string
  timestamp: Date
  details?: any
}

interface AgentsState {
  agents: Agent[]
  activities: AgentActivity[]
  isLoading: boolean
  error: string | null
}

const initialState: AgentsState = {
  agents: [
    {
      id: '1',
      name: '技术分析师',
      type: 'analyst',
      status: 'active',
      confidence: 0.85,
      lastActivity: new Date(),
      avatar: '📊'
    },
    {
      id: '2',
      name: '基本面分析师',
      type: 'analyst',
      status: 'active',
      confidence: 0.78,
      lastActivity: new Date(),
      avatar: '📈'
    },
    {
      id: '3',
      name: '情绪分析师',
      type: 'analyst',
      status: 'idle',
      confidence: 0.92,
      lastActivity: new Date(Date.now() - 300000), // 5 minutes ago
      avatar: '🧠'
    },
    {
      id: '4',
      name: '多头研究员',
      type: 'researcher',
      status: 'active',
      confidence: 0.88,
      lastActivity: new Date(),
      avatar: '📈'
    },
    {
      id: '5',
      name: '空头研究员',
      type: 'researcher',
      status: 'idle',
      confidence: 0.76,
      lastActivity: new Date(Date.now() - 600000), // 10 minutes ago
      avatar: '📉'
    },
    {
      id: '6',
      name: '交易执行员',
      type: 'trader',
      status: 'active',
      confidence: 0.91,
      lastActivity: new Date(),
      avatar: '💼'
    },
    {
      id: '7',
      name: '风险管理师',
      type: 'risk_manager',
      status: 'active',
      confidence: 0.94,
      lastActivity: new Date(),
      avatar: '🛡️'
    },
  ],
  activities: [],
  isLoading: false,
  error: null,
}

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    updateAgentStatus: (state, action: PayloadAction<{ id: string; status: Agent['status'] }>) => {
      const agent = state.agents.find(a => a.id === action.payload.id)
      if (agent) {
        agent.status = action.payload.status
        agent.lastActivity = new Date()
      }
    },
    updateAgentConfidence: (state, action: PayloadAction<{ id: string; confidence: number }>) => {
      const agent = state.agents.find(a => a.id === action.payload.id)
      if (agent) {
        agent.confidence = action.payload.confidence
      }
    },
    addActivity: (state, action: PayloadAction<AgentActivity>) => {
      state.activities.unshift(action.payload)
      // Keep only last 100 activities
      if (state.activities.length > 100) {
        state.activities = state.activities.slice(0, 100)
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    clearActivities: (state) => {
      state.activities = []
    },
  },
})

export const {
  updateAgentStatus,
  updateAgentConfidence,
  addActivity,
  setLoading,
  setError,
  clearActivities,
} = agentsSlice.actions

export default agentsSlice.reducer