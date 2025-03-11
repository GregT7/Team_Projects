import os
import zipfile
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time
import shutil

# === CONFIGURATION ===
FOLDER_TO_SEND = "images_to_send"
ZIP_FILENAME = "send_package.zip"

# Initialize RF24
radio = RF24(17, 0)

if not radio.begin():
    print("❌ NRF24 module not responding")
    exit()

radio.setPALevel(RF24_PA_LOW)
radio.setDataRate(rf24_datarate_e.RF24_2MBPS)
radio.setChannel(76)
radio.setPayloadSize(32)
radio.setRetries(5, 15)
radio.setAutoAck(True)

radio.openWritingPipe(0xF0F0F0F0E1)
radio.stopListening()

print("📦 Compressing folder...")

# Compress folder
with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(FOLDER_TO_SEND):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, start=FOLDER_TO_SEND)
            zipf.write(file_path, arcname)
print("✅ Folder compressed into ZIP file.")

# Function to read file in chunks
def read_file_chunks(filename, chunk_size=30):  # Now only 30 bytes for data (2 bytes for header)
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Send START signal
start_signal = "START".ljust(32).encode('utf-8')
radio.write(start_signal)
print("🚀 Sent START signal.")

time.sleep(1)  # Give receiver time to prepare

# Send chunks with sequence numbers
try:
    chunk_number = 0
    for chunk in read_file_chunks(ZIP_FILENAME):
        header = chunk_number.to_bytes(2, 'big')  # 2 bytes for sequence number
        packet = header + chunk
        if len(packet) < 32:
            packet = packet.ljust(32, b'\0')  # Padding to 32 bytes
        if radio.write(packet):
            print(f"✅ Sent chunk #{chunk_number}")
        else:
            print(f"❌ Failed to send chunk #{chunk_number}")
        chunk_number += 1
        time.sleep(0.05)  # Increased delay for reliability

    # Send END signal
    end_signal = "END".ljust(32).encode('utf-8')
    radio.write(end_signal)
    print("🏁 Transmission completed. END signal sent.")

except KeyboardInterrupt:
    print("⏹️ Transmission interrupted by user.")

finally:
    if os.path.exists(ZIP_FILENAME):
        os.remove(ZIP_FILENAME)  # Clean up zip file
        print("🧹 Temporary ZIP file removed.")
