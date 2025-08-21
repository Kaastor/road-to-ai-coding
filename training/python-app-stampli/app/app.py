from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Set, List


@dataclass
class LetterRule:
    """Represents a validation rule for a single letter."""
    letter: str
    can_be_followed_by: Set[str]
    can_be_final: bool


class WordValidator(ABC):
    """Abstract interface for word validation."""
    
    @abstractmethod
    def is_valid(self, word: str) -> bool:
        """Check if a word is valid according to the rules."""
        pass


class RuleBasedWordValidator(WordValidator):
    """Validates words based on letter transition and finality rules."""
    
    def __init__(self, rules: Dict[str, LetterRule]):
        """Initialize validator with letter rules.
        
        Args:
            rules: Dictionary mapping letters to their validation rules.
        """
        self._rules = rules
    
    def is_valid(self, word: str) -> bool:
        """Check if a word is valid according to the rules.
        
        Args:
            word: The word to validate.
            
        Returns:
            True if the word is valid, False otherwise.
        """
        if not word:
            return True
        
        for i, letter in enumerate(word):
            if letter not in self._rules:
                return False
            
            rule = self._rules[letter]
            
            # Check if letter can be final (last letter in word)
            if i == len(word) - 1:
                if not rule.can_be_final:
                    return False
            else:
                # Check if next letter is allowed to follow current letter
                next_letter = word[i + 1]
                if next_letter not in rule.can_be_followed_by:
                    return False
        
        return True


def create_default_validator() -> WordValidator:
    """Create a validator with the example rules."""
    rules = {
        'a': LetterRule('a', {'a', 'b', 'd'}, True),
        'b': LetterRule('b', {'a', 'f'}, False),
        'c': LetterRule('c', {'a'}, True),
        'd': LetterRule('d', {'d'}, True),
        'f': LetterRule('f', set(), True),
    }
    return RuleBasedWordValidator(rules)


def IsValid(word: str) -> bool:
    """API function to check if a word is valid.
    
    Args:
        word: The word to validate.
        
    Returns:
        True if the word is valid according to predefined rules, False otherwise.
    """
    validator = create_default_validator()
    return validator.is_valid(word)


def water_in_pool(heights: List[int]) -> int:
    """Calculate how much water can be trapped in a pool with bars.
    
    Given an array of non-negative integers representing the height of bars,
    where each bar has width 1, compute how much water can be trapped.
    
    Args:
        heights: List of non-negative integers representing bar heights.
        
    Returns:
        Total amount of water that can be trapped.
        
    Examples:
        >>> water_in_pool([3, 0, 2, 0, 4])
        7
        >>> water_in_pool([1, 1, 1, 1])
        0
        >>> water_in_pool([1, 2, 3, 4, 3, 2, 1, 1])
        0
        >>> water_in_pool([5, 1, 2, 3, 4, 5, 1, 1])
        10
    """
    if not heights or len(heights) < 3:
        return 0
    
    n = len(heights)
    left_max = [0] * n
    right_max = [0] * n
    
    # Fill left_max array
    left_max[0] = heights[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], heights[i])
    
    # Fill right_max array
    right_max[n - 1] = heights[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], heights[i])
    
    # Calculate water trapped
    water = 0
    for i in range(n):
        water_level = min(left_max[i], right_max[i])
        if water_level > heights[i]:
            water += water_level - heights[i]
    
    return water


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
    print(hello())


if __name__ == "__main__":
    main()