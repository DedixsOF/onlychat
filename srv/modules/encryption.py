import hashlib
import os

class Encryption:
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        return hashlib.sha512((password + salt).encode()).hexdigest()

    @staticmethod
    def generate_salt() -> str:
        return os.urandom(16).hex()

    @staticmethod
    def verify_password(stored_password: str, provided_password: str, salt: str) -> bool:
        return stored_password == Encryption.hash_password(provided_password, salt)
