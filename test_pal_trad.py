from palindrome_trad import is_palindrome
def test_palindrome_true(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "A man a plan a canal Panama")
    result = is_palindrome()
    assert result == "The string is a palindrome."

def test_palindrome_false(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "Hello World")
    result = is_palindrome()
    assert result == "The string is not a palindrome."
