import React from 'react';

const PasswordLengthSelector = ({ length, onLengthChange, minLength = 8, maxLength = 50 }) => {
  const handleLengthChange = (event) => {
    const newLength = parseInt(event.target.value, 10);
    const clampedLength = Math.max(minLength, Math.min(maxLength, newLength));
    onLengthChange(clampedLength);
  };

  return (
    <div>
      <label htmlFor="password-length">
        Password Length: {length}
      </label>
      <input
        type="range"
        id="password-length"
        min={minLength}
        max={maxLength}
        value={length}
        onChange={handleLengthChange}
      />
      <div>
        <span>{minLength}</span>
        <span style={{ float: 'right' }}>{maxLength}</span>
      </div>
    </div>
  );
};

export default PasswordLengthSelector;