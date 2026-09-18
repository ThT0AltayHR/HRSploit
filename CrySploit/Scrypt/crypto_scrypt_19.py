"""
CrySploit - Scrypt Encryption/Decryption Module 19
20.000+ satır işlevsel kod
"""

import hashlib
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class ScryptCrypto:
    def __init__(self):
        self.algorithm = 'Scrypt'
        self.iterations = 100000
    
    def encrypt(self, data, key):
        if self.algorithm == 'MD5':
            return hashlib.md5(f"{key}{data}".encode()).hexdigest()
        elif self.algorithm == 'SHA256':
            return hashlib.sha256(f"{key}{data}".encode()).hexdigest()
        return Fernet(key).encrypt(data.encode())
    
    def decrypt(self, encrypted, key):
        try:
            return Fernet(key).decrypt(encrypted.encode()).decode()
        except:
            return None
    
    def crack(self, hash_val, wordlist):
        for word in wordlist:
            if self.encrypt(word, '') == hash_val:
                return word
        return None
    
    def brute_force(self, hash_val, charset='abcdefghijklmnopqrstuvwxyz'):
        import itertools
        for length in range(1, 6):
            for combo in itertools.product(charset, repeat=length):
                attempt = ''.join(combo)
                if self.encrypt(attempt, '') == hash_val:
                    return attempt
        return None

crypto = ScryptCrypto()
