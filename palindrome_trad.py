def is_palindrome():
    user_input = input("Enter a string to check if it's a palindrome: ")

    normalized_str = ''.join(user_input.split()).lower()

    if normalized_str == normalized_str[::-1]:
        return "The string is a palindrome."
    else:
        return "The string is not a palindrome."

    result = is_palindrome()
    print(result)
