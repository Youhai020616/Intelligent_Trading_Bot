import React from 'react'
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Chip,
  useTheme,
} from '@mui/material'
import {
  Menu as MenuIcon,
  TrendingUp as TrendingUpIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
} from '@mui/icons-material'

interface HeaderProps {
  onMenuClick: () => void
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const theme = useTheme()

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: theme.palette.background.paper,
        color: theme.palette.text.primary,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={onMenuClick}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <TrendingUpIcon sx={{ mr: 2, color: theme.palette.primary.main }} />
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          智能交易机器人
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* 系统状态指示器 */}
          <Chip
            label="系统运行中"
            color="success"
            size="small"
            variant="outlined"
          />

          {/* 通知按钮 */}
          <IconButton color="inherit">
            <NotificationsIcon />
          </IconButton>

          {/* 用户头像 */}
          <IconButton color="inherit">
            <AccountCircleIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Header