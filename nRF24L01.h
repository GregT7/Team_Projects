import os
import time
from Cryptodome.Cipher import ChaCha20
from PIL import Image
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW

# === CONFIGURATION ===
RECEIVE_FOLDER = "received_images"
DECRYPTED_FOLDER = "decrypted_images"
PAYLOAD_SIZE = 32  # Must match sender's payload size
EXPECTED_IMAGE_SIZE = (256, 256)

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

def decrypt_file(input_filepath, output_filepath, key):
    """Decrypts a file using ChaCha20."""
    with open(input_filepath, "rb") as file:
        nonce = file.read(8)
        encrypted_data = file.read()
    
    cipher = ChaCha20.new(key=key, nonce=nonce)
    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_filepath, "wb") as out_file:
        out_file.write(decrypted_data)

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
                    ordered_data = b''.join([chunks[i] for i in sorted(chunks.keys())])
                    
                    received_path = os.path.join(RECEIVE_FOLDER, current_filename)
                    with open(received_path, "wb") as f:
                        f.write(ordered_data)

                    decrypted_path = os.path.join(DECRYPTED_FOLDER, os.path.splitext(current_filename)[0] + ".png")
                    decrypt_file(received_path, decrypted_path, key)

                    resized_path = os.path.join(DECRYPTED_FOLDER, "resized_" + os.path.basename(decrypted_path))
                    resize_image(decrypted_path, resized_path, EXPECTED_IMAGE_SIZE)

                current_filename = None
                chunks = {}

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n🛑 Receiver stopped by user.")
