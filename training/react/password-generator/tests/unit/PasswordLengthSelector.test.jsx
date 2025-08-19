import { fireEvent, render, screen } from '@testing-library/react';
import PasswordLengthSelector from '../../src/components/PasswordLengthSelector';

describe('PasswordLengthSelector', () => {
  const mockOnLengthChange = vi.fn();

  beforeEach(() => {
    mockOnLengthChange.mockClear();
  });

  it('renders with default props', () => {
    render(<PasswordLengthSelector length={12} onLengthChange={mockOnLengthChange} />);

    expect(screen.getByLabelText(/Password Length: 12/)).toBeInTheDocument();
    expect(screen.getByRole('slider')).toHaveValue('12');
  });

  it('displays custom length value', () => {
    render(<PasswordLengthSelector length={20} onLengthChange={mockOnLengthChange} />);

    expect(screen.getByText('Password Length: 20')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toHaveValue('20');
  });

  it('calls onLengthChange when slider value changes', () => {
    render(<PasswordLengthSelector length={12} onLengthChange={mockOnLengthChange} />);

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '16' } });

    expect(mockOnLengthChange).toHaveBeenCalledWith(16);
  });

  it('uses custom min and max values', () => {
    render(
      <PasswordLengthSelector
        length={8}
        onLengthChange={mockOnLengthChange}
        minLength={6}
        maxLength={30}
      />
    );

    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('min', '6');
    expect(slider).toHaveAttribute('max', '30');
    expect(screen.getByText('6')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
  });

  it('uses default min and max values when not provided', () => {
    render(<PasswordLengthSelector length={12} onLengthChange={mockOnLengthChange} />);

    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('min', '8');
    expect(slider).toHaveAttribute('max', '50');
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });

  it('clamps values to minimum limit', () => {
    render(<PasswordLengthSelector length={12} onLengthChange={mockOnLengthChange} />);

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '5' } });

    expect(mockOnLengthChange).toHaveBeenCalledWith(8);
  });

  it('clamps values to maximum limit', () => {
    render(<PasswordLengthSelector length={12} onLengthChange={mockOnLengthChange} />);

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '55' } });

    expect(mockOnLengthChange).toHaveBeenCalledWith(50);
  });
});