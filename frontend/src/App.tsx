import React from "react";
import { Routes, Route } from "react-router-dom";
import { Box, Container } from "@mui/material";
import { AuroraBackground } from "@/components/ui/aurora-background";

import Header from "./components/layout/Header";
import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./pages/Dashboard";
import Analysis from "./pages/Analysis";
import Agents from "./pages/Agents";
import History from "./pages/History";
import Login from "./pages/Login";

function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const [isLoggedIn, setIsLoggedIn] = React.useState(false); // 临时状态，实际应用中应该使用全局状态管理

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // 如果未登录，显示登录页面
  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />;
  }

  // 已登录，显示主应用界面
  return (
    <AuroraBackground className="!h-screen !p-0">
      <Box
        sx={{
          display: "flex",
          minHeight: "100vh",
          width: "100%",
          position: "relative",
          zIndex: 1,
        }}
      >
        <Header onMenuClick={handleSidebarToggle} />
        <Sidebar open={sidebarOpen} />

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            marginLeft: sidebarOpen ? "280px" : "80px",
            transition: "margin-left 0.3s ease",
            marginTop: "64px", // Header height
            backgroundColor: "rgba(255, 255, 255, 0.1)", // 半透明背景
            backdropFilter: "blur(10px)", // 背景模糊
            borderRadius: "16px",
            margin: "80px 16px 16px 16px", // 调整边距
            minHeight: "calc(100vh - 96px)",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
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
    </AuroraBackground>
  );
}

export default App;
