import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Box,
  Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Divider, Container
} from '@mui/material';
import { Dashboard as DashIcon, ShowChart as ChartIcon } from '@mui/icons-material';
import { useAuth } from '../auth-context';

const menuItems = [
  { text:'Dashboard', path:'/dashboard', icon:<DashIcon/> },
  { text:'Pronósticos', path:'/forecast', icon:<ChartIcon/> }
];

export default function Layout(){
  const { logout } = useAuth();
  const nav = useNavigate(), loc = useLocation();

  return (
    <Box sx={{ display:'flex', minHeight:'100vh' }}>
      <AppBar position="fixed" sx={{ zIndex:t=>t.zIndex.drawer+1 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow:1 }}>FinPredict</Typography>
          <Button color="inherit" onClick={logout}>Cerrar Sesión</Button>
        </Toolbar>
      </AppBar>
      <Drawer variant="permanent" sx={{ width:240,'& .MuiDrawer-paper':{width:240,mt:8} }}>
        <List>
          {menuItems.map(i=>(
            <ListItemButton
              key={i.text}
              selected={loc.pathname===i.path}
              onClick={()=>nav(i.path)}
            >
              <ListItemIcon>{i.icon}</ListItemIcon>
              <ListItemText primary={i.text}/>
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow:1,p:3,mt:8,bgcolor:'background.default' }}>
        <Container maxWidth="lg"><Outlet/></Container>
        <Box component="footer" sx={{ textAlign:'center',py:2,mt:4,bgcolor:'background.paper' }}>
          <Typography variant="body2" color="text.secondary">
            FinPredict © 2025 | Proyecto de Titulación
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
