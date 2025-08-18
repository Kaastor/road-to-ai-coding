import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders binary converter heading', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /binary converter/i })).toBeInTheDocument()
  })

  it('renders binary input field', () => {
    render(<App />)
    expect(screen.getByLabelText(/binary input \(8 digits max\)/i)).toBeInTheDocument()
  })

  it('renders decimal output field', () => {
    render(<App />)
    expect(screen.getByLabelText(/decimal output/i)).toBeInTheDocument()
  })

  it('renders current binary value display', () => {
    render(<App />)
    expect(screen.getByText(/current binary value:/i)).toBeInTheDocument()
  })
})