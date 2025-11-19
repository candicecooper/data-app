#!/usr/bin/env python3
"""
Password Hash Generator for Behaviour Support App
Use this to generate password hashes for staff members
"""

import hashlib
import secrets

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def main():
    print("=" * 60)
    print("Password Hash Generator")
    print("=" * 60)
    print()
    
    # Generate default password hash
    default_password = "Welcome123!"
    default_hash = hash_password(default_password)
    
    print(f"Default Password: {default_password}")
    print(f"Hash: {default_hash}")
    print()
    print("Copy this hash to use in your SQL UPDATE statement:")
    print(f"  password_hash = '{default_hash}'")
    print()
    print("=" * 60)
    print()
    
    # Interactive mode
    while True:
        print("Generate another password hash? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice != 'y':
            break
        
        print("Enter password: ", end="")
        custom_password = input().strip()
        
        if custom_password:
            custom_hash = hash_password(custom_password)
            print(f"Hash: {custom_hash}")
            print()

if __name__ == "__main__":
    main()
