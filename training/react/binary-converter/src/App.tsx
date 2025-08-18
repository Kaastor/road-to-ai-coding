import { useState } from 'react'
import './App.css'
import { BinaryInput } from './components/BinaryInput'
import { DecimalOutput } from './components/DecimalOutput'

function App() {
  const [binaryValue, setBinaryValue] = useState('')

  return (
    <div className="App">
      <h1>Binary Converter</h1>
      <div className="card">
        <BinaryInput onBinaryChange={setBinaryValue} />
        <DecimalOutput binaryValue={binaryValue} />
        <p>Current binary value: {binaryValue}</p>
      </div>
    </div>
  )
}

export default App