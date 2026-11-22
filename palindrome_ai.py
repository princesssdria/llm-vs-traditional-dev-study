import string

def is_palindrome(text: str) -> bool:
    """
    Checks if a given string is a palindrome.
    Ignores spaces, punctuation, and case sensitivity.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
        
    # Remove punctuation and whitespace, then convert to lowercase
    cleaned_text = "".join(
        char.lower() for char in text if char not in string.punctuation and not char.isspace()
    )
    
    # Check if the cleaned string equals its reverse
    return cleaned_text == cleaned_text[::-1]

def main():
    print("--- Palindrome Checker ---")
    user_input = input("Enter a word, phrase, or sentence: ")
    
    if is_palindrome(user_input):
        print(f"'{user_input}' is a palindrome! 🎉")
    else:
        print(f"'{user_input}' is not a palindrome.")

if __name__ == "__main__":
    main()