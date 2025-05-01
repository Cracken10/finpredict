import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';

import theme from './theme';
import { AuthProvider, useAuth } from './auth-context';
import App from './App';
import Layout from './components/Layout';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import ChatForecast from './components/ChatForecast';

function Protected({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/auth" replace />;
}

ReactDOM.render(
  <ThemeProvider theme={theme}>
    <CssBaseline/>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"     element={<App/>}/>
          <Route path="/auth" element={<Auth/>}/>
          <Route path="/*"    element={<Protected><Layout/></Protected>}>
            <Route index element={<Navigate to="dashboard" replace/>}/>
            <Route path="dashboard" element={<Dashboard/>}/>
            <Route path="forecast"   element={<ChatForecast/>}/>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </ThemeProvider>,
  document.getElementById('root')
);
