import os
import time
import hashlib
from Cryptodome.Cipher import ChaCha20
from PIL import Image
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW

# === CONFIGURATION ===
RECEIVE_FOLDER = "received_images"
DECRYPTED_FOLDER = "decrypted_images"
PAYLOAD_SIZE = 32  # Must match sender's payload size
EXPECTED_IMAGE_SIZE = (256, 256)
HASH_SIZE = 64  # SHA-256 hash length in hex

# Create necessary folders
os.makedirs(RECEIVE_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

# Define encryption key (must match sender's key)
key = b"0123456789abcdef0123456789abcdef"  # Example key (32 bytes)

# === Initialize RF24 ===
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(PAYLOAD_SIZE)
radio.setAutoAck(True)
radio.setRetries(5, 15)

radio.openReadingPipe(1, 0xF0F0F0F0E1)
radio.startListening()

print("📡 Receiver is listening...")

# === Variables to manage file reception ===
current_filename = None
chunks = {}

def hash_raw_data(data, hash_algorithm="sha256"):
    """Compute SHA-256 hash directly from raw image data."""
    hasher = hashlib.new(hash_algorithm)
    hasher.update(data)
    return hasher.hexdigest()

def decrypt_file(input_filepath, key):
    """Decrypts a file using ChaCha20 and extracts the original hash."""
    with open(input_filepath, "rb") as file:
        nonce = file.read(8)
        encrypted_data = file.read()
    
    cipher = ChaCha20.new(key=key, nonce=nonce)
    decrypted_data = cipher.decrypt(encrypted_data)

    # Extract the original hash and remove any padding
    original_hash = decrypted_data[:HASH_SIZE].decode("utf-8", errors="ignore").rstrip('0')

    # Extract image data
    image_data = decrypted_data[HASH_SIZE:]

    # Compute hash before saving
    final_hash = hash_raw_data(image_data)

    return original_hash, final_hash, image_data

def resize_image(image_path, output_path, target_size):
    """Resize the image to the expected dimensions."""
    with Image.open(image_path) as img:
        img = img.resize(target_size, Image.LANCZOS)
        img.save(output_path, "PNG")

try:
    while True:
        if radio.available():
            received_payload = radio.read(PAYLOAD_SIZE)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            if message.startswith("START:"):
                current_filename = message.split(":", 1)[1].strip()
                chunks = {}
                print(f"📥 Receiving: {current_filename}")

            elif message.startswith("END:"):
                end_filename = message.split(":", 1)[1].strip()
                if current_filename == end_filename:
                    print(f"🔄 Finalizing {current_filename}...")

                    # Ensure we received all chunks
                    ordered_data = b''.join([chunks[i] for i in sorted(chunks.keys())])

                    if len(ordered_data) <= (8 + HASH_SIZE):
                        print(f"❌ Received file is too small. Possible corruption.")
                        continue
                    
                    # Save received encrypted file
                    received_path = os.path.join(RECEIVE_FOLDER, current_filename)
                    with open(received_path, "wb") as f:
                        f.write(ordered_data)

                    # Decrypt the file and verify integrity
                    original_hash, final_hash, decrypted_data = decrypt_file(received_path, key)

                    # Verify integrity BEFORE writing to disk
                    if original_hash == final_hash:
                        print(f"✅ Image integrity verified: {current_filename}")
                    else:
                        print(f"⚠️ WARNING: Hash mismatch for {current_filename}. Possible corruption or tampering.")
                        print(f"Expected Hash: {original_hash}")
                        print(f"Received Hash: {final_hash}")

                    # Save decrypted file if hash matches
                    decrypted_path = os.path.join(DECRYPTED_FOLDER, os.path.splitext(current_filename)[0] + ".png")
                    with open(decrypted_path, "wb") as out_file:
                        out_file.write(decrypted_data)

                    # Resize image after verification
                    resized_path = os.path.join(DECRYPTED_FOLDER, "resized_" + os.path.basename(decrypted_path))
                    resize_image(decrypted_path, resized_path, EXPECTED_IMAGE_SIZE)

                # Reset variables
                current_filename = None
                chunks = {}

            elif current_filename and len(received_payload) >= 2:
                seq_num = int.from_bytes(received_payload[:2], 'big')
                data = received_payload[2:]
                chunks[seq_num] = data

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n🛑 Receiver stopped by user.")

finally:
    radio.stopListening()
    print("📴 Radio stopped listening.")
