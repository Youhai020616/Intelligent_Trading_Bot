import React from "react";
import { useSelector } from "react-redux";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
} from "@mui/material";
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as HoldIcon,
  SmartToy as AgentIcon,
} from "@mui/icons-material";
import { RootState } from "../store";

const Dashboard: React.FC = () => {
  const { signals } = useSelector((state: RootState) => state.trading);
  const { agents } = useSelector((state: RootState) => state.agents);

  // 模拟实时数据
  const systemMetrics = {
    totalSignals: signals.length,
    activeAgents: agents.filter((a) => a.status === "active").length,
    systemUptime: "99.9%",
    lastUpdate: new Date().toLocaleTimeString(),
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case "BUY":
        return <TrendingUpIcon sx={{ color: "success.main" }} />;
      case "SELL":
        return <TrendingDownIcon sx={{ color: "error.main" }} />;
      case "HOLD":
        return <HoldIcon sx={{ color: "warning.main" }} />;
      default:
        return <HoldIcon />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case "BUY":
        return "success";
      case "SELL":
        return "error";
      case "HOLD":
        return "warning";
      default:
        return "default";
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        交易仪表板
      </Typography>

      <Grid container spacing={3}>
        {/* 系统状态卡片 */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AgentIcon sx={{ mr: 1, color: "primary.main" }} />
                <Typography variant="h6">活跃智能体</Typography>
              </Box>
              <Typography variant="h3" color="primary.main">
                {systemMetrics.activeAgents}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                共 {agents.length} 个智能体
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUpIcon sx={{ mr: 1, color: "success.main" }} />
                <Typography variant="h6">今日信号</Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {systemMetrics.totalSignals}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                实时更新
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                系统状态
              </Typography>
              <Chip label="运行正常" color="success" sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                正常运行时间: {systemMetrics.systemUptime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                最后更新
              </Typography>
              <Typography variant="h5">{systemMetrics.lastUpdate}</Typography>
              <Typography variant="body2" color="text.secondary">
                实时同步
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 最新交易信号 */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                最新交易信号
              </Typography>
              <List>
                {signals.slice(0, 5).map((signal, index) => (
                  <React.Fragment key={signal.id}>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor: `${getSignalColor(signal.signal)}.main`,
                          }}
                        >
                          {getSignalIcon(signal.signal)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <span
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "8px",
                            }}
                          >
                            <Typography variant="subtitle1">
                              {signal.symbol}
                            </Typography>
                            <Typography
                              variant="body2"
                              component="span"
                              sx={{
                                color: `${getSignalColor(signal.signal)}.main`,
                                fontWeight: 500,
                                px: 1,
                                py: 0.5,
                                borderRadius: 1,
                                bgcolor: `${getSignalColor(signal.signal)}.light`,
                                fontSize: "0.75rem",
                              }}
                            >
                              {signal.signal}
                            </Typography>
                          </span>
                        }
                        secondary={
                          <span>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              component="span"
                            >
                              置信度: {(signal.confidence * 100).toFixed(1)}%
                            </Typography>
                            <br />
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              component="span"
                            >
                              {new Date(signal.timestamp).toLocaleString()}
                            </Typography>
                          </span>
                        }
                      />
                    </ListItem>
                    {index < signals.slice(0, 5).length - 1 && <Divider />}
                  </React.Fragment>
                ))}
                {signals.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="暂无交易信号"
                      secondary="系统正在监控市场..."
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* 智能体状态 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                智能体状态
              </Typography>
              <List>
                {agents.slice(0, 4).map((agent, index) => (
                  <React.Fragment key={agent.id}>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor:
                              agent.status === "active"
                                ? "success.main"
                                : agent.status === "idle"
                                  ? "warning.main"
                                  : "error.main",
                          }}
                        >
                          {agent.avatar || <AgentIcon />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={agent.name}
                        secondary={
                          <span>
                            <Typography
                              variant="body2"
                              component="span"
                              sx={{
                                color:
                                  agent.status === "active"
                                    ? "success.main"
                                    : agent.status === "idle"
                                      ? "warning.main"
                                      : "error.main",
                                fontWeight: 500,
                                mr: 1,
                              }}
                            >
                              {agent.status}
                            </Typography>
                            <Typography variant="body2" component="span">
                              置信度: {(agent.confidence * 100).toFixed(0)}%
                            </Typography>
                          </span>
                        }
                      />
                    </ListItem>
                    <Box sx={{ px: 2, pb: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={agent.confidence * 100}
                        color={
                          agent.confidence > 0.8
                            ? "success"
                            : agent.confidence > 0.6
                              ? "warning"
                              : "error"
                        }
                        sx={{ height: 4, borderRadius: 2 }}
                      />
                    </Box>
                    {index < agents.slice(0, 4).length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
