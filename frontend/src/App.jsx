import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './auth-context';

export default function App(){
  const { token } = useAuth();
  return token
    ? <Navigate to="/dashboard" replace/>
    : <Navigate to="/auth"      replace/>;
}
