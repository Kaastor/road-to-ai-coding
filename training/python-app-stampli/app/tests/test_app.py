import pytest
from app.app import hello, IsValid, LetterRule, RuleBasedWordValidator


def test_hello_default():
    assert hello() == "Hello, World!"


def test_hello_name():
    assert hello("Ada") == "Hello, Ada!"


class TestLetterRule:
    """Tests for LetterRule dataclass."""
    
    def test_letter_rule_creation(self):
        rule = LetterRule('a', {'b', 'c'}, True)
        assert rule.letter == 'a'
        assert rule.can_be_followed_by == {'b', 'c'}
        assert rule.can_be_final is True


class TestRuleBasedWordValidator:
    """Tests for RuleBasedWordValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create validator with test rules."""
        rules = {
            'a': LetterRule('a', {'a', 'b', 'd'}, True),
            'b': LetterRule('b', {'a', 'f'}, False),
            'c': LetterRule('c', {'a'}, True),
            'd': LetterRule('d', {'d'}, True),
            'f': LetterRule('f', set(), True),
        }
        return RuleBasedWordValidator(rules)
    
    def test_empty_word(self, validator):
        assert validator.is_valid("") is True
    
    def test_single_letter_valid_final(self, validator):
        assert validator.is_valid("a") is True
        assert validator.is_valid("c") is True
        assert validator.is_valid("d") is True
        assert validator.is_valid("f") is True
    
    def test_single_letter_invalid_final(self, validator):
        assert validator.is_valid("b") is False
    
    def test_unknown_letter(self, validator):
        assert validator.is_valid("x") is False
        assert validator.is_valid("ax") is False
    
    def test_valid_sequences(self, validator):
        assert validator.is_valid("aa") is True
        assert validator.is_valid("ab") is False  # b cannot be final
        assert validator.is_valid("aba") is True
        assert validator.is_valid("baf") is False  # a cannot be followed by f
        assert validator.is_valid("bf") is True    # b->f is valid, f can be final
        assert validator.is_valid("ad") is True
        assert validator.is_valid("add") is True
        assert validator.is_valid("ca") is True
    
    def test_invalid_sequences(self, validator):
        assert validator.is_valid("ac") is False  # c cannot follow a
        assert validator.is_valid("ab") is False  # b cannot be final
        assert validator.is_valid("ba") is True   # but ba is valid since a can be final
        assert validator.is_valid("cb") is False  # b cannot follow c


class TestIsValidAPI:
    """Tests for the IsValid API function."""
    
    @pytest.mark.parametrize("word,expected", [
        ("", True),
        ("a", True),
        ("c", True),
        ("b", False),  # b cannot be final
        ("aba", True),
        ("ab", False),  # b cannot be final
        ("ac", False),  # c cannot follow a
        ("ca", True),
        ("aa", True),
        ("ad", True),
        ("x", False),   # unknown letter
    ])
    def test_is_valid_examples(self, word, expected):
        assert IsValid(word) == expected
    
    def test_example_cases_from_requirements(self):
        """Test the specific examples from the requirements."""
        assert IsValid("ac") is False  # c cannot be after a
        assert IsValid("ab") is False  # b cannot be final
        assert IsValid("aba") is True  # valid sequence
