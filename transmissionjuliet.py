# import os
# import time
# import hashlib
# from Crypto.Cipher import ChaCha20
# from PIL import Image
# import io
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW

# # === CONFIGURATION ===
# FOLDER_TO_SEND = "images"
# ENCRYPTED_FOLDER = "encrypted"
# PAYLOAD_SIZE = 32  # Max packet size
# MAX_RETRIES = 300  # Max retries per packet
# INTER_PACKET_DELAY = 0.0001  # Delay between packets
# CONTROL_SIGNAL_DELAY = 0.01  # Delay for START/END signals
# FILENAME_MAX_LEN = 32 - len("START:")  # Max filename length
# TARGET_IMAGE_SIZE = (128, 128)  # Reduce to 128x128 for faster transmission

# # Ensure necessary folders exist
# os.makedirs(FOLDER_TO_SEND, exist_ok=True)
# os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

# # Define encryption key
# key = b"0123456789abcdef0123456789abcdef"  # Example key (32 bytes)

# # === Initialize NRF24 ===
# def initialize_transmitter():
#     radio = RF24(17, 0)
#     if not radio.begin():
#         print("❌ NRF24 module not responding")
#         exit()
#     radio.setPALevel(RF24_PA_LOW)
#     radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
#     radio.setChannel(76)
#     radio.setPayloadSize(PAYLOAD_SIZE)
#     radio.setRetries(5, 15)
#     radio.setAutoAck(True)
#     radio.openWritingPipe(0xF0F0F0F0E1)
#     radio.stopListening()
#     return radio

# def compress_image(input_filepath):
#     """Compresses the image while keeping it in PNG format."""
#     with Image.open(input_filepath) as img:
#         img = img.convert("RGBA")
#         img = img.resize(TARGET_IMAGE_SIZE, Image.LANCZOS)
        
#         compressed_image_io = io.BytesIO()
#         img.save(compressed_image_io, format="PNG", optimize=True, compression_level=9)
#         compressed_image_io.seek(0)
#         return compressed_image_io.read()

# def encrypt_file(input_data, key):
#     """Encrypts the data using ChaCha20."""
#     nonce = os.urandom(8)
#     cipher = ChaCha20.new(key=key, nonce=nonce)
    
#     encrypted_data = cipher.encrypt(input_data)
    
#     return nonce + encrypted_data  

# def read_file_chunks(data, chunk_size=PAYLOAD_SIZE - 2):
#     """Generator to read data in chunks."""
#     for i in range(0, len(data), chunk_size):
#         yield data[i:i + chunk_size]

# def send_with_retry(radio, packet, description):
#     retry_count = 0
#     while retry_count < MAX_RETRIES:
#         if radio.write(packet):
#             print(f"✅ {description}")
#             return True
#         retry_count += 1
#         print(f"⚠️ Retry {retry_count}/{MAX_RETRIES} for {description}")
#         time.sleep(0.1)
#     print(f"❌ Failed to send {description} after {MAX_RETRIES} retries")
#     return False

# def send_encrypted_images(radio):
#     image_files = os.listdir(FOLDER_TO_SEND)
#     if not image_files:
#         print("No images found.")
#         exit()

#     for image in image_files:
#         full_path = os.path.join(FOLDER_TO_SEND, image)
#         if not os.path.isfile(full_path):
#             continue  
        
#         compressed_image_data = compress_image(full_path)
        
#         encrypted_data = encrypt_file(compressed_image_data, key)
        
#         encrypted_path = os.path.join(ENCRYPTED_FOLDER, os.path.splitext(image)[0] + ".enc")
        
#         with open(encrypted_path, "wb") as debug_file:
#             debug_file.write(encrypted_data)
#         print(f"🛠 [DEBUG] Saved encrypted file for verification: {encrypted_path}")

#         safe_name = ("START:" + os.path.splitext(image)[0] + ".enc").ljust(32).encode('utf-8')
#         if not send_with_retry(radio, safe_name, f"START signal for {image}"):
#             continue
#         time.sleep(CONTROL_SIGNAL_DELAY)
        
#         chunk_number = 0
#         for chunk in read_file_chunks(encrypted_data):
#             header = chunk_number.to_bytes(2, 'big')
#             packet = header + chunk.ljust(PAYLOAD_SIZE, b'\0')
#             if not send_with_retry(packet, f"Chunk #{chunk_number} of {image}.enc"):
#                 print(f"⛔ Aborting {image}")
#                 break
#             chunk_number += 1
#             time.sleep(INTER_PACKET_DELAY)
        
#         end_signal = ("END:" + os.path.splitext(image)[0] + ".enc").ljust(32).encode('utf-8')
#         if send_with_retry(end_signal, f"END signal for {image}.enc"):
#             print(f"🏁 Finished sending {image}.enc")
#         else:
#             print(f"⚠️ {image}.enc may not have been received correctly.")
#         time.sleep(CONTROL_SIGNAL_DELAY)

#     print("✅ All images resized, compressed, encrypted, and transmitted!")
