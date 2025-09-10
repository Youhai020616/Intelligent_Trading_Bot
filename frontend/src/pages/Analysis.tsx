import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Alert,
} from '@mui/material'
import {
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import { RootState } from '../store'
import { setCurrentSymbol, setAnalyzing, addAnalysis } from '../store/slices/tradingSlice'

const Analysis: React.FC = () => {
  const dispatch = useDispatch()
  const { currentSymbol, analysis, isAnalyzing, error } = useSelector((state: RootState) => state.trading)
  const [searchSymbol, setSearchSymbol] = useState(currentSymbol)

  const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX']

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      dispatch(setCurrentSymbol(searchSymbol.toUpperCase()))
      dispatch(setAnalyzing(true))

      // 模拟分析过程
      setTimeout(() => {
        const mockAnalysis = {
          id: Date.now().toString(),
          symbol: searchSymbol.toUpperCase(),
          type: 'technical' as const,
          data: {
            rsi: 65.4,
            macd: 2.34,
            moving_average: 'bullish',
            support: 150.25,
            resistance: 175.80,
          },
          timestamp: new Date(),
        }
        dispatch(addAnalysis(mockAnalysis))
        dispatch(setAnalyzing(false))
      }, 2000)
    }
  }

  const handlePopularStockClick = (symbol: string) => {
    setSearchSymbol(symbol)
    dispatch(setCurrentSymbol(symbol))
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        交易分析
      </Typography>

      {/* 股票搜索区域 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            股票分析
          </Typography>

          <Box display="flex" gap={2} mb={2}>
            <TextField
              fullWidth
              label="输入股票代码"
              value={searchSymbol}
              onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="例如: AAPL, GOOGL, TSLA"
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={isAnalyzing}
              startIcon={<SearchIcon />}
              sx={{ minWidth: 120 }}
            >
              {isAnalyzing ? '分析中...' : '分析'}
            </Button>
          </Box>

          {/* 热门股票 */}
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              热门股票:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {popularStocks.map((stock) => (
                <Chip
                  key={stock}
                  label={stock}
                  onClick={() => handlePopularStockClick(stock)}
                  variant={currentSymbol === stock ? "filled" : "outlined"}
                  color={currentSymbol === stock ? "primary" : "default"}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {isAnalyzing && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              分析进度
            </Typography>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              正在分析 {currentSymbol} 的技术指标、基本面和市场情绪...
            </Typography>
          </CardContent>
        </Card>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* 分析结果 */}
      {analysis.length > 0 && (
        <Grid container spacing={3}>
          {/* 技术分析结果 */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                  <AssessmentIcon sx={{ mr: 1 }} />
                  技术分析结果 - {currentSymbol}
                </Typography>

                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>指标</TableCell>
                        <TableCell align="right">数值</TableCell>
                        <TableCell align="center">信号</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analysis
                        .filter(a => a.symbol === currentSymbol)
                        .slice(0, 1)
                        .map((item) => (
                          <React.Fragment key={item.id}>
                            <TableRow>
                              <TableCell>RSI</TableCell>
                              <TableCell align="right">{item.data.rsi}</TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={item.data.rsi > 70 ? '超买' : item.data.rsi < 30 ? '超卖' : '中性'}
                                  color={item.data.rsi > 70 ? 'error' : item.data.rsi < 30 ? 'success' : 'default'}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>MACD</TableCell>
                              <TableCell align="right">{item.data.macd}</TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={item.data.macd > 0 ? '看涨' : '看跌'}
                                  color={item.data.macd > 0 ? 'success' : 'error'}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>移动平均线</TableCell>
                              <TableCell align="right">-</TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={item.data.moving_average}
                                  color="primary"
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                          </React.Fragment>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* 关键指标卡片 */}
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  关键指标
                </Typography>

                {analysis
                  .filter(a => a.symbol === currentSymbol)
                  .slice(0, 1)
                  .map((item) => (
                    <Box key={item.id}>
                      <Box display="flex" justifyContent="space-between" mb={2}>
                        <Typography variant="body2">支撑位</Typography>
                        <Typography variant="body1" fontWeight="bold">
                          ${item.data.support}
                        </Typography>
                      </Box>

                      <Box display="flex" justifyContent="space-between" mb={2}>
                        <Typography variant="body2">阻力位</Typography>
                        <Typography variant="body1" fontWeight="bold">
                          ${item.data.resistance}
                        </Typography>
                      </Box>

                      <Box display="flex" justifyContent="space-between" mb={2}>
                        <Typography variant="body2">分析时间</Typography>
                        <Typography variant="body2">
                          {new Date(item.timestamp).toLocaleString()}
                        </Typography>
                      </Box>

                      <Box mt={3}>
                        <Button
                          fullWidth
                          variant="contained"
                          startIcon={<TrendingUpIcon />}
                          sx={{ mb: 1 }}
                        >
                          执行买入
                        </Button>
                        <Button
                          fullWidth
                          variant="outlined"
                          color="error"
                        >
                          执行卖出
                        </Button>
                      </Box>
                    </Box>
                  ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 空状态 */}
      {!isAnalyzing && analysis.length === 0 && !error && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <AssessmentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              还没有分析结果
            </Typography>
            <Typography variant="body2" color="text.secondary">
              选择一只股票开始分析，或从热门股票中选择
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default Analysis