import os
import glob
import hashlib
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

def hash_file(filename, hash_algorithm="sha256", buffer_size=65536):
    """
    Compute the hash of a file using the specified hash algorithm.
    
    :param filename: Path to the file to be hashed.
    :param hash_algorithm: Name of the hash algorithm (default is 'sha256').
    :param buffer_size: Number of bytes to read per chunk.
    :return: Hexadecimal digest of the computed hash.
    """
    hasher = getattr(hashlib, hash_algorithm)()
    with open(filename, "rb") as file:
        while chunk := file.read(buffer_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def encrypt_file(input_filepath, output_filepath, key):
    """
    Encrypt a file using the ChaCha20 algorithm.
    
    :param input_filepath: The file to encrypt.
    :param output_filepath: Where to save the encrypted file.
    :param key: The encryption key (must be 32 bytes long).
    """
    # Generate an 8-byte nonce for ChaCha20
    nonce = get_random_bytes(8)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    
    # Read the entire file (for large files consider processing in chunks)
    with open(input_filepath, "rb") as file:
        plaintext = file.read()
    
    # Encrypt the file data
    ciphertext = cipher.encrypt(plaintext)
    
    # Write the nonce and ciphertext to the output file.
    # The nonce is needed later for decryption.
    with open(output_filepath, "wb") as out_file:
        out_file.write(nonce)
        out_file.write(ciphertext)
    
    print(f"Encrypted {input_filepath} -> {output_filepath}")

def main():
    # Define the directory containing your images and the destination for encrypted files.
    image_directory = os.path.join("images")  # e.g., D:\Scripts\Hashing\images
    encrypted_directory = "encrypted"         # Encrypted files will be saved here

    # Create the encrypted directory if it doesn't exist.
    if not os.path.exists(encrypted_directory):
        os.makedirs(encrypted_directory)

    # Use glob to find image files (adjust patterns for your file types if needed)
    image_files = glob.glob(os.path.join(image_directory, "*.jpeg"))
    image_files += glob.glob(os.path.join(image_directory, "*.jpg"))
    image_files = list(set(image_files))  # Remove duplicates if any

    if not image_files:
        print("No image files found in:", os.path.abspath(image_directory))
        return
    else:
        print(f"Found {len(image_files)} image(s) in '{os.path.abspath(image_directory)}'.\n")

    # Define a 32-byte key for ChaCha20 encryption.
    # **Security Note:** In production, manage and store your keys securely!
    key = b"0123456789abcdef0123456789abcdef"  # Example key (32 bytes)
    if len(key) != 32:
        raise ValueError("The encryption key must be 32 bytes long for ChaCha20.")

    # Process each image: hash it and then encrypt it.
    for image in image_files:
        # Compute and display the hash for verification
        file_hash = hash_file(image)
        print(f"SHA-256 hash of {image}: {file_hash}")

        # Prepare the name for the encrypted file (using a .enc extension)
        base_name = os.path.basename(image)
        encrypted_filename = os.path.splitext(base_name)[0] + ".enc"
        output_filepath = os.path.join(encrypted_directory, encrypted_filename)

        # Encrypt the image file using ChaCha20
        encrypt_file(image, output_filepath, key)

    # Final verification message
    print("\nVerification: All images have been hashed and encrypted.")
    print("Encrypted files are stored in:", os.path.abspath(encrypted_directory))
    print("They are ready for transmission via the radio transceiver.")

if __name__ == "__main__":
    main()
