import os
import time
import hashlib
from Cryptodome.Cipher import ChaCha20
from PIL import Image
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW

# === CONFIGURATION ===
RECEIVE_FOLDER = "received_images"
DECRYPTED_FOLDER = "decrypted_images"
PAYLOAD_SIZE = 32  
EXPECTED_IMAGE_SIZE = (256, 256)  

# Create necessary folders
os.makedirs(RECEIVE_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

# Define encryption key
key = b"0123456789abcdef0123456789abcdef"  

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

received_hash = None
chunks = {}

def hash_data(data):
    """Compute SHA-256 hash of given data."""
    return hashlib.sha256(data).hexdigest()

def decrypt_data(data, key):
    """Decrypts data using ChaCha20."""
    nonce, encrypted_data = data[:8], data[8:]
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return cipher.decrypt(encrypted_data)

def resize_image(image_path, output_path, target_size):
    """Resize the image."""
    with Image.open(image_path) as img:
        img = img.resize(target_size, Image.LANCZOS)
        img.save(output_path, "PNG")

try:
    while True:
        if radio.available():
            received_payload = radio.read(PAYLOAD_SIZE)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            if message.startswith("START:"):
                received_hash = message.split(":", 1)[1].strip()
                chunks = {}
                print(f"📥 Receiving file with expected hash: {received_hash}")

            elif message.startswith("END:"):
                final_hash = hash_data(b''.join(chunks[i] for i in sorted(chunks)))
                if final_hash == received_hash:
                    print(f"✅ Hash match confirmed: {received_hash}")

                    received_path = os.path.join(RECEIVE_FOLDER, "received.enc")
                    with open(received_path, "wb") as f:
                        f.write(b''.join(chunks[i] for i in sorted(chunks)))

                    decrypted_data = decrypt_data(b''.join(chunks[i] for i in sorted(chunks)), key)
                    decrypted_path = os.path.join(DECRYPTED_FOLDER, "decrypted.png")
                    with open(decrypted_path, "wb") as f:
                        f.write(decrypted_data)

                    resized_path = os.path.join(DECRYPTED_FOLDER, "resized.png")
                    resize_image(decrypted_path, resized_path, EXPECTED_IMAGE_SIZE)
                else:
                    print(f"❌ Hash mismatch! Expected {received_hash}, got {final_hash}")
                
                received_hash = None
                chunks = {}

            else:
                seq_num = int.from_bytes(received_payload[:2], 'big')
                data = received_payload[2:]
                chunks[seq_num] = data

        time.sleep(0.01)

except KeyboardInterrupt:
    radio.stopListening()
    print("\n🛑 Receiver stopped.")
