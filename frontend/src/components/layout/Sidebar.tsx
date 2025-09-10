import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  useTheme,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  SmartToy as SmartToyIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
} from "@mui/icons-material";

interface SidebarProps {
  open: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ open }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  const menuItems = [
    {
      text: "仪表板",
      icon: <DashboardIcon />,
      path: "/",
    },
    {
      text: "交易分析",
      icon: <AnalyticsIcon />,
      path: "/analysis",
    },
    {
      text: "智能体监控",
      icon: <SmartToyIcon />,
      path: "/agents",
    },
    {
      text: "决策历史",
      icon: <HistoryIcon />,
      path: "/history",
    },
  ];

  const drawerWidth = open ? 280 : 80;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
          backgroundColor: theme.palette.background.paper,
          borderRight: `1px solid ${theme.palette.divider}`,
          transition: "width 0.3s ease",
        },
      }}
    >
      <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
        {open ? (
          <Typography variant="h6" sx={{ color: theme.palette.primary.main }}>
            🤖 智能交易系统
          </Typography>
        ) : (
          <Typography variant="h6" sx={{ textAlign: "center" }}>
            🤖
          </Typography>
        )}
      </Box>

      <List sx={{ pt: 1 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  minHeight: 48,
                  justifyContent: open ? "initial" : "center",
                  px: 2.5,
                  backgroundColor: isActive
                    ? theme.palette.action.selected
                    : "transparent",
                  "&:hover": {
                    backgroundColor: theme.palette.action.hover,
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : "auto",
                    justifyContent: "center",
                    color: isActive
                      ? theme.palette.primary.main
                      : theme.palette.text.secondary,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary={item.text}
                    sx={{
                      color: isActive
                        ? theme.palette.primary.main
                        : theme.palette.text.primary,
                      "& .MuiTypography-root": {
                        fontWeight: isActive ? 600 : 400,
                      },
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ mt: "auto" }} />

      <Box sx={{ p: 2 }}>
        <ListItemButton
          sx={{
            minHeight: 48,
            justifyContent: open ? "initial" : "center",
            px: 2.5,
          }}
        >
          <ListItemIcon
            sx={{
              minWidth: 0,
              mr: open ? 3 : "auto",
              justifyContent: "center",
            }}
          >
            <SettingsIcon />
          </ListItemIcon>
          {open && <ListItemText primary="设置" />}
        </ListItemButton>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
