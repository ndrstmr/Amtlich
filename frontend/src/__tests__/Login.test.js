import React from 'react';
import { render, screen } from '@testing-library/react';
import Login from '../components/Login';

// Mock AuthContext to avoid loading App.js and its router dependencies
jest.mock('../App', () => {
  const React = require('react');
  return { AuthContext: React.createContext({ auth: {} }) };
});

test('renders Sign In heading', () => {
  render(<Login />);
  expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument();
});
