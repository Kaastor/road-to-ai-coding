import { useState, useEffect } from 'react'

const PomodoroTimer = () => {
  const [timeLeft, setTimeLeft] = useState(25 * 60) // 25 minutes in seconds
  const [isActive, setIsActive] = useState(false)
  const [isWork, setIsWork] = useState(true) // true for work, false for break

  useEffect(() => {
    let interval = null
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1)
      }, 1000)
    } else if (timeLeft === 0) {
      setIsWork(!isWork)
      setTimeLeft(isWork ? 5 * 60 : 25 * 60) // Switch between work (25min) and break (5min)
      setIsActive(false)
    }
    return () => clearInterval(interval)
  }, [isActive, timeLeft, isWork])

  const toggle = () => {
    setIsActive(!isActive)
  }

  const stop = () => {
    setIsActive(false)
    setTimeLeft(isWork ? 25 * 60 : 5 * 60) // Reset to current session duration
  }

  const reset = () => {
    setIsActive(false)
    setIsWork(true)
    setTimeLeft(25 * 60)
  }

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="pomodoro-timer">
      <div className="timer-display">
        <h2>{isWork ? 'Work Time' : 'Break Time'}</h2>
        <div className="time">{formatTime(timeLeft)}</div>
      </div>
      <div className="timer-controls">
        <button onClick={toggle}>
          {isActive ? 'Pause' : 'Start'}
        </button>
        <button onClick={stop}>Stop</button>
        <button onClick={reset}>Reset</button>
      </div>
    </div>
  )
}

export default PomodoroTimer