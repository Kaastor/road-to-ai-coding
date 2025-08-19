import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import PomodoroTimer from '../../src/components/PomodoroTimer'

describe('PomodoroTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  test('renders work time initially', () => {
    render(<PomodoroTimer />)
    expect(screen.getByText('Work Time')).toBeInTheDocument()
    expect(screen.getByText('25:00')).toBeInTheDocument()
  })

  test('starts and pauses timer', () => {
    render(<PomodoroTimer />)
    const startButton = screen.getByText('Start')
    
    fireEvent.click(startButton)
    expect(screen.getByText('Pause')).toBeInTheDocument()
    
    fireEvent.click(screen.getByText('Pause'))
    expect(screen.getByText('Start')).toBeInTheDocument()
  })

  test('resets timer to initial state', () => {
    render(<PomodoroTimer />)
    const startButton = screen.getByText('Start')
    const resetButton = screen.getByText('Reset')
    
    fireEvent.click(startButton)
    vi.advanceTimersByTime(1000)
    
    fireEvent.click(resetButton)
    expect(screen.getByText('Start')).toBeInTheDocument()
    expect(screen.getByText('25:00')).toBeInTheDocument()
    expect(screen.getByText('Work Time')).toBeInTheDocument()
  })

  test('counts down time correctly', () => {
    render(<PomodoroTimer />)
    const startButton = screen.getByText('Start')
    
    fireEvent.click(startButton)
    vi.advanceTimersByTime(1000)
    
    expect(screen.getByText('24:59')).toBeInTheDocument()
  })
})