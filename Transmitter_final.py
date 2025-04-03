import os
import time
import hashlib
from Cryptodome.Cipher import ChaCha20
from PIL import Image
import io
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW

# === CONFIGURATION ===
FOLDER_TO_SEND = "images"
ENCRYPTED_FOLDER = "encrypted"
PAYLOAD_SIZE = 32
MAX_RETRIES = 300
INTER_PACKET_DELAY = 0.0001
CONTROL_SIGNAL_DELAY = 0.001
TARGET_IMAGE_SIZE = (250, 250)

# Setup folders
os.makedirs(FOLDER_TO_SEND, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

# Encryption key (32 bytes)
key = b"0123456789abcdef0123456789abcdef"

# Initialize NRF24
radio = RF24(17, 0)
if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()
radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(PAYLOAD_SIZE)
radio.setRetries(5, 15)
radio.setAutoAck(True)
radio.openWritingPipe(0xF0F0F0F0E1)
radio.stopListening()

def compress_image(filepath):
    with Image.open(filepath) as img:
        img = img.convert("RGBA")
        img = img.resize(TARGET_IMAGE_SIZE, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True, compression_level=9)
        return buf.getvalue()

def encrypt_file(data, key):
    nonce = os.urandom(8)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return nonce + cipher.encrypt(data)

def compute_sha256(data):
    return hashlib.sha256(data).digest()

def read_chunks(data):
    chunk_size = PAYLOAD_SIZE - 2
    for i in range(0, len(data), chunk_size):
        yield data[i:i+chunk_size]

def send_with_retry(packet, desc):
    for attempt in range(MAX_RETRIES):
        if radio.write(packet):
            print(f"✅ Sent: {desc}")
            return True
        print(f"⏳ Retry {attempt+1}/{MAX_RETRIES} for {desc}")
        time.sleep(0.1)
    print(f"❌ Failed to send: {desc}")
    return False

# Begin transmission
image_files = os.listdir(FOLDER_TO_SEND)
if not image_files:
    print("📂 No images found.")
    exit()

for image in image_files:
    path = os.path.join(FOLDER_TO_SEND, image)
    if not os.path.isfile(path):
        continue

    compressed = compress_image(path)
    encrypted = encrypt_file(compressed, key)
    file_hash = compute_sha256(encrypted)
    print(f"🔐 Hash for {image}: {file_hash.hex()}")

    with open(os.path.join(ENCRYPTED_FOLDER, os.path.splitext(image)[0] + ".enc"), "wb") as f:
        f.write(encrypted)

    start_packet = ("START:" + os.path.splitext(image)[0] + ".enc").ljust(32).encode()
    if not send_with_retry(start_packet, "START"):
        continue
    time.sleep(CONTROL_SIGNAL_DELAY)

    for i, chunk in enumerate(read_chunks(encrypted)):
        header = i.to_bytes(2, 'big')
        payload = header + chunk.ljust(PAYLOAD_SIZE - 2, b'\0')
        send_with_retry(payload, f"Chunk {i}")
        time.sleep(INTER_PACKET_DELAY)

    hash_packet_1 = b"HASH:" + file_hash[:27]
    hash_packet_2 = file_hash[27:].ljust(PAYLOAD_SIZE, b'\0')
    send_with_retry(hash_packet_1.ljust(PAYLOAD_SIZE, b'\0'), "HASH part 1")
    time.sleep(CONTROL_SIGNAL_DELAY)
    send_with_retry(hash_packet_2, "HASH part 2")
    time.sleep(CONTROL_SIGNAL_DELAY)

    end_packet = ("END:" + os.path.splitext(image)[0] + ".enc").ljust(32).encode()
    send_with_retry(end_packet, "END")
    time.sleep(CONTROL_SIGNAL_DELAY)

print("✅ All images transmitted with encryption and hash.")
