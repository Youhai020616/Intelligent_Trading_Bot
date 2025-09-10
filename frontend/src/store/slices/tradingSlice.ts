import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface TradingSignal {
  id: string
  symbol: string
  signal: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  price: number
  timestamp: Date
  reasoning: string
}

export interface AnalysisResult {
  id: string
  symbol: string
  type: 'technical' | 'fundamental' | 'sentiment'
  data: any
  timestamp: Date
}

interface TradingState {
  currentSymbol: string
  signals: TradingSignal[]
  analysis: AnalysisResult[]
  isAnalyzing: boolean
  error: string | null
}

const initialState: TradingState = {
  currentSymbol: 'AAPL',
  signals: [],
  analysis: [],
  isAnalyzing: false,
  error: null,
}

const tradingSlice = createSlice({
  name: 'trading',
  initialState,
  reducers: {
    setCurrentSymbol: (state, action: PayloadAction<string>) => {
      state.currentSymbol = action.payload
    },
    addSignal: (state, action: PayloadAction<TradingSignal>) => {
      state.signals.unshift(action.payload)
      // Keep only last 50 signals
      if (state.signals.length > 50) {
        state.signals = state.signals.slice(0, 50)
      }
    },
    addAnalysis: (state, action: PayloadAction<AnalysisResult>) => {
      state.analysis.unshift(action.payload)
      // Keep only last 20 analysis results
      if (state.analysis.length > 20) {
        state.analysis = state.analysis.slice(0, 20)
      }
    },
    setAnalyzing: (state, action: PayloadAction<boolean>) => {
      state.isAnalyzing = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    clearSignals: (state) => {
      state.signals = []
    },
    clearAnalysis: (state) => {
      state.analysis = []
    },
  },
})

export const {
  setCurrentSymbol,
  addSignal,
  addAnalysis,
  setAnalyzing,
  setError,
  clearSignals,
  clearAnalysis,
} = tradingSlice.actions

export default tradingSlice.reducer