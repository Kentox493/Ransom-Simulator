import math
import random
from typing import Tuple, Union
import os

class RSACrypto:
    def __init__(self):
        # Generate key pairs during initialization with 4096 bit key
        self.public_key, self.private_key = self.generate_keypair(4096)
    
    def is_prime(self, n: int, k: int = 128) -> bool:
        """Miller-Rabin primality test"""
        if n == 2 or n == 3:
            return True
        if n < 2 or n % 2 == 0:
            return False
        
        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Witness loop
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def generate_prime(self, bits: int) -> int:
        """Generate a prime number with specified bits"""
        while True:
            # Generate random number with specified bits
            num = random.getrandbits(bits)
            # Make sure it's odd
            num |= 1
            # Make sure it has exactly the specified bits
            num |= (1 << bits - 1)
            if self.is_prime(num):
                return num
    
    def extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean Algorithm"""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    def mod_inverse(self, e: int, phi: int) -> int:
        """Calculate modular multiplicative inverse"""
        _, d, _ = self.extended_gcd(e, phi)
        return d % phi
    
    def generate_keypair(self, bits: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Generate public and private key pairs"""
        # Generate two prime numbers with bit size of half the total key size
        p = self.generate_prime(bits // 2)
        q = self.generate_prime(bits // 2)
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Choose public exponent
        e = 65537  # Common choice for e
        
        # Calculate private exponent
        d = self.mod_inverse(e, phi)
        
        return ((e, n), (d, n))
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt bytes using RSA"""
        e, n = self.public_key
        # Convert bytes to integer
        m = int.from_bytes(data, 'big')
        # Encrypt
        c = pow(m, e, n)
        # Convert back to bytes
        return c.to_bytes((c.bit_length() + 7) // 8, 'big')
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypt bytes using RSA"""
        d, n = self.private_key
        # Convert bytes to integer
        c = int.from_bytes(encrypted_data, 'big')
        # Decrypt
        m = pow(c, d, n)
        # Convert back to bytes
        return m.to_bytes((m.bit_length() + 7) // 8, 'big')
    
    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """Encrypt a file"""
        # Read file in binary mode
        with open(input_path, 'rb') as f:
            data = f.read()
        
        # Encrypt data
        encrypted_data = self.encrypt_bytes(data)
        
        # Write encrypted data
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """Decrypt a file"""
        # Read encrypted file
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt data
        decrypted_data = self.decrypt_bytes(encrypted_data)
        
        # Write decrypted data
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

    def encrypt_directory(self, directory_path: str) -> None:
        """Encrypt all files in a directory"""
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                encrypted_path = file_path + '.encrypted'
                self.encrypt_file(file_path, encrypted_path)
                os.remove(file_path)  # Remove original file

    def decrypt_directory(self, directory_path: str) -> None:
        """Decrypt all encrypted files in a directory"""
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.encrypted'):
                    file_path = os.path.join(root, file)
                    decrypted_path = file_path[:-10]  # Remove .encrypted extension
                    self.decrypt_file(file_path, decrypted_path)
                    os.remove(file_path)  # Remove encrypted file
