import React from 'react'
import { useSelector } from 'react-redux'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Badge,
} from '@mui/material'
import {
  SmartToy as SmartToyIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material'
import { RootState } from '../store'

const Agents: React.FC = () => {
  const { agents, activities } = useSelector((state: RootState) => state.agents)

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'analyst':
        return <AnalyticsIcon />
      case 'researcher':
        return <PsychologyIcon />
      case 'trader':
        return <TrendingUpIcon />
      case 'risk_manager':
        return <SecurityIcon />
      default:
        return <SmartToyIcon />
    }
  }

  const getAgentTypeName = (type: string) => {
    switch (type) {
      case 'analyst':
        return '分析师'
      case 'researcher':
        return '研究员'
      case 'trader':
        return '交易员'
      case 'risk_manager':
        return '风险管理师'
      default:
        return '智能体'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success'
      case 'idle':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success'
    if (confidence >= 0.6) return 'warning'
    return 'error'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        智能体监控
      </Typography>

      <Grid container spacing={3}>
        {/* 智能体网格 */}
        {agents.map((agent) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
            <Card
              sx={{
                height: '100%',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: (theme) => theme.shadows[8],
                },
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Badge
                    overlap="circular"
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    badgeContent={
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: getStatusColor(agent.status) + '.main',
                        }}
                      />
                    }
                  >
                    <Avatar
                      sx={{
                        width: 56,
                        height: 56,
                        bgcolor: getStatusColor(agent.status) + '.main',
                        fontSize: '1.5rem',
                      }}
                    >
                      {agent.avatar || getAgentIcon(agent.type)}
                    </Avatar>
                  </Badge>
                </Box>

                <Typography variant="h6" gutterBottom>
                  {agent.name}
                </Typography>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {getAgentTypeName(agent.type)}
                </Typography>

                <Box mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">置信度</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {(agent.confidence * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={agent.confidence * 100}
                    color={getConfidenceColor(agent.confidence) as any}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>

                <Box>
                  <Chip
                    label={agent.status === 'active' ? '活跃' :
                           agent.status === 'idle' ? '空闲' : '错误'}
                    color={getStatusColor(agent.status) as any}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {new Date(agent.lastActivity).toLocaleTimeString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {/* 智能体协作流程图 */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                智能体协作流程
              </Typography>

              <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
                {agents.map((agent, index) => (
                  <React.Fragment key={agent.id}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        p: 2,
                        border: '2px solid',
                        borderColor: getStatusColor(agent.status) + '.main',
                        borderRadius: 2,
                        minWidth: 120,
                        backgroundColor: agent.status === 'active' ? 'action.selected' : 'background.paper',
                      }}
                    >
                      <Avatar
                        sx={{
                          width: 40,
                          height: 40,
                          mb: 1,
                          bgcolor: getStatusColor(agent.status) + '.main',
                        }}
                      >
                        {getAgentIcon(agent.type)}
                      </Avatar>
                      <Typography variant="body2" align="center">
                        {agent.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {getAgentTypeName(agent.type)}
                      </Typography>
                    </Box>

                    {index < agents.length - 1 && (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="h6" color="text.secondary">
                          →
                        </Typography>
                      </Box>
                    )}
                  </React.Fragment>
                ))}
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                智能体按顺序协作：分析师 → 研究员 → 交易员 → 风险管理师 → 最终决策
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 活动日志 */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                最新活动
              </Typography>

              <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                {activities.slice(0, 10).map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start">
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <SmartToyIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" fontWeight="bold">
                            {activity.agentId}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.primary">
                              {activity.action}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(activity.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < activities.slice(0, 10).length - 1 && <Divider />}
                  </React.Fragment>
                ))}

                {activities.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="暂无活动记录"
                      secondary="智能体活动将显示在这里"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Agents