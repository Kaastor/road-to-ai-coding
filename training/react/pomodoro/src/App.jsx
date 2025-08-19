import { useState } from 'react'
import PomodoroTimer from './components/PomodoroTimer'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Pomodoro Timer</h1>
        <PomodoroTimer />
      </header>
    </div>
  )
}

export default App