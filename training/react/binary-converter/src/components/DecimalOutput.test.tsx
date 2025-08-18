import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DecimalOutput } from './DecimalOutput'

describe('DecimalOutput Component', () => {
  it('renders decimal output field with label', () => {
    render(<DecimalOutput binaryValue="" />)
    
    expect(screen.getByLabelText(/decimal output/i)).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveAttribute('readonly')
  })

  it('converts valid binary to decimal - "111" -> 7', () => {
    render(<DecimalOutput binaryValue="111" />)
    
    const output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('7')
  })

  it('converts "0" -> 0', () => {
    render(<DecimalOutput binaryValue="0" />)
    
    const output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('0')
  })

  it('converts "1" -> 1', () => {
    render(<DecimalOutput binaryValue="1" />)
    
    const output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('1')
  })

  it('converts all 1s (8 bits) "11111111" -> 255', () => {
    render(<DecimalOutput binaryValue="11111111" />)
    
    const output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('255')
  })

  it('shows 0 for empty input', () => {
    render(<DecimalOutput binaryValue="" />)
    
    const output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('0')
  })

  it('shows 0 for whitespace-only input', () => {
    render(<DecimalOutput binaryValue="   " />)
    
    const output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('0')
  })

  it('updates when binary input changes', () => {
    const { rerender } = render(<DecimalOutput binaryValue="101" />)
    
    let output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('5')
    
    rerender(<DecimalOutput binaryValue="1010" />)
    
    output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('10')
  })

  it('converts other valid binary strings correctly', () => {
    const { rerender } = render(<DecimalOutput binaryValue="1100" />)
    
    let output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('12')
    
    rerender(<DecimalOutput binaryValue="10110" />)
    
    output = screen.getByLabelText(/decimal output/i)
    expect(output).toHaveValue('22')
  })
})