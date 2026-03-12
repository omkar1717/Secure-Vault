from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_file(file_data):
    return cipher.encrypt(file_data)

def decrypt_file(file_data):
    return cipher.decrypt(file_data)