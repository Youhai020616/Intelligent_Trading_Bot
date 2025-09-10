import { configureStore } from '@reduxjs/toolkit'
import tradingReducer from './slices/tradingSlice'
import agentsReducer from './slices/agentsSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    trading: tradingReducer,
    agents: agentsReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch