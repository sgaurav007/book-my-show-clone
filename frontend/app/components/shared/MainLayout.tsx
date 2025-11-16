import { AppBar, Toolbar, Typography, Button, Box, Container, IconButton, Drawer, List, ListItem, ListItemButton, ListItemText, Avatar, Menu, MenuItem } from "@mui/material";
import { Link, useNavigate } from "@remix-run/react";
import MenuIcon from "@mui/icons-material/Menu";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import { useState } from "react";
import { useAuth } from "~/hooks/shared/useAuth";
import { APP_NAME } from "~/utils/shared/constants";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleProfileMenuClose();
    navigate("/");
  };

  const menuItems = [
    { label: "Home", path: "/" },
    { label: "Movies", path: "/movies" },
    { label: "Theaters", path: "/theaters" },
  ];

  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: "center" }}>
      <Typography variant="h6" sx={{ my: 2, color: "primary.main" }}>
        {APP_NAME}
      </Typography>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton component={Link} to={item.path} sx={{ textAlign: "center" }}>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="sticky" color="primary">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{
              flexGrow: 0,
              mr: 4,
              textDecoration: "none",
              color: "inherit",
              fontWeight: 700,
            }}
          >
            {APP_NAME}
          </Typography>
          <Box sx={{ flexGrow: 1, display: { xs: "none", sm: "flex" }, gap: 2 }}>
            {menuItems.map((item) => (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                sx={{ color: "white" }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
          <Box>
            {isAuthenticated ? (
              <>
                <IconButton
                  size="large"
                  edge="end"
                  aria-label="account of current user"
                  aria-controls="menu-appbar"
                  aria-haspopup="true"
                  onClick={handleProfileMenuOpen}
                  color="inherit"
                >
                  <Avatar sx={{ width: 32, height: 32, bgcolor: "secondary.main" }}>
                    {user?.firstName?.[0]?.toUpperCase() || <AccountCircleIcon />}
                  </Avatar>
                </IconButton>
                <Menu
                  id="menu-appbar"
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: "bottom",
                    horizontal: "right",
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: "top",
                    horizontal: "right",
                  }}
                  open={Boolean(anchorEl)}
                  onClose={handleProfileMenuClose}
                >
                  <MenuItem onClick={() => { navigate("/profile"); handleProfileMenuClose(); }}>
                    Profile
                  </MenuItem>
                  <MenuItem onClick={() => { navigate("/profile/bookings"); handleProfileMenuClose(); }}>
                    My Bookings
                  </MenuItem>
                  {user?.role === "ADMIN" && (
                    <MenuItem onClick={() => { navigate("/admin/dashboard"); handleProfileMenuClose(); }}>
                      Admin Dashboard
                    </MenuItem>
                  )}
                  <MenuItem onClick={handleLogout}>Logout</MenuItem>
                </Menu>
              </>
            ) : (
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button color="inherit" component={Link} to="/auth/login">
                  Login
                </Button>
                <Button
                  variant="outlined"
                  sx={{ color: "white", borderColor: "white" }}
                  component={Link}
                  to="/auth/register"
                >
                  Register
                </Button>
              </Box>
            )}
          </Box>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: "block", sm: "none" },
          "& .MuiDrawer-paper": { boxSizing: "border-box", width: 240 },
        }}
      >
        {drawer}
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, bgcolor: "background.default" }}>
        {children}
      </Box>
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: "auto",
          backgroundColor: "secondary.main",
          color: "white",
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" align="center">
            © {new Date().getFullYear()} {APP_NAME}. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
