import React, { useEffect, useState } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { initializeApp } from 'firebase/app';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Layout from './components/Layout';
import axios from 'axios';
import {
  registerUserIfNeeded,
  fetchUserFromServer,
} from './services/authService';

// Firebase auth instance will be created after fetching config
let auth = null;

// Auth Context
export const AuthContext = React.createContext();

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authInstance, setAuthInstance] = useState(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const { data } = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/config/firebase`,
        );
        const app = initializeApp(data);
        auth = getAuth(app);
        setAuthInstance(auth);
      } catch (err) {
        console.error('Failed to load Firebase config', err);
        setLoading(false);
      }
    };
    fetchConfig();
  }, []);

  useEffect(() => {
    if (!authInstance) return;
    const unsubscribe = onAuthStateChanged(
      authInstance,
      async (firebaseUser) => {
        if (firebaseUser) {
          try {
            // Get user token
            const token = await firebaseUser.getIdToken();

            // Set axios default header
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

            await registerUserIfNeeded(firebaseUser);
            const userData = await fetchUserFromServer();
            setUser(userData);
          } catch (error) {
            console.error('Error setting up user:', error);
            setUser(null);
          }
        } else {
          setUser(null);
          delete axios.defaults.headers.common['Authorization'];
        }
        setLoading(false);
      },
    );

    return unsubscribe;
  }, [authInstance]);

  return (
    <AuthContext.Provider value={{ user, loading, auth: authInstance }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = React.useContext(AuthContext);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return user ? <Layout>{children}</Layout> : <Navigate to="/login" />;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;
