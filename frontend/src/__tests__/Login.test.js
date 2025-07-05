import { render, screen } from '@testing-library/react';
import Login from '../components/Login';

test('renders Sign In heading', () => {
  render(<Login />);
  expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument();
});
