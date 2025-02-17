def caesar_cipher(text, shift):
    """Encrypt or decrypt text using a Caesar cipher with a given shift."""
    result = ""
    for char in text:
        if char.isalpha():
            shift_amount = shift % 26
            new_char = chr(((ord(char.lower()) - 97 + shift_amount) % 26) + 97)
            if char.isupper():
                new_char = new_char.upper()
            result += new_char
        else:
            result += char
    return result