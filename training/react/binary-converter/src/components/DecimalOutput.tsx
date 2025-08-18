interface DecimalOutputProps {
  binaryValue: string
}

export function DecimalOutput({ binaryValue }: DecimalOutputProps) {
  const convertToDecimal = (binary: string): number => {
    if (!binary || binary.trim() === '') {
      return 0
    }
    
    const decimal = parseInt(binary, 2)
    return isNaN(decimal) ? 0 : decimal
  }

  const decimalValue = convertToDecimal(binaryValue)

  return (
    <div>
      <label htmlFor="decimal-output">Decimal Output:</label>
      <input
        id="decimal-output"
        type="text"
        value={decimalValue}
        readOnly
        aria-label="Decimal equivalent of binary input"
      />
    </div>
  )
}