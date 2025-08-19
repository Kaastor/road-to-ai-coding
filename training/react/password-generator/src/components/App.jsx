import React, { useState } from 'react';
import PasswordLengthSelector from './PasswordLengthSelector';

const App = () => {
  const [passwordLength, setPasswordLength] = useState(12);
  const [characterSets, setCharacterSets] = useState({
    uppercase: true,
    lowercase: true,
    numbers: true,
    symbols: false
  });

  const handleLengthChange = (newLength) => {
    setPasswordLength(newLength);
  };

  const handleCharacterSetChange = (type) => {
    setCharacterSets(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  return (
    <div>
      <h1>Password Generator</h1>
      <p>Generate passwords based on your selected characteristics</p>
      <PasswordLengthSelector 
        length={passwordLength}
        onLengthChange={handleLengthChange}
      />
      <div>
        <h3>Character Sets</h3>
        <label>
          <input
            type="checkbox"
            checked={characterSets.uppercase}
            onChange={() => handleCharacterSetChange('uppercase')}
          />
          Include uppercase letters (A-Z)
        </label>
        <label>
          <input
            type="checkbox"
            checked={characterSets.lowercase}
            onChange={() => handleCharacterSetChange('lowercase')}
          />
          Include lowercase letters (a-z)
        </label>
        <label>
          <input
            type="checkbox"
            checked={characterSets.numbers}
            onChange={() => handleCharacterSetChange('numbers')}
          />
          Include numbers (0-9)
        </label>
        <label>
          <input
            type="checkbox"
            checked={characterSets.symbols}
            onChange={() => handleCharacterSetChange('symbols')}
          />
          Include symbols (!@#$%)
        </label>
      </div>
    </div>
  );
};

export default App;