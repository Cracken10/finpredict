import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../auth-context';
import {
  Box, Typography, TextField, Button,
  Alert, Link, CircularProgress
} from '@mui/material';

export default function Auth(){
  const { login, showSnackbar } = useAuth();
  const [mode, setMode]     = useState('login');
  const [user, setUser]     = useState('');
  const [pass, setPass]     = useState('');
  const [error, setError]   = useState('');
  const [loading, setLoading]= useState(false);

  const validatePassword = pw => {
    const errs = [];
    if (pw.length<8) errs.push('≥8 caracteres');
    if (!/[A-Z]/.test(pw)) errs.push('1 mayúscula');
    if (!/[0-9]/.test(pw)) errs.push('1 número');
    return errs;
  };

  const handle = async () => {
    setError('');
    if (mode==='register') {
      const errs = validatePassword(pass);
      if (errs.length) return setError(`Req: ${errs.join(', ')}`);
      try {
        const { data } = await axios.post('/api/auth/register',{
          username:user, password:pass
        });
        showSnackbar(data.msg,'success');
        setMode('login');
      } catch(e) {
        setError(e.response?.data?.detail||e.message);
      }
      return;
    }
    setLoading(true);
    try { await login(user,pass) }
    catch(e){ setError(e.response?.data?.detail||e.message) }
    finally{ setLoading(false) }
  };

  return (
    <Box component="form" onSubmit={e=>{e.preventDefault();handle();}}
         sx={{ maxWidth:400,mx:'auto',mt:8,p:3,boxShadow:3,borderRadius:2,bgcolor:'background.paper' }}>
      <Typography variant="h5" align="center" gutterBottom>
        {mode==='login'?'Iniciar Sesión':'Registrarse'}
      </Typography>
      {error && <Alert severity="error" sx={{ mb:2 }}>{error}</Alert>}
      <TextField
        label="Usuario" fullWidth value={user}
        onChange={e=>setUser(e.target.value)} sx={{ mb:2 }}
      />
      <TextField
        label="Contraseña" type="password" fullWidth value={pass}
        onChange={e=>setPass(e.target.value)} sx={{ mb:1 }}
        error={!!error && mode==='register'}
        helperText={mode==='register' && validatePassword(pass).length>0
          ? `Req: ${validatePassword(pass).join(', ')}` : ''}
      />
      <Button
        type="submit" variant="contained" fullWidth
        disabled={loading||!user||!pass} sx={{ mb:2 }}
      >
        {loading ? <CircularProgress size={24}/> : (mode==='login'?'Entrar':'Crear Cuenta')}
      </Button>
      <Typography align="center">
        <Link component="button" onClick={()=>setMode(m=>m==='login'?'register':'login')}>
          {mode==='login'?'¿No tienes cuenta?':'¿Ya tienes cuenta?'}
        </Link>
      </Typography>
    </Box>
  );
}
