from typing import Dict, List, Optional


class RomanNumeralValueMapping:
    """Simple symbol-to-value dictionary for Roman numerals."""
    
    @staticmethod
    def get_basic_values() -> Dict[str, int]:
        """Get basic Roman numeral symbol values."""
        return {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }
    
    @staticmethod
    def get_subtraction_pairs() -> Dict[str, int]:
        """Get valid subtraction pair values."""
        return {
            'IV': 4,
            'IX': 9,
            'XL': 40,
            'XC': 90,
            'CD': 400,
            'CM': 900
        }


class SubtractionRuleValidator:
    """Handle IV, IX, XL, XC, CD, CM patterns validation."""
    
    def __init__(self):
        self._valid_pairs = RomanNumeralValueMapping.get_subtraction_pairs()
    
    def validate(self, roman: str) -> bool:
        """Validate subtraction rules in Roman numeral string."""
        i = 0
        used_pairs = []
        
        while i < len(roman) - 1:
            pair = roman[i:i+2]
            if pair in self._valid_pairs:
                if pair in used_pairs:
                    return False
                used_pairs.append(pair)
                i += 2
            else:
                if i < len(roman) - 1:
                    current_val = RomanNumeralValueMapping.get_basic_values().get(roman[i], 0)
                    next_val = RomanNumeralValueMapping.get_basic_values().get(roman[i+1], 0)
                    if current_val < next_val:
                        return False
                i += 1
        
        return True


class RepetitionRuleValidator:
    """Max 3 consecutive, V/L/D no repeats validation."""
    
    def validate(self, roman: str) -> bool:
        """Validate repetition rules."""
        no_repeat_symbols = {'V', 'L', 'D'}
        
        for symbol in no_repeat_symbols:
            if roman.count(symbol) > 1:
                return False
        
        consecutive_count = 1
        for i in range(1, len(roman)):
            if roman[i] == roman[i-1]:
                consecutive_count += 1
                if consecutive_count > 3:
                    return False
            else:
                consecutive_count = 1
        
        return True


class ConversionAlgorithm:
    """Transform valid Roman string to integer."""
    
    def __init__(self):
        self._basic_values = RomanNumeralValueMapping.get_basic_values()
        self._subtraction_pairs = RomanNumeralValueMapping.get_subtraction_pairs()
    
    def convert(self, roman: str) -> int:
        """Convert Roman numeral string to integer."""
        result = 0
        i = 0
        
        while i < len(roman):
            if i < len(roman) - 1:
                pair = roman[i:i+2]
                if pair in self._subtraction_pairs:
                    result += self._subtraction_pairs[pair]
                    i += 2
                    continue
            
            result += self._basic_values[roman[i]]
            i += 1
        
        return result


class InputValidation:
    """Orchestrate all validation rules."""
    
    def __init__(self):
        self._subtraction_validator = SubtractionRuleValidator()
        self._repetition_validator = RepetitionRuleValidator()
    
    def validate(self, roman: str) -> bool:
        """Validate Roman numeral string against all rules."""
        if not roman or not isinstance(roman, str):
            return False
        
        roman = roman.upper().strip()
        
        valid_chars = set(RomanNumeralValueMapping.get_basic_values().keys())
        if not all(char in valid_chars for char in roman):
            return False
        
        return (self._subtraction_validator.validate(roman) and 
                self._repetition_validator.validate(roman))


class RomanNumeralCalculator:
    """Main calculator class that orchestrates validation and conversion."""
    
    def __init__(self):
        self._validator = InputValidation()
        self._converter = ConversionAlgorithm()
    
    def calculate(self, roman_input: str) -> Optional[int]:
        """Calculate integer value from Roman numeral string."""
        if not self._validator.validate(roman_input):
            return None
        
        roman_input = roman_input.upper().strip()
        return self._converter.convert(roman_input)


def hello(name: str = "World") -> str:
    """Return a greeting message.
    
    Args:
        name: The name to greet. Defaults to "World".
        
    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"


def main() -> None:
    """Main entry point for the application."""
    calculator = RomanNumeralCalculator()
    
    test_cases = ["III", "CV", "DCXLVIII", "IIII", "VV", "IC"]
    for case in test_cases:
        result = calculator.calculate(case)
        if result is not None:
            print(f"{case} = {result}")
        else:
            print(f"{case} is invalid")


if __name__ == "__main__":
    main()