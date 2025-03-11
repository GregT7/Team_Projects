import os
from RF24 import RF24, rf24_datarate_e, RF24_PA_LOW
import time

# === CONFIGURATION ===
FOLDER_TO_SEND = "images_to_send"

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

print("📂 Ready to send images from folder:", FOLDER_TO_SEND)

# Function to read file in chunks
def read_file_chunks(filename, chunk_size=30):  # 30 bytes data + 2 bytes chunk number
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Send all images
try:
    for file_name in os.listdir(FOLDER_TO_SEND):
        full_path = os.path.join(FOLDER_TO_SEND, file_name)
        if not os.path.isfile(full_path):
            continue  # Skip directories

        print(f"🚀 Sending file: {file_name}")

        # Send START signal with filename
        start_signal = ("START:" + file_name).ljust(32)[:32].encode('utf-8')
        radio.write(start_signal)
        time.sleep(1)  # Let receiver prep for new file

        # Send file chunks with chunk numbers
        chunk_number = 0
        for chunk in read_file_chunks(full_path):
            header = chunk_number.to_bytes(2, 'big')  # 2 bytes for chunk number
            packet = header + chunk
            if len(packet) < 32:
                packet = packet.ljust(32, b'\0')  # Padding to 32 bytes

            if radio.write(packet):
                print(f"✅ Sent chunk #{chunk_number}")
            else:
                print(f"❌ Failed to send chunk #{chunk_number}")
            chunk_number += 1
            time.sleep(0.05)  # Adjust as needed

        # Send END signal with filename
        end_signal = ("END:" + file_name).ljust(32)[:32].encode('utf-8')
        radio.write(end_signal)
        print(f"🏁 Finished sending file: {file_name}")
        time.sleep(1)  # Space between files

except KeyboardInterrupt:
    print("⏹️ Transmission interrupted by user.")
