import { render, screen, fireEvent } from '@testing-library/react';
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

  it('renders password length selector with default value', () => {
    render(<App />);
    expect(screen.getByText('Password Length: 12')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toHaveValue('12');
  });

  it('updates password length when slider changes', () => {
    render(<App />);
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '16' } });
    
    expect(screen.getByText('Password Length: 16')).toBeInTheDocument();
  });

  it('renders character set checkboxes with default values', () => {
    render(<App />);
    
    expect(screen.getByLabelText('Include uppercase letters (A-Z)')).toBeChecked();
    expect(screen.getByLabelText('Include lowercase letters (a-z)')).toBeChecked();
    expect(screen.getByLabelText('Include numbers (0-9)')).toBeChecked();
    expect(screen.getByLabelText('Include symbols (!@#$%)')).not.toBeChecked();
  });

  it('toggles character set checkboxes when clicked', () => {
    render(<App />);
    
    const symbolsCheckbox = screen.getByLabelText('Include symbols (!@#$%)');
    const uppercaseCheckbox = screen.getByLabelText('Include uppercase letters (A-Z)');
    
    fireEvent.click(symbolsCheckbox);
    expect(symbolsCheckbox).toBeChecked();
    
    fireEvent.click(uppercaseCheckbox);
    expect(uppercaseCheckbox).not.toBeChecked();
  });

  it('renders Generate password button', () => {
    render(<App />);
    expect(screen.getByText('Generate password')).toBeInTheDocument();
  });

  it('generates and displays password when Generate button is clicked', () => {
    render(<App />);
    
    const generateButton = screen.getByText('Generate password');
    fireEvent.click(generateButton);
    
    expect(screen.getByText('Generated Password:')).toBeInTheDocument();
    const passwordElement = screen.getByText('Generated Password:').nextSibling;
    expect(passwordElement.textContent).toHaveLength(12);
  });

  it('does not display password initially', () => {
    render(<App />);
    expect(screen.queryByText('Generated Password:')).not.toBeInTheDocument();
  });
});