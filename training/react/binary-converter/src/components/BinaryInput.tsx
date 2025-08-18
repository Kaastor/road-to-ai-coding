import { useState, ChangeEvent } from 'react'

interface BinaryInputProps {
  onBinaryChange?: (value: string) => void
}

export function BinaryInput({ onBinaryChange }: BinaryInputProps) {
  const [binaryValue, setBinaryValue] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const rawInput = e.target.value
    const input = rawInput.trim()
    
    // Clear error if input is empty (after trimming)
    if (input.length === 0) {
      setErrorMessage('')
    } else {
      // Check for invalid characters before filtering
      const invalidChars = input.match(/[^01]/g)
      
      if (invalidChars) {
        setErrorMessage(`Invalid character(s): "${invalidChars.join(', ')}". Only 0 and 1 are allowed.`)
      } else {
        setErrorMessage('')
      }
    }
    
    // Only allow binary digits (0 and 1) - use trimmed input
    const binaryOnly = input.replace(/[^01]/g, '')
    
    // Limit to 8 characters
    const limitedValue = binaryOnly.slice(0, 8)
    
    setBinaryValue(limitedValue)
    onBinaryChange?.(limitedValue)
  }

  const hasError = errorMessage.length > 0

  return (
    <div>
      <label htmlFor="binary-input">Binary Input (8 digits max):</label>
      <input
        id="binary-input"
        type="text"
        value={binaryValue}
        onChange={handleChange}
        placeholder="Enter binary digits (0 or 1)"
        maxLength={8}
        aria-invalid={hasError}
        aria-describedby={hasError ? "binary-input-error" : undefined}
        style={{
          borderColor: hasError ? '#dc3545' : undefined,
          borderWidth: hasError ? '2px' : undefined,
        }}
      />
      {hasError && (
        <div
          id="binary-input-error"
          role="alert"
          aria-live="polite"
          style={{
            color: '#dc3545',
            fontSize: '0.875rem',
            marginTop: '4px',
          }}
        >
          {errorMessage}
        </div>
      )}
    </div>
  )
}