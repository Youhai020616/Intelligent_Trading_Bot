import React from 'react'
import { useSelector } from 'react-redux'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Avatar,
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as HoldIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material'
import { RootState } from '../store'

const History: React.FC = () => {
  const { signals } = useSelector((state: RootState) => state.trading)
  const { activities } = useSelector((state: RootState) => state.agents)

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return <TrendingUpIcon sx={{ color: 'success.main' }} />
      case 'SELL':
        return <TrendingDownIcon sx={{ color: 'error.main' }} />
      case 'HOLD':
        return <HoldIcon sx={{ color: 'warning.main' }} />
      default:
        return <HoldIcon />
    }
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return 'success'
      case 'SELL':
        return 'error'
      case 'HOLD':
        return 'warning'
      default:
        return 'default'
    }
  }

  // 计算统计数据
  const stats = React.useMemo(() => {
    const totalSignals = signals.length
    const buySignals = signals.filter(s => s.signal === 'BUY').length
    const sellSignals = signals.filter(s => s.signal === 'SELL').length
    const holdSignals = signals.filter(s => s.signal === 'HOLD').length

    const avgConfidence = signals.length > 0
      ? signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length
      : 0

    return {
      totalSignals,
      buySignals,
      sellSignals,
      holdSignals,
      avgConfidence,
    }
  }, [signals])

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        决策历史
      </Typography>

      {/* 统计卡片 */}
      <Box display="flex" gap={2} mb={3} flexWrap="wrap">
        <Card sx={{ minWidth: 150 }}>
          <CardContent>
            <Typography variant="h6" color="primary">
              {stats.totalSignals}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              总信号数
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 150 }}>
          <CardContent>
            <Typography variant="h6" color="success.main">
              {stats.buySignals}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              买入信号
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 150 }}>
          <CardContent>
            <Typography variant="h6" color="error.main">
              {stats.sellSignals}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              卖出信号
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 150 }}>
          <CardContent>
            <Typography variant="h6" color="warning.main">
              {stats.holdSignals}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              持有信号
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 150 }}>
          <CardContent>
            <Typography variant="h6" color="info.main">
              {(stats.avgConfidence * 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              平均置信度
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* 交易信号历史表格 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            交易信号历史
          </Typography>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>股票代码</TableCell>
                  <TableCell>信号</TableCell>
                  <TableCell align="right">价格</TableCell>
                  <TableCell align="right">置信度</TableCell>
                  <TableCell>时间</TableCell>
                  <TableCell>推理</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {signals.map((signal) => (
                  <TableRow key={signal.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="bold">
                        {signal.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getSignalIcon(signal.signal)}
                        <Chip
                          label={signal.signal}
                          color={getSignalColor(signal.signal) as any}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        ${signal.price.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {(signal.confidence * 100).toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(signal.timestamp).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{
                        maxWidth: 200,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {signal.reasoning}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}

                {signals.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                      <Typography variant="body1" color="text.secondary">
                        暂无交易信号历史
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        系统生成的交易信号将显示在这里
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* 智能体活动历史 */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            智能体活动历史
          </Typography>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>智能体</TableCell>
                  <TableCell>活动</TableCell>
                  <TableCell>时间</TableCell>
                  <TableCell>详情</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activities.map((activity) => (
                  <TableRow key={activity.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Avatar sx={{ width: 32, height: 32 }}>
                          <SmartToyIcon sx={{ fontSize: 16 }} />
                        </Avatar>
                        <Typography variant="body2">
                          {activity.agentId}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {activity.action}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(activity.timestamp).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{
                        maxWidth: 200,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {activity.details || '无详情'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}

                {activities.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center" sx={{ py: 6 }}>
                      <Typography variant="body1" color="text.secondary">
                        暂无智能体活动历史
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        智能体的活动记录将显示在这里
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  )
}

export default History