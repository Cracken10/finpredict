import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box, Typography, Button, Grid, Card, CardHeader,
  CardContent, List, ListItem, ListItemText,
  Divider, Avatar, CircularProgress, Alert
} from '@mui/material';
import { ShowChart, TrendingUp, TrendingDown } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export default function Dashboard(){
  const nav = useNavigate();
  const [recent, setRecent] = useState(null);
  const [err, setErr]       = useState('');

  useEffect(() => {
    axios.get('/api/user/predict-history')
      .then(r => setRecent(r.data))
      .catch(()=>{
        setErr('No se cargó historial');
        setRecent([]);
      });
  }, []);

  if (recent === null) return <CircularProgress/>;

  return (
    <Box>
      <Box sx={{ display:'flex', justifyContent:'space-between', mb:4 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Button variant="contained" startIcon={<ShowChart/>}
                onClick={()=>nav('/forecast')}>
          Nuevo Pronóstico
        </Button>
      </Box>

      {err && <Alert severity="warning">{err}</Alert>}

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Pronósticos Recientes" />
            <Divider/>
            <CardContent>
              <List>
                {recent.map((p,i)=>(
                  <React.Fragment key={p.id}>
                    <ListItem>
                      <Avatar sx={{ mr:2 }}>{p.ticker[0]}</Avatar>
                      <ListItemText
                        primary={`${p.ticker} (${p.days} días)`}
                        secondary={new Date(p.timestamp).toLocaleDateString('es-MX')}
                      />
                      {p.direction==='Subir'
                        ? <TrendingUp color="success"/>
                        : <TrendingDown color="error"/>
                      }
                    </ListItem>
                    {i < recent.length-1 && <Divider/>}
                  </React.Fragment>
                ))}
                {recent.length===0 && (
                  <Typography color="text.secondary">Sin pronósticos</Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
