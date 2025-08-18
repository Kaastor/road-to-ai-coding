import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { BinaryInput } from './BinaryInput'

describe('BinaryInput Component', () => {
  it('renders binary input field with label', () => {
    render(<BinaryInput />)
    
    expect(screen.getByLabelText(/binary input/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/enter binary digits/i)).toBeInTheDocument()
  })

  it('accepts up to 8 binary digits', async () => {
    const user = userEvent.setup()
    const onBinaryChange = vi.fn()
    
    render(<BinaryInput onBinaryChange={onBinaryChange} />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    await user.type(input, '10110101')
    
    expect(input).toHaveValue('10110101')
    expect(onBinaryChange).toHaveBeenLastCalledWith('10110101')
  })

  it('limits input to exactly 8 characters', async () => {
    const user = userEvent.setup()
    const onBinaryChange = vi.fn()
    
    render(<BinaryInput onBinaryChange={onBinaryChange} />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    // Try to enter more than 8 characters
    await user.type(input, '101101011001')
    
    // Should only contain first 8 characters
    expect(input).toHaveValue('10110101')
    expect(onBinaryChange).toHaveBeenLastCalledWith('10110101')
  })

  it('only accepts binary digits (0 and 1)', async () => {
    const user = userEvent.setup()
    const onBinaryChange = vi.fn()
    
    render(<BinaryInput onBinaryChange={onBinaryChange} />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    // Try to enter non-binary characters
    await user.type(input, '1a0b2c3d4e5f6g7h8i9j')
    
    // Should only contain valid binary digits
    expect(input).toHaveValue('10')
    expect(onBinaryChange).toHaveBeenLastCalledWith('10')
  })

  it('handles empty input', () => {
    const onBinaryChange = vi.fn()
    
    render(<BinaryInput onBinaryChange={onBinaryChange} />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    expect(input).toHaveValue('')
    // onBinaryChange is not called initially, only on actual changes
  })

  it('updates state on every valid character input', async () => {
    const user = userEvent.setup()
    const onBinaryChange = vi.fn()
    
    render(<BinaryInput onBinaryChange={onBinaryChange} />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    await user.type(input, '1')
    expect(onBinaryChange).toHaveBeenCalledWith('1')
    
    await user.type(input, '0')
    expect(onBinaryChange).toHaveBeenCalledWith('10')
    
    await user.type(input, '1')
    expect(onBinaryChange).toHaveBeenCalledWith('101')
  })

  it('prevents input beyond 8 characters by truncating', async () => {
    const user = userEvent.setup()
    
    render(<BinaryInput />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    // Type exactly 8 characters first
    await user.type(input, '11110000')
    expect(input).toHaveValue('11110000')
    
    // Try to add more characters
    await user.type(input, '1111')
    
    // Should still be 8 characters
    expect(input).toHaveValue('11110000')
  })

  it('handles mixed invalid and valid characters correctly', async () => {
    const user = userEvent.setup()
    const onBinaryChange = vi.fn()
    
    render(<BinaryInput onBinaryChange={onBinaryChange} />)
    
    const input = screen.getByLabelText(/binary input/i)
    
    // Simulate copy-paste of mixed content
    fireEvent.change(input, { target: { value: '1a0b1c0d1e0f1g0h1i' } })
    
    // Should extract only binary digits and limit to 8
    expect(input).toHaveValue('10101010')
    expect(onBinaryChange).toHaveBeenLastCalledWith('10101010')
  })

  describe('Error Message Display', () => {
    it('shows error message for invalid character "2"', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      await user.type(input, '2')
      
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid character(s): "2". Only 0 and 1 are allowed.')
      expect(input).toHaveValue('')
    })

    it('shows error message for invalid character "a"', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      await user.type(input, 'a')
      
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid character(s): "a". Only 0 and 1 are allowed.')
      expect(input).toHaveValue('')
    })

    it('shows error message for multiple invalid characters', async () => {
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Simulate paste operation with multiple invalid characters
      fireEvent.change(input, { target: { value: '2a3b' } })
      
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid character(s): "2, a, 3, b". Only 0 and 1 are allowed.')
      expect(input).toHaveValue('')
    })

    it('clears error message when valid input is entered', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // First enter invalid character
      await user.type(input, 'x')
      expect(screen.getByRole('alert')).toBeInTheDocument()
      
      // Clear input and enter valid characters
      await user.clear(input)
      await user.type(input, '101')
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      expect(input).toHaveValue('101')
    })

    it('shows error for mixed valid/invalid characters', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Mix valid and invalid characters
      fireEvent.change(input, { target: { value: '1a0b2' } })
      
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid character(s): "a, b, 2". Only 0 and 1 are allowed.')
      expect(input).toHaveValue('10')
    })
  })

  describe('Edge Cases', () => {
    it('handles leading and trailing spaces', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Spaces should be trimmed, no error for valid binary
      fireEvent.change(input, { target: { value: '  101  ' } })
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      expect(input).toHaveValue('101')
    })

    it('shows error for spaces mixed with invalid characters', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Spaces will be trimmed, but invalid chars should show error
      fireEvent.change(input, { target: { value: '  1a0  ' } })
      
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid character(s): "a". Only 0 and 1 are allowed.')
      expect(input).toHaveValue('10')
    })


    it('handles paste operation with mixed content', () => {
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Simulate paste with mixed valid/invalid content
      fireEvent.change(input, { target: { value: '1x0y1z0' } })
      
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid character(s): "x, y, z". Only 0 and 1 are allowed.')
      expect(input).toHaveValue('1010')
    })

    it('does not show error for empty input initially', () => {
      render(<BinaryInput />)
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility and UI', () => {
    it('applies error styling when invalid input is entered', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      await user.type(input, 'x')
      
      expect(input).toHaveAttribute('aria-invalid', 'true')
      expect(input).toHaveAttribute('aria-describedby', 'binary-input-error')
      expect(input).toHaveStyle('border-color: #dc3545')
    })

    it('removes error styling when input becomes valid', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Enter invalid input
      await user.type(input, 'x')
      expect(input).toHaveAttribute('aria-invalid', 'true')
      
      // Clear and enter valid input
      await user.clear(input)
      await user.type(input, '101')
      
      expect(input).toHaveAttribute('aria-invalid', 'false')
      expect(input).not.toHaveAttribute('aria-describedby')
    })

    it('error message has proper accessibility attributes', async () => {
      const user = userEvent.setup()
      
      render(<BinaryInput />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      await user.type(input, 'x')
      
      const errorMessage = screen.getByRole('alert')
      expect(errorMessage).toHaveAttribute('id', 'binary-input-error')
      expect(errorMessage).toHaveAttribute('role', 'alert')
      expect(errorMessage).toHaveAttribute('aria-live', 'polite')
    })

    it('maintains normal functionality while showing errors', async () => {
      const user = userEvent.setup()
      const onBinaryChange = vi.fn()
      
      render(<BinaryInput onBinaryChange={onBinaryChange} />)
      
      const input = screen.getByLabelText(/binary input/i)
      
      // Enter mixed valid/invalid input
      fireEvent.change(input, { target: { value: '1a0b1' } })
      
      // Error should show but callback should still work with valid part
      expect(screen.getByRole('alert')).toBeInTheDocument()
      expect(input).toHaveValue('101')
      expect(onBinaryChange).toHaveBeenLastCalledWith('101')
    })
  })
})