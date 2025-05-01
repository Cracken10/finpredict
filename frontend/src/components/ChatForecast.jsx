import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import {
  Box, Typography, Card, CardContent,
  TextField, Button, CircularProgress,
  Chip, Alert, Fade
} from '@mui/material';
import { useAuth } from '../auth-context';

export default function ChatForecast(){
  const { showSnackbar } = useAuth();
  const [prompt,setPrompt]   = useState('');
  const [result,setResult]   = useState(null);
  const [loading,setLoading] = useState(false);
  const [error,setError]     = useState('');
  const [history,setHistory] = useState([]);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('predictHistory')||'[]');
    setHistory(saved);
    axios.get('/api/user/predict-history')
      .then(r => {
        setHistory(r.data);
        localStorage.setItem('predictHistory', JSON.stringify(r.data));
      })
      .catch(()=>showSnackbar('No se pudo cargar historial','warning'));
  }, [showSnackbar]);

  const handleSubmit = async () => {
    if (!prompt.trim()){ setError('Ingresa texto'); return; }
    const dm = prompt.match(/(\d+)\s*d[ií]as?/i);
    const days = dm? parseInt(dm[1]) : 5;
    if (days<1||days>365){ setError('Días entre 1 y 365'); return; }
    const tm = prompt.match(/([A-Za-z]{1,5})/);
    if (!tm){ setError('Ticker inválido'); return; }
    setError(''); setLoading(true);

    try {
      const { data } = await axios.post('/api/predict',{ prompt });
      setResult(data);

      const newH = [{
        id:Date.now(),
        ticker:data.ticker,
        days:data.days,
        direction:data.forecast_direction,
        timestamp:new Date().toISOString()
      },...history].slice(0,5);

      setHistory(newH);
      localStorage.setItem('predictHistory', JSON.stringify(newH));
      showSnackbar(`Pronóstico para ${data.ticker}`,'success');
    } catch(e) {
      setError(e.response?.data?.detail||e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display:'flex', flexDirection:'column', gap:4 }}>
      <Typography variant="h4">Pronóstico de Acciones</Typography>

      <Card>
        <CardContent>
          <TextField
            fullWidth
            label="Ej: Pronóstico para AAPL en 5 días"
            value={prompt}
            onChange={e=>setPrompt(e.target.value)}
            error={!!error}
            helperText={error}
            disabled={loading}
          />
          <Box sx={{ mt:2, textAlign:'right' }}>
            <Button variant="contained" onClick={handleSubmit} disabled={loading}>
              {loading ? <CircularProgress size={24}/> : 'Generar'}
            </Button>
          </Box>
          <Box sx={{ mt:2, display:'flex', gap:1, flexWrap:'wrap' }}>
            {history.map(h=>(
              <Chip
                key={h.id}
                label={`${h.ticker} (${h.days}d)`}
                onClick={()=>setPrompt(`Pronóstico para ${h.ticker} en ${h.days} días`)}
                clickable
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {loading && !result && <CircularProgress />}

      {result && result.no_news && (
        <Alert severity="warning">No se encontraron noticias para sentimiento</Alert>
      )}

      <Fade in={!!result} timeout={500}>
        {result && (
          <Card>
            <CardContent>
              <Typography variant="h6">Resumen para {result.ticker}</Typography>
              <Typography>Pronóstico: {result.final_forecast}</Typography>
              <Typography>Dirección: {result.forecast_direction}</Typography>

              {/* Histórico */}
              <Plot
                data={[{
                  x: result.historical_data.dates.map(d =>
                    new Date(d).toLocaleDateString('es-MX')
                  ),
                  y: result.historical_data.prices,
                  type:'scatter', mode:'lines', name:'Histórico'
                }]}
                layout={{
                  title:'Histórico',
                  xaxis:{ title:'Fecha' },
                  yaxis:{ title:'Precio (USD)' },
                  autosize:true, height:300
                }}
                config={{ responsive:true }}
              />

              {/* Pronósticos */}
              <Plot
                data={[
                  { x:result.forecast_data.dates, y:result.forecast_data.arima,  name:'ARIMA',   mode:'lines' },
                  { x:result.forecast_data.dates, y:result.forecast_data.prophet,name:'Prophet', mode:'lines' },
                  { x:result.forecast_data.dates, y:result.forecast_data.lstm,   name:'LSTM',    mode:'lines' }
                ]}
                layout={{
                  title:'Pronósticos',
                  xaxis:{ title:'Fecha' },
                  yaxis:{ title:'Precio (USD)' },
                  autosize:true, height:300
                }}
                config={{ responsive:true }}
              />
            </CardContent>
          </Card>
        )}
      </Fade>
    </Box>
  );
}
