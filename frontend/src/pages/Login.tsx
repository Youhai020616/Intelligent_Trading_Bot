import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  SmartToy,
} from "@mui/icons-material";
import ShaderDemo_ATC from "@/components/ui/atc-shader";

interface LoginProps {
  onLogin?: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    if (error) setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // 模拟登录验证
      if (
        formData.email === "admin@tradingbot.com" &&
        formData.password === "admin123"
      ) {
        // 登录成功，调用回调函数
        if (onLogin) {
          onLogin();
        }
        // 跳转到仪表板
        navigate("/");
      } else {
        setError("邮箱或密码错误");
      }
    } catch (err) {
      setError("登录失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* WebGL Shader Background */}
      <ShaderDemo_ATC />

      {/* Login Form Overlay */}
      <Box
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 10,
          backdropFilter: "blur(2px)",
        }}
      >
        <Paper
          elevation={24}
          sx={{
            p: 4,
            width: "100%",
            maxWidth: 400,
            mx: 2,
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(10px)",
            borderRadius: 3,
            border: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          {/* Logo and Title */}
          <Box sx={{ textAlign: "center", mb: 3 }}>
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                backgroundColor: "primary.main",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                mx: "auto",
                mb: 2,
                boxShadow: 3,
              }}
            >
              <SmartToy sx={{ fontSize: 32, color: "white" }} />
            </Box>
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              fontWeight="bold"
            >
              智能交易机器人
            </Typography>
            <Typography variant="body1" color="text.secondary">
              登录您的账户开始交易
            </Typography>
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="邮箱地址"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="密码"
              name="password"
              type={showPassword ? "text" : "password"}
              value={formData.password}
              onChange={handleChange}
              required
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleTogglePasswordVisibility}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                py: 1.5,
                fontSize: "1.1rem",
                fontWeight: "bold",
                borderRadius: 2,
                background: "linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)",
                boxShadow: "0 3px 5px 2px rgba(33, 150, 243, .3)",
                "&:hover": {
                  background:
                    "linear-gradient(45deg, #1565c0 30%, #1976d2 90%)",
                  transform: "translateY(-2px)",
                  boxShadow: "0 6px 10px 2px rgba(33, 150, 243, .3)",
                },
                transition: "all 0.3s ease",
              }}
            >
              {loading ? "登录中..." : "登录"}
            </Button>
          </Box>

          {/* Demo Credentials */}
          <Box sx={{ mt: 3, p: 2, bgcolor: "grey.50", borderRadius: 2 }}>
            <Typography variant="body2" color="text.secondary" align="center">
              <strong>演示账户：</strong>
              <br />
              邮箱: admin@tradingbot.com
              <br />
              密码: admin123
            </Typography>
          </Box>

          {/* Footer */}
          <Typography
            variant="body2"
            color="text.secondary"
            align="center"
            sx={{ mt: 2 }}
          >
            基于AI的量化交易系统
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};

export default Login;
