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

# Setup folders
os.makedirs(RECEIVE_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)
os.makedirs(FINAL_FOLDER, exist_ok=True)

# Encryption key
key = b"0123456789abcdef0123456789abcdef"

# Initialize RF24
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

def decrypt_file(in_path, out_path, key):
    with open(in_path, "rb") as f:
        data = f.read()
    nonce = data[:8]
    cipher = ChaCha20.new(key=key, nonce=nonce)
    decrypted = cipher.decrypt(data[8:])
    with open(out_path, "wb") as f:
        f.write(decrypted)
    print(f"✅ Decrypted: {in_path}")

def resize_image(in_path, out_path, size):
    with Image.open(in_path) as img:
        img = img.resize(size, Image.LANCZOS)
        img.save(out_path, format="PNG", compress_level=0)
    print(f"📏 Resized: {out_path}")

try:
    while True:
        if radio.available():
            payload = radio.read(PAYLOAD_SIZE)
            message = payload.decode('utf-8', errors='ignore').strip()

            if message.startswith("START:"):
                current_filename = message.split(":", 1)[1].strip()
                chunks = {}
                received_hash = None
                print(f"📥 Receiving: {current_filename}")

            elif message.startswith("HASH:") and current_filename:
                part1 = payload[5:]
                while not radio.available():
                    time.sleep(0.01)
                part2 = radio.read(PAYLOAD_SIZE)
                received_hash = part1 + part2[:5]
                print(f"🔒 Received hash: {received_hash.hex()}")

            elif message.startswith("END:") and current_filename:
                end_filename = message.split(":", 1)[1].strip()
                if end_filename == current_filename:
                    print(f"🔄 Finalizing: {current_filename}")
                    chunk_list = [chunks[i] for i in sorted(chunks)]
                    chunk_list[-1] = chunk_list[-1].rstrip(b'\0')  # Strip last-chunk padding
                    ordered = b''.join(chunk_list)

                    with open("debug_raw_received.enc", "wb") as f:
                        f.write(ordered)
                    print("💾 Saved raw file for debugging.")

                    calc_hash = compute_sha256(ordered)
                    print(f"🔍 Calculated hash: {calc_hash.hex()}")

                    if received_hash != calc_hash:
                        print("❌ Hash mismatch! File corrupted.")
                        current_filename = None
                        continue
                    print("✅ Hash verified.")

                    recv_path = os.path.join(RECEIVE_FOLDER, current_filename)
                    with open(recv_path, "wb") as f:
                        f.write(ordered)

                    decrypt_path = os.path.join(DECRYPTED_FOLDER, os.path.splitext(current_filename)[0] + ".png")
                    decrypt_file(recv_path, decrypt_path, key)

                    final_path = os.path.join(FINAL_FOLDER, "final_" + os.path.basename(decrypt_path))
                    resize_image(decrypt_path, final_path, TARGET_SIZE)

                current_filename = None
                chunks = {}
                received_hash = None

            elif current_filename and len(payload) >= 2:
                seq = int.from_bytes(payload[:2], 'big')
                chunk = payload[2:]
                chunks[seq] = chunk
                print(f"📦 Chunk {seq} received")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("🛑 Receiver stopped.")
