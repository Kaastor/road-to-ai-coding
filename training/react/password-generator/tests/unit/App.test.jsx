import { render, screen } from '@testing-library/react';
import App from '../../src/components/App';

describe('App', () => {
  it('renders password generator heading', () => {
    render(<App />);
    expect(screen.getByText('Password Generator')).toBeInTheDocument();
  });

  it('renders description text', () => {
    render(<App />);
    expect(screen.getByText('Generate passwords based on your selected characteristics')).toBeInTheDocument();
  });
});