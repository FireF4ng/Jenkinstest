import itertools

DEFAULT_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_vigenere_key(text, key):
    """Génère une clé répétée pour qu'elle ait la même longueur que le texte."""
    filtered_text = ''.join(c for c in text if c in DEFAULT_ALPHABET)
    repeated_key = ''.join(itertools.islice(itertools.cycle(key), len(filtered_text)))
    return repeated_key

def vigenere_encrypt(text, key, alphabet=DEFAULT_ALPHABET):
    """Chiffre un texte avec Vigenère."""
    key = generate_vigenere_key(text, key)
    encrypted_text = []
    key_index = 0

    for char in text:
        if char in alphabet:
            new_index = (alphabet.index(char) + alphabet.index(key[key_index])) % len(alphabet)
            encrypted_text.append(alphabet[new_index])
            key_index += 1
        else:
            encrypted_text.append(char)

    return ''.join(encrypted_text)

def vigenere_decrypt(text, key, alphabet=DEFAULT_ALPHABET):
    """Déchiffre un texte chiffré avec Vigenère."""
    key = generate_vigenere_key(text, key)
    decrypted_text = []
    key_index = 0

    for char in text:
        if char in alphabet:
            new_index = (alphabet.index(char) - alphabet.index(key[key_index])) % len(alphabet)
            decrypted_text.append(alphabet[new_index])
            key_index += 1
        else:
            decrypted_text.append(char)

    return ''.join(decrypted_text)
