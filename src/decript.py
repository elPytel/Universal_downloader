import base64

def datoid_decrypt(data_href: str, title: str) -> str:
    """
    Python implementace dešifrovací funkce d() z Datoid.cz.
    """
    # 1. Base64 dekódování (odpovídá funkci dl v JS)
    try:
        decoded_bytes = base64.b64decode(data_href)
    except Exception:
        return ""

    # 2. Příprava klíče (v JS onclicku je title + salt)
    salt = "$P$$$$$P$$$$"
    key = title + salt
    key_len = len(key)
    
    result = ""
    
    # 3. Samotná dešifrace (substrakce hodnot)
    for i, byte_val in enumerate(decoded_bytes):
        # Indexování klíče: i % key_len - 1
        # V Pythonu index -1 funguje stejně jako v JS substr(-1, 1) -> poslední znak
        key_char = key[(i % key_len) - 1]
        
        # Dešifrovací operace: d = ord(data) - ord(key)
        # Používáme modulo 65536 pro simulaci 16-bit charCode v JS (pokud by výsledek byl záporný)
        decrypted_char_code = (byte_val - ord(key_char)) % 65536
        result += chr(decrypted_char_code)
        
    return result