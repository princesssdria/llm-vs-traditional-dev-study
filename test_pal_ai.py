import unittest
from palindrome_ai import is_palindrome  # <-- Updated from 'palindrome' to 'palindrome_ai'

class TestPalindrome(unittest.TestCase):
    
    def test_simple_palindromes(self):
        self.assertTrue(is_palindrome("racecar"))
        self.assertTrue(is_palindrome("madam"))
        self.assertTrue(is_palindrome("noon"))

    def test_case_insensitivity(self):
        self.assertTrue(is_palindrome("RaceCar"))
        self.assertTrue(is_palindrome("Level"))

    def test_phrases_with_punctuation_and_spaces(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama!"))
        self.assertTrue(is_palindrome("Was it a car or a cat I saw?"))
        self.assertTrue(is_palindrome("No 'x' in Nixon"))

    def test_non_palindromes(self):
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("python"))
        self.assertFalse(is_palindrome("palindrome"))

    def test_edge_cases(self):
        self.assertTrue(is_palindrome(""))        # Empty string
        self.assertTrue(is_palindrome("a"))       # Single character
        self.assertTrue(is_palindrome("   "))     # Only spaces
        self.assertTrue(is_palindrome("12321"))   # Numeric palindrome

    def test_invalid_input_type(self):
        with self.assertRaises(TypeError):
            is_palindrome(12321)  # Passing an integer instead of a string

if __name__ == "__main__":
    unittest.main()