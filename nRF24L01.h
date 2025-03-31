
import os
import time
import hashlib
from Cryptodome.Cipher import ChaCha20
from PIL import Image
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW

# === CONFIGURATION ===
RECEIVE_FOLDER = "received_images"
DECRYPTED_FOLDER = "decrypted_images"
FINAL_FOLDER = "final_images"
PAYLOAD_SIZE = 32
TARGET_SIZE = (1024, 1024)

os.makedirs(RECEIVE_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)
os.makedirs(FINAL_FOLDER, exist_ok=True)

key = b"0123456789abcdef0123456789abcdef"

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

current_filename = None
chunks = {}
received_hash = None

def compute_sha256(data):
    return hashlib.sha256(data).digest()

def decrypt_file(input_filepath, output_filepath, key):
    with open(input_filepath, "rb") as file:
        file_data = file.read()
    if len(file_data) < 8:
        print(f"❌ ERROR: Received file {input_filepath} is too small! Possible corruption.")
        return
    nonce = file_data[:8]
    encrypted_data = file_data[8:]
    cipher = ChaCha20.new(key=key, nonce=nonce)
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(output_filepath, "wb") as out_file:
        out_file.write(decrypted_data)
    print(f"✅ Successfully decrypted {input_filepath} -> {output_filepath}")

def resize_image(image_path, output_path, target_size):
    with Image.open(image_path) as img:
        img = img.resize(target_size, Image.LANCZOS)
        img.save(output_path, "PNG", compress_level=0)
    print(f"📏 Resized and saved uncompressed: {output_path}")

try:
    while True:
        if radio.available():
            received_payload = radio.read(PAYLOAD_SIZE)
            message = received_payload.decode('utf-8', errors='ignore').strip()

            if message.startswith("START:"):
                current_filename = message.split(":", 1)[1].strip()
                chunks = {}
                received_hash = None
                print(f"📥 Receiving: {current_filename}")

            elif message.startswith("HASH:") and current_filename:
                hash_part1 = received_payload[5:]
                while not radio.available():
                    time.sleep(0.01)
                hash_part2 = radio.read(PAYLOAD_SIZE)
                received_hash = hash_part1 + hash_part2.strip(b'\0')
                print(f"🔒 Received hash for {current_filename}")

            elif message.startswith("END:"):
                end_filename = message.split(":", 1)[1].strip()
                if current_filename == end_filename:
                    print(f"🔄 Finalizing {current_filename}...")
                    ordered_data = b''.join([chunks[i] for i in sorted(chunks.keys())])
                    if len(ordered_data) < 8:
                        print(f"❌ ERROR: Received file is too small! Possible corruption.")
                        continue

                    # Verify hash
                    calculated_hash = compute_sha256(ordered_data)
                    if not received_hash or calculated_hash != received_hash:
                        print(f"❌ Hash mismatch! File {current_filename} corrupted.")
                        continue
                    print(f"✅ Hash verified for {current_filename}")

                    received_path = os.path.join(RECEIVE_FOLDER, current_filename)
                    with open(received_path, "wb") as f:
                        f.write(ordered_data)

                    decrypted_path = os.path.join(DECRYPTED_FOLDER, os.path.splitext(current_filename)[0] + ".png")
                    decrypt_file(received_path, decrypted_path, key)

                    final_path = os.path.join(FINAL_FOLDER, "final_" + os.path.basename(decrypted_path))
                    resize_image(decrypted_path, final_path, TARGET_SIZE)

                current_filename = None
                chunks = {}
                received_hash = None

            elif current_filename and len(received_payload) >= 2:
                seq_num = int.from_bytes(received_payload[:2], 'big')
                data = received_payload[2:]
                chunks[seq_num] = data
                print(f"🛠 [DEBUG] Received chunk #{seq_num}, size: {len(data)} bytes")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n🛑 Receiver stopped by user.")

