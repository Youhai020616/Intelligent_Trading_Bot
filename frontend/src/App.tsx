import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, Container } from '@mui/material'

import Header from './components/layout/Header'
import Sidebar from './components/layout/Sidebar'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Agents from './pages/Agents'
import History from './pages/History'

function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen)
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header onMenuClick={handleSidebarToggle} />
      <Sidebar open={sidebarOpen} />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          marginLeft: sidebarOpen ? '280px' : '80px',
          transition: 'margin-left 0.3s ease',
          marginTop: '64px', // Header height
        }}
      >
        <Container maxWidth="xl" sx={{ py: 2 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  )
}

export default App