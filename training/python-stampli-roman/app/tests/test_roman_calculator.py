import pytest
from app.app import (
    RomanNumeralValueMapping,
    SubtractionRuleValidator,
    RepetitionRuleValidator,
    ConversionAlgorithm,
    InputValidation,
    RomanNumeralCalculator
)


class TestRomanNumeralValueMapping:
    """Test the value mapping functionality."""
    
    def test_basic_values(self):
        """Test basic Roman numeral values."""
        values = RomanNumeralValueMapping.get_basic_values()
        assert values['I'] == 1
        assert values['V'] == 5
        assert values['X'] == 10
        assert values['L'] == 50
        assert values['C'] == 100
        assert values['D'] == 500
        assert values['M'] == 1000
    
    def test_subtraction_pairs(self):
        """Test subtraction pair values."""
        pairs = RomanNumeralValueMapping.get_subtraction_pairs()
        assert pairs['IV'] == 4
        assert pairs['IX'] == 9
        assert pairs['XL'] == 40
        assert pairs['XC'] == 90
        assert pairs['CD'] == 400
        assert pairs['CM'] == 900


class TestSubtractionRuleValidator:
    """Test subtraction rule validation."""
    
    def setUp(self):
        self.validator = SubtractionRuleValidator()
    
    def test_valid_subtraction_patterns(self):
        """Test valid subtraction patterns."""
        validator = SubtractionRuleValidator()
        assert validator.validate("IV") is True
        assert validator.validate("IX") is True
        assert validator.validate("XL") is True
        assert validator.validate("XC") is True
        assert validator.validate("CD") is True
        assert validator.validate("CM") is True
    
    def test_invalid_subtraction_patterns(self):
        """Test invalid subtraction patterns."""
        validator = SubtractionRuleValidator()
        assert validator.validate("IC") is False
        assert validator.validate("IL") is False
        assert validator.validate("CDCD") is False


class TestRepetitionRuleValidator:
    """Test repetition rule validation."""
    
    def test_valid_repetitions(self):
        """Test valid repetitions."""
        validator = RepetitionRuleValidator()
        assert validator.validate("III") is True
        assert validator.validate("XXX") is True
        assert validator.validate("CCC") is True
    
    def test_invalid_repetitions(self):
        """Test invalid repetitions."""
        validator = RepetitionRuleValidator()
        assert validator.validate("IIII") is False
        assert validator.validate("VV") is False
        assert validator.validate("LL") is False
        assert validator.validate("DD") is False


class TestConversionAlgorithm:
    """Test conversion algorithm."""
    
    def test_basic_conversions(self):
        """Test basic Roman numeral conversions."""
        converter = ConversionAlgorithm()
        assert converter.convert("I") == 1
        assert converter.convert("V") == 5
        assert converter.convert("X") == 10
        assert converter.convert("III") == 3
    
    def test_subtraction_conversions(self):
        """Test subtraction pattern conversions."""
        converter = ConversionAlgorithm()
        assert converter.convert("IV") == 4
        assert converter.convert("IX") == 9
        assert converter.convert("XL") == 40
        assert converter.convert("XC") == 90
        assert converter.convert("CD") == 400
        assert converter.convert("CM") == 900
    
    def test_complex_conversions(self):
        """Test complex Roman numeral conversions."""
        converter = ConversionAlgorithm()
        assert converter.convert("MCMXLIV") == 1944
        assert converter.convert("DCXLVIII") == 648


class TestInputValidation:
    """Test input validation orchestrator."""
    
    def test_valid_inputs(self):
        """Test valid Roman numeral inputs."""
        validator = InputValidation()
        assert validator.validate("III") is True
        assert validator.validate("CV") is True
        assert validator.validate("DCXLVIII") is True
        assert validator.validate("MCMXLIV") is True
    
    def test_invalid_inputs(self):
        """Test invalid Roman numeral inputs."""
        validator = InputValidation()
        assert validator.validate("IIII") is False
        assert validator.validate("VV") is False
        assert validator.validate("IC") is False
        assert validator.validate("") is False
        assert validator.validate("ABC") is False


class TestRomanNumeralCalculator:
    """Test the main calculator functionality."""
    
    def test_valid_calculations(self):
        """Test valid Roman numeral calculations."""
        calculator = RomanNumeralCalculator()
        assert calculator.calculate("III") == 3
        assert calculator.calculate("CV") == 105
        assert calculator.calculate("DCXLVIII") == 648
        assert calculator.calculate("MMDXLIX") == 2549
        assert calculator.calculate("MCMXLIV") == 1944
        assert calculator.calculate("MCMXCIX") == 1999
    
    def test_invalid_calculations(self):
        """Test invalid Roman numeral calculations return None."""
        calculator = RomanNumeralCalculator()
        assert calculator.calculate("IIII") is None
        assert calculator.calculate("VV") is None
        assert calculator.calculate("IC") is None
        assert calculator.calculate("CDCD") is None
        assert calculator.calculate("IL") is None
    
    def test_case_insensitive(self):
        """Test calculator handles lowercase input."""
        calculator = RomanNumeralCalculator()
        assert calculator.calculate("iii") == 3
        assert calculator.calculate("cv") == 105