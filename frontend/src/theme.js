import { createTheme } from '@mui/material/styles';

export default createTheme({
  palette: {
    primary:   { main: '#1976d2' },
    secondary: { main: '#4caf50' },
    background:{ default: '#f5f5f5', paper: '#ffffff' },
    text:      { primary: '#333333', secondary: '#666666' }
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h1: { fontSize: '2rem', fontWeight: 500 },
    h2: { fontSize: '1.5rem', fontWeight: 400 },
    body1:{ fontSize: '1rem' }
  }
});
