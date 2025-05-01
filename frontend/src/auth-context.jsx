import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Snackbar, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken]         = useState(localStorage.getItem('accessToken'));
  const [refreshToken, setRToken] = useState(localStorage.getItem('refreshToken'));
  const [snack, setSnack]         = useState({ open:false, msg:'', sev:'info' });
  const navigate = useNavigate();

  const showSnackbar = (msg, sev='info') => setSnack({ open:true, msg, sev });

  const login = useCallback(async (username, password) => {
    const { data } = await axios.post('/api/auth/login',{ username, password });
    setToken(data.access_token);
    setRToken(data.refresh_token);
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
  }, []);

  const logout = useCallback(async () => {
    await axios.post('/api/auth/logout');
    setToken(null);
    setRToken(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];
    navigate('/auth');
  }, [navigate]);

  const refresh = useCallback(async () => {
    const { data } = await axios.post('/api/auth/refresh',{ token: refreshToken });
    setToken(data.access_token);
    setRToken(data.refresh_token);
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
  }, [refreshToken]);

  useEffect(() => {
    if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    const i = axios.interceptors.response.use(
      res => res,
      async err => {
        const orig = err.config;
        if (err.response?.status === 401 && refreshToken && !orig._retry) {
          orig._retry = true;
          try { await refresh(); return axios(orig); }
          catch { await logout(); showSnackbar('Sesión expirada','error'); }
        }
        return Promise.reject(err);
      }
    );
    return () => axios.interceptors.response.eject(i);
  }, [token, refreshToken, refresh, logout, showSnackbar]);

  return (
    <AuthContext.Provider value={{ token, login, logout, showSnackbar }}>
      {children}
      <Snackbar open={snack.open} autoHideDuration={4000}
                onClose={() => setSnack(s=>({...s,open:false}))}>
        <Alert severity={snack.sev}>{snack.msg}</Alert>
      </Snackbar>
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
